"""Runtime-owned independent reviewer orchestration."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from agent.subagent_lifecycle import SubagentLaunchRequest, SubagentState
from utils import atomic_json_write

from .receipt import TrustedReceiptStore
from .review_snapshot import (
    collect_design_subject_paths,
    compute_snapshot_hash,
    create_review_snapshot,
)


@dataclass(frozen=True)
class ReviewerResult:
    passed: bool
    reason_code: str
    reviewer_session_id: str | None = None
    subject_sha256: str | None = None
    trusted_receipt_path: Path | None = None


def compute_subject_hash(project_root: Path, validator_path: Path) -> str:
    completed = subprocess.run(
        [sys.executable, str(validator_path), "--subject-hash", str(project_root)],
        cwd=str(project_root),
        capture_output=True,
        timeout=30,
        check=False,
    )
    stdout = (completed.stdout or b"").decode("utf-8", errors="replace").strip()
    if completed.returncode != 0 or len(stdout) != 64 or any(
        char not in "0123456789abcdef" for char in stdout
    ):
        raise RuntimeError("cannot compute canonical design subject hash")
    return stdout


def _strict_json_object(text: str) -> dict[str, Any]:
    def strict_pairs(pairs):
        data = {}
        for key, value in pairs:
            if key in data:
                raise ValueError(f"duplicate reviewer result member: {key}")
            data[key] = value
        return data

    value = json.loads(
        text,
        object_pairs_hook=strict_pairs,
        parse_constant=lambda item: (_ for _ in ()).throw(
            ValueError(f"non-finite reviewer value: {item}")
        ),
    )
    if not isinstance(value, dict):
        raise ValueError("reviewer result must be an object")
    return value


def _atomic_text_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    except Exception:
        try:
            os.unlink(name)
        except OSError:
            pass
        raise


class ReviewOrchestrator:
    def __init__(
        self,
        *,
        lifecycle,
        validator_path: str | Path,
        receipt_store: TrustedReceiptStore,
        snapshot_root: str | Path,
        subject_hasher: Callable[[Path], str] | None = None,
    ):
        self.lifecycle = lifecycle
        self.validator_path = Path(validator_path).resolve(strict=False)
        self.receipt_store = receipt_store
        self.snapshot_root = Path(snapshot_root).resolve(strict=False)
        self.subject_hasher = subject_hasher or (
            lambda root: compute_subject_hash(root, self.validator_path)
        )

    def run(
        self,
        project_root: str | Path,
        *,
        parent_session_id: str,
        reviewer_model: str,
        timeout_seconds: float = 600,
    ) -> ReviewerResult:
        root = Path(project_root).expanduser().resolve(strict=True)
        try:
            live_subject = self.subject_hasher(root)
            subject_paths = collect_design_subject_paths(root)
            snapshot = create_review_snapshot(
                root,
                self.snapshot_root,
                include_paths=subject_paths,
            )
            # The injected hasher is a host-owned dependency (used by tests); in
            # production it is the pinned validator subprocess above. Hash the
            # completed snapshot with the same trusted implementation and bind
            # the receipt only when live and snapshot subjects agree.
            subject = self.subject_hasher(snapshot.path)
            if subject != live_subject:
                return ReviewerResult(False, "review_subject_changed_during_snapshot")
        except Exception:
            return ReviewerResult(False, "review_snapshot_failed")

        goal = (
            "Independently review the design completion subject in this read-only "
            "snapshot. Do not trust claims without evidence. Return ONLY one JSON "
            "object with schema_version=1, subject_sha256 exactly '"
            + subject
            + "', disposition pass|fail, blocking_findings as an array, "
            "non_blocking_findings as an array, and evidence_reviewed as an array. "
            "A pass requires zero blocking findings."
        )
        try:
            request = SubagentLaunchRequest(
                goal=goal,
                context=(
                    "The snapshot hash is "
                    f"{snapshot.subject_sha256}. The canonical validator subject hash "
                    f"is {subject}. Inspect the files; do not modify them."
                ),
                role="leaf",
                model=reviewer_model or None,
                allowed_toolsets=("file-readonly",),
                working_directory=str(snapshot.path),
                parent_session_id=parent_session_id,
                correlation_id=f"design-review:{subject}",
                metadata={"policy": "design-completion", "subject_sha256": subject},
            )
            handle = self.lifecycle.launch(request)
            effective_parent_session = str(
                parent_session_id or getattr(handle, "parent_session_id", "") or ""
            )
            if not effective_parent_session:
                return ReviewerResult(False, "parent_session_missing")
            if handle.subagent_id == effective_parent_session:
                return ReviewerResult(False, "reviewer_not_independent")
            terminal = self.lifecycle.wait(handle, timeout_seconds=timeout_seconds)
            if not terminal.completed or terminal.timed_out:
                return ReviewerResult(False, "reviewer_timeout")
            result = self.lifecycle.result(handle)
            if not result.ready or result.terminal_state not in {
                SubagentState.SUCCEEDED,
                "SUCCEEDED",
            }:
                return ReviewerResult(False, "reviewer_failed")
            payload = _strict_json_object(result.summary or "")
        except Exception:
            return ReviewerResult(False, "reviewer_execution_error")

        if compute_snapshot_hash(snapshot.path) != snapshot.subject_sha256:
            return ReviewerResult(False, "review_snapshot_changed")

        if (
            payload.get("schema_version") != 1
            or payload.get("subject_sha256") != subject
            or payload.get("disposition") != "pass"
            or payload.get("blocking_findings") != []
            or not isinstance(payload.get("non_blocking_findings"), list)
            or not isinstance(payload.get("evidence_reviewed"), list)
        ):
            return ReviewerResult(False, "reviewer_did_not_pass")

        reviewer_session = str(handle.subagent_id)
        reviewer_model_actual = str(handle.model or reviewer_model or "")
        non_blocking = payload["non_blocking_findings"]
        evidence = payload["evidence_reviewed"]
        report = (
            "# Independent design review\n\n"
            "## Review scope\n\n"
            f"- Subject hash reviewed: {subject}\n"
            f"- Reviewer session: {reviewer_session}\n"
            f"- Runtime result hash: {getattr(result, 'result_hash', '') or ''}\n\n"
            "## Disposition\n\n"
            "Disposition: pass\n\n"
            "## Blocking findings\n\n"
            "None.\n\n"
            "## Non-blocking findings\n\n"
            + ("\n".join(f"- {item}" for item in non_blocking) if non_blocking else "None.")
            + "\n\n## Evidence reviewed\n\n"
            + ("\n".join(f"- {item}" for item in evidence) if evidence else "None.")
            + "\n"
        )
        report_path = root / "INDEPENDENT-REVIEW.md"
        try:
            _atomic_text_write(report_path, report)
            report_hash = hashlib.sha256(report_path.read_bytes()).hexdigest()
            local_receipt = {
                "schema_version": 1,
                "subject_sha256": subject,
                "report_sha256": report_hash,
                "reviewer": {
                    "session_id": reviewer_session,
                    "role": "independent-reviewer",
                    "model": reviewer_model_actual,
                    "invocation": "runtime_subagent_lifecycle",
                },
                "reviewed_at": datetime.now(timezone.utc).isoformat(),
                "disposition": "pass",
                "blocking_findings": [],
            }
            atomic_json_write(root / "REVIEW-RECEIPT.json", local_receipt, mode=0o600)
            trusted_path = self.receipt_store.issue(
                parent_session_id=effective_parent_session,
                reviewer_session_id=reviewer_session,
                reviewer_model=reviewer_model_actual,
                subject_sha256=subject,
                report_sha256=report_hash,
                disposition="pass",
            )
        except Exception:
            return ReviewerResult(False, "review_receipt_write_failed")
        return ReviewerResult(
            True,
            "review_passed",
            reviewer_session,
            subject,
            trusted_path,
        )
