"""Durable host-owned response release gate."""

from __future__ import annotations

import hashlib
import json
import os
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from agent.finalization_policy import (
    DEFAULT_BLOCK_MESSAGE,
    FinalizationAction,
    FinalizationContext,
    FinalizationDecision,
    RegisteredFinalizationPolicy,
    evaluate_finalization_policies,
)


AUDIT_FAILURE_MESSAGE = "Final delivery blocked: the required policy decision could not be audited."
_AUDIT_LOCK = threading.RLock()


@dataclass(frozen=True)
class FinalizationGateResult:
    applied: bool
    allowed: bool
    response_text: str
    reason_code: str
    response_sha256: str
    candidate_response_sha256: str
    audit_id: str | None
    decisions: tuple[FinalizationDecision, ...]


def _audit_id(context: FinalizationContext) -> str:
    key = "\0".join(
        (
            context.session_id,
            context.turn_id or "",
            context.response_sha256,
        )
    )
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def _record_for(
    context: FinalizationContext,
    *,
    audit_id: str,
    action: FinalizationAction,
    reason_code: str,
    release_sha256: str,
    decisions: tuple[FinalizationDecision, ...],
) -> dict:
    return {
        "schema_version": 1,
        "audit_id": audit_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "session_id": context.session_id,
        "task_id": context.task_id,
        "turn_id": context.turn_id,
        "platform": context.platform,
        "model": context.model,
        "project_root_sha256": hashlib.sha256(
            context.project_root.encode("utf-8")
        ).hexdigest(),
        "candidate_response_sha256": context.response_sha256,
        "response_sha256": release_sha256,
        "decision": action.value,
        "reason_code": reason_code,
        "policy_ids": [decision.policy_id for decision in decisions],
        "policies": [
            {
                "policy_id": decision.policy_id,
                "action": decision.action.value,
                "reason_code": decision.reason_code,
                "evidence": decision.evidence,
            }
            for decision in decisions
        ],
    }


def _lock_file(handle) -> None:
    if os.name == "nt":  # pragma: no cover - exercised on Windows CI
        import msvcrt

        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
    else:
        import fcntl

        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)


def _unlock_file(handle) -> None:
    if os.name == "nt":  # pragma: no cover - exercised on Windows CI
        import msvcrt

        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        import fcntl

        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _persist_audit(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    encoded = json.dumps(
        record,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    with _AUDIT_LOCK:
        with path.open("a+", encoding="utf-8") as handle:
            _lock_file(handle)
            try:
                handle.seek(0)
                for line in handle:
                    try:
                        existing = json.loads(line)
                    except json.JSONDecodeError as exc:
                        raise RuntimeError(
                            "malformed finalization audit log"
                        ) from exc
                    if existing.get("audit_id") == record["audit_id"]:
                        if existing != record:
                            # created_at is expected to differ on a replay; all
                            # security-relevant fields must remain identical.
                            left = dict(existing)
                            right = dict(record)
                            left.pop("created_at", None)
                            right.pop("created_at", None)
                            if left != right:
                                raise RuntimeError("conflicting finalization audit record")
                        return
                handle.seek(0, os.SEEK_END)
                handle.write(encoded + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            finally:
                _unlock_file(handle)


def apply_finalization_gate(
    context: FinalizationContext,
    policies: Iterable[RegisteredFinalizationPolicy],
    *,
    audit_path: str | Path,
    max_evidence_bytes: int = 65_536,
) -> FinalizationGateResult:
    """Return only policy-approved content after durably recording the decision."""

    policy_snapshot = tuple(policies)
    if not policy_snapshot:
        return FinalizationGateResult(
            applied=False,
            allowed=True,
            response_text=context.response_text,
            reason_code="no_required_finalization_policies",
            response_sha256=context.response_sha256,
            candidate_response_sha256=context.response_sha256,
            audit_id=None,
            decisions=(),
        )

    evaluation = evaluate_finalization_policies(
        context,
        policy_snapshot,
        max_evidence_bytes=max_evidence_bytes,
    )
    allowed = evaluation.action is FinalizationAction.ALLOW
    release_text = context.response_text if allowed else DEFAULT_BLOCK_MESSAGE
    release_sha256 = hashlib.sha256(release_text.encode("utf-8")).hexdigest()
    audit_id = _audit_id(context)
    record = _record_for(
        context,
        audit_id=audit_id,
        action=evaluation.action,
        reason_code=evaluation.reason_code,
        release_sha256=release_sha256,
        decisions=evaluation.decisions,
    )
    try:
        _persist_audit(Path(audit_path), record)
    except Exception:
        return FinalizationGateResult(
            applied=True,
            allowed=False,
            response_text=AUDIT_FAILURE_MESSAGE,
            reason_code="finalization_audit_failed",
            response_sha256=hashlib.sha256(
                AUDIT_FAILURE_MESSAGE.encode("utf-8")
            ).hexdigest(),
            candidate_response_sha256=context.response_sha256,
            audit_id=None,
            decisions=evaluation.decisions,
        )

    return FinalizationGateResult(
        applied=True,
        allowed=allowed,
        response_text=release_text,
        reason_code=evaluation.reason_code,
        response_sha256=release_sha256,
        candidate_response_sha256=context.response_sha256,
        audit_id=audit_id,
        decisions=evaluation.decisions,
    )
