"""Typed, fail-closed finalization policy evaluation.

Required policies are deliberately separate from best-effort lifecycle hooks:
errors, timeouts, malformed results, and oversized evidence deny release of the
candidate response.  This module has no plugin or delivery dependencies so the
same evaluator can guard every Hermes surface.
"""

from __future__ import annotations

import hashlib
import json
import queue
import re
import threading
from contextvars import copy_context
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from pathlib import Path
from typing import Any, Callable, Iterable


DEFAULT_BLOCK_MESSAGE = "Final delivery blocked: a required finalization policy did not pass."


class ProjectPolicyRequirementError(ValueError):
    """The host could not safely interpret a project enforcement contract."""


def project_required_policy_ids(project_root: str | Path) -> tuple[str, ...]:
    """Read the strict host-owned project requirement, if present.

    A present-but-invalid contract is never treated as if enforcement were
    absent. Callers must block or refuse startup on this exception.
    """

    root = Path(project_root).expanduser().resolve(strict=True)
    path = root / ".hermes" / "enforcement.json"
    if not path.exists() and not path.is_symlink():
        return ()
    if path.is_symlink():
        raise ProjectPolicyRequirementError("enforcement config may not be a symlink")
    try:
        stat = path.stat()
        if not path.is_file() or stat.st_size > 65_536:
            raise ProjectPolicyRequirementError("invalid enforcement config file")

        def strict_pairs(pairs):
            value = {}
            for key, member in pairs:
                if key in value:
                    raise ProjectPolicyRequirementError(
                        f"duplicate enforcement member: {key}"
                    )
                value[key] = member
            return value

        data = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=strict_pairs,
            parse_constant=lambda item: (_ for _ in ()).throw(
                ProjectPolicyRequirementError(f"non-finite value: {item}")
            ),
        )
        if not isinstance(data, dict) or data.get("schema_version") != 1:
            raise ProjectPolicyRequirementError("schema_version must equal 1")
        required = data.get("required_policies")
        if not isinstance(required, list):
            raise ProjectPolicyRequirementError("required_policies must be an array")
        result = []
        for policy_id in required:
            if not isinstance(policy_id, str) or not re.fullmatch(
                r"[a-z0-9][a-z0-9._-]{0,127}", policy_id
            ):
                raise ProjectPolicyRequirementError("invalid required policy id")
            if policy_id in result:
                raise ProjectPolicyRequirementError("duplicate required policy id")
            result.append(policy_id)
        return tuple(result)
    except ProjectPolicyRequirementError:
        raise
    except (OSError, UnicodeError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ProjectPolicyRequirementError("invalid enforcement config") from exc


class FinalizationAction(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"


@dataclass(frozen=True)
class FinalizationContext:
    session_id: str
    task_id: str | None
    turn_id: str | None
    platform: str
    model: str
    project_root: str
    user_message: Any
    response_text: str
    response_sha256: str
    changed_paths: tuple[str, ...] = ()
    loaded_skills: tuple[str, ...] = ()
    mode: str = "working"
    metadata: Any = field(default_factory=lambda: MappingProxyType({}))

    @classmethod
    def for_response(
        cls,
        *,
        session_id: str,
        task_id: str | None,
        turn_id: str | None,
        platform: str,
        model: str,
        project_root: str,
        user_message: Any,
        response_text: str,
        changed_paths: tuple[str, ...] = (),
        loaded_skills: tuple[str, ...] = (),
        mode: str = "working",
        metadata: dict[str, Any] | None = None,
    ) -> "FinalizationContext":
        digest = hashlib.sha256(response_text.encode("utf-8")).hexdigest()
        return cls(
            session_id=session_id,
            task_id=task_id,
            turn_id=turn_id,
            platform=platform,
            model=model,
            project_root=project_root,
            user_message=user_message,
            response_text=response_text,
            response_sha256=digest,
            changed_paths=tuple(changed_paths),
            loaded_skills=tuple(loaded_skills),
            mode=mode,
            metadata=MappingProxyType(dict(metadata or {})),
        )


@dataclass(frozen=True)
class FinalizationDecision:
    action: FinalizationAction
    policy_id: str
    reason_code: str
    user_message: str
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RegisteredFinalizationPolicy:
    id: str
    callback: Callable[[FinalizationContext], FinalizationDecision]
    required: bool = True
    timeout_seconds: float = 30.0
    owner: str = "core"
    turn_predicate: Callable[[str, Any], bool] | None = None

    def __post_init__(self) -> None:
        if not self.id or not isinstance(self.id, str):
            raise ValueError("finalization policy id must be a non-empty string")
        if not callable(self.callback):
            raise TypeError("finalization policy callback must be callable")
        if isinstance(self.timeout_seconds, bool) or self.timeout_seconds <= 0:
            raise ValueError("finalization policy timeout_seconds must be positive")
        if self.turn_predicate is not None and not callable(self.turn_predicate):
            raise TypeError("finalization policy turn_predicate must be callable")


def policy_buffers_turn(
    policy: RegisteredFinalizationPolicy,
    project_root: str,
    user_message: Any,
    *,
    timeout_seconds: float = 2.0,
) -> tuple[bool, str | None]:
    """Evaluate a turn-scope predicate without allowing it to fail open."""
    if policy.turn_predicate is None:
        return True, None
    result_queue: queue.Queue[tuple[str, Any]] = queue.Queue(maxsize=1)
    caller_context = copy_context()

    def run() -> None:
        try:
            value = policy.turn_predicate(project_root, user_message)
            result_queue.put_nowait(("ok", value))
        except BaseException as exc:
            try:
                result_queue.put_nowait(("error", exc))
            except queue.Full:
                pass

    thread = threading.Thread(
        target=lambda: caller_context.run(run),
        name=f"finalization-scope-{policy.id}",
        daemon=True,
    )
    thread.start()
    try:
        status, value = result_queue.get(timeout=float(timeout_seconds))
    except queue.Empty:
        return policy.required, "turn_predicate_timeout"
    if status != "ok" or type(value) is not bool:
        return policy.required, "turn_predicate_error"
    return value, None


@dataclass(frozen=True)
class FinalizationEvaluation:
    action: FinalizationAction
    reason_code: str
    user_message: str
    decisions: tuple[FinalizationDecision, ...]


def _synthetic_decision(policy: RegisteredFinalizationPolicy, reason: str) -> FinalizationDecision:
    prefix = "required" if policy.required else "optional"
    action = FinalizationAction.BLOCK if policy.required else FinalizationAction.ALLOW
    return FinalizationDecision(
        action=action,
        policy_id=policy.id,
        reason_code=f"{prefix}_policy_{reason}",
        user_message=DEFAULT_BLOCK_MESSAGE if policy.required else "",
        evidence={},
    )


def _invoke_with_timeout(
    policy: RegisteredFinalizationPolicy,
    context: FinalizationContext,
) -> tuple[str, Any]:
    """Run a callback on a daemon thread and return status/value.

    Python cannot safely kill a thread.  A timed-out callback may finish later,
    but its result is discarded and it cannot release the buffered response.
    Policies that require process isolation should implement it internally.
    """

    result_queue: queue.Queue[tuple[str, Any]] = queue.Queue(maxsize=1)

    def run() -> None:
        try:
            result_queue.put_nowait(("ok", policy.callback(context)))
        except BaseException as exc:  # Callback failure must never release content.
            try:
                result_queue.put_nowait(("error", exc))
            except queue.Full:
                pass

    caller_context = copy_context()
    thread = threading.Thread(
        target=lambda: caller_context.run(run),
        name=f"finalization-policy-{policy.id}",
        daemon=True,
    )
    thread.start()
    try:
        return result_queue.get(timeout=float(policy.timeout_seconds))
    except queue.Empty:
        return "timeout", None


def _validate_decision(
    policy: RegisteredFinalizationPolicy,
    value: Any,
    max_evidence_bytes: int,
) -> FinalizationDecision | None:
    if not isinstance(value, FinalizationDecision):
        return None
    if value.policy_id != policy.id or not isinstance(value.action, FinalizationAction):
        return None
    if not isinstance(value.reason_code, str) or not value.reason_code:
        return None
    if not isinstance(value.user_message, str) or not isinstance(value.evidence, dict):
        return None
    try:
        encoded = json.dumps(
            value.evidence,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeError):
        return None
    if len(encoded) > max_evidence_bytes:
        return None
    return value


def evaluate_finalization_policies(
    context: FinalizationContext,
    policies: Iterable[RegisteredFinalizationPolicy],
    *,
    max_evidence_bytes: int = 65_536,
) -> FinalizationEvaluation:
    """Evaluate policies in order; every required policy must explicitly allow."""

    if isinstance(max_evidence_bytes, bool) or max_evidence_bytes <= 0:
        raise ValueError("max_evidence_bytes must be positive")

    decisions: list[FinalizationDecision] = []
    first_required_denial: FinalizationDecision | None = None

    for policy in policies:
        status, value = _invoke_with_timeout(policy, context)
        if status == "timeout":
            decision = _synthetic_decision(policy, "timeout")
        elif status == "error":
            decision = _synthetic_decision(policy, "error")
        else:
            decision = _validate_decision(policy, value, max_evidence_bytes)
            if decision is None:
                decision = _synthetic_decision(policy, "malformed")

        decisions.append(decision)
        if policy.required and decision.action is not FinalizationAction.ALLOW:
            if first_required_denial is None:
                first_required_denial = decision

    if first_required_denial is not None:
        return FinalizationEvaluation(
            action=FinalizationAction.BLOCK,
            reason_code=first_required_denial.reason_code,
            user_message=first_required_denial.user_message or DEFAULT_BLOCK_MESSAGE,
            decisions=tuple(decisions),
        )

    return FinalizationEvaluation(
        action=FinalizationAction.ALLOW,
        reason_code="all_required_policies_allowed",
        user_message="",
        decisions=tuple(decisions),
    )
