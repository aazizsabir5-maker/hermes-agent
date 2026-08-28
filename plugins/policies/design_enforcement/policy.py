"""Host-owned applicability, mode, and completion policy for design work."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Callable

from agent.finalization_policy import (
    FinalizationAction,
    FinalizationContext,
    FinalizationDecision,
)

from .validator_runner import run_validator
from .reviewer import compute_subject_hash


_DESIGN_RE = re.compile(
    r"\b(design|redesign|architect|architecture|experience|system|service|"
    r"interaction|workflow|policy|product|organization|space|identity|interface|"
    r"website|dashboard|checkout|page|screen|mobile app|application|prototype|"
    r"brand|logo|presentation|deck|diagram|visual|layout)\b",
    re.IGNORECASE,
)
_COMPLETION_RE = re.compile(
    r"\b(complete(?:d)?|finished|final(?:ized)?|done|delivered|ready|"
    r"implemented|built|shipped|production[- ]ready|fully designed|here it is)\b",
    re.IGNORECASE,
)


def _strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def _load_json(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_strict_object,
        parse_constant=lambda value: (_ for _ in ()).throw(
            ValueError(f"non-finite JSON value: {value}")
        ),
    )


def _stringify_user_message(value: Any) -> str:
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    except Exception:
        return str(value)


class DesignCompletionPolicy:
    def __init__(
        self,
        *,
        validator_path: str | Path,
        validator_runner: Callable[..., Any] = run_validator,
        receipt_verifier: Callable[..., bool],
        subject_hasher: Callable[[Path, Path], str] = compute_subject_hash,
        expected_validator_sha256: str | None = None,
        timeout_seconds: float = 30.0,
    ):
        self.validator_path = Path(validator_path)
        self.validator_runner = validator_runner
        self.receipt_verifier = receipt_verifier
        self.subject_hasher = subject_hasher
        self.expected_validator_sha256 = expected_validator_sha256
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def _project_policy(root: Path) -> tuple[dict[str, Any] | None, str | None]:
        path = root / ".hermes" / "enforcement.json"
        if not path.exists():
            return None, None
        try:
            data = _load_json(path)
            if not isinstance(data, dict) or data.get("schema_version") != 1:
                raise ValueError("schema_version must equal 1")
            required = data.get("required_policies")
            if not isinstance(required, list) or not all(
                isinstance(item, str) for item in required
            ):
                raise ValueError("required_policies must be a string array")
            design = data.get("design", {})
            if not isinstance(design, dict):
                raise ValueError("design must be an object")
            mode = design.get("mode", "working")
            if mode not in {"working", "finalizing"}:
                raise ValueError("design.mode must be working or finalizing")
            applicable = design.get("applicable", True)
            if not isinstance(applicable, bool):
                raise ValueError("design.applicable must be boolean")
            return data, None
        except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError) as exc:
            return None, str(exc)

    def applies_to_turn(self, project_root: str, user_message: Any) -> bool:
        """Trusted turn-start scope used to decide whether text must buffer."""
        root = Path(project_root).expanduser().resolve(strict=False)
        project_policy, config_error = self._project_policy(root)
        if config_error:
            # Present-but-invalid policy state is protected and will block at
            # finalization rather than silently reverting to streaming.
            return True
        explicitly_required = bool(
            project_policy
            and "design-completion" in project_policy.get("required_policies", [])
        )
        return explicitly_required or bool(
            _DESIGN_RE.search(_stringify_user_message(user_message))
        )

    def evaluate(self, context: FinalizationContext) -> FinalizationDecision:
        root = Path(context.project_root).expanduser().resolve(strict=False)
        project_policy, config_error = self._project_policy(root)
        request_text = _stringify_user_message(context.user_message)
        heuristic_applicable = bool(_DESIGN_RE.search(request_text))
        explicitly_required = bool(
            project_policy
            and "design-completion" in project_policy.get("required_policies", [])
        )
        runtime_active = "design-completion" in set(
            context.metadata.get("active_policy_ids", ())
        )
        required_at_turn_start = "design-completion" in set(
            context.metadata.get("project_required_policy_ids_at_turn_start", ())
        )
        applicable = (
            heuristic_applicable
            or explicitly_required
            or runtime_active
            or required_at_turn_start
        )

        if config_error:
            return FinalizationDecision(
                FinalizationAction.BLOCK,
                "design-completion",
                "configuration_invalid",
                "Final delivery blocked: the project design-enforcement configuration is invalid.",
                {"configuration_valid": False},
            )
        if not applicable:
            return FinalizationDecision(
                FinalizationAction.ALLOW,
                "design-completion",
                "not_applicable",
                "",
                {
                    "applicable": False,
                    "reason": "No explicit project requirement or design-task signal.",
                },
            )

        design_cfg = project_policy.get("design", {}) if project_policy else {}

        completion_attempt = (
            design_cfg.get("mode") == "finalizing"
            or context.mode == "finalizing"
            or bool(_COMPLETION_RE.search(context.response_text))
        )
        if not completion_attempt:
            return FinalizationDecision(
                FinalizationAction.ALLOW,
                "design-completion",
                "working_mode",
                "",
                {"applicable": True, "mode": "working"},
            )

        try:
            validation = self.validator_runner(
                root,
                validator_path=self.validator_path,
                timeout_seconds=self.timeout_seconds,
            )
        except Exception:
            return FinalizationDecision(
                FinalizationAction.BLOCK,
                "design-completion",
                "validator_execution_error",
                "Final delivery blocked: the design validator could not be executed.",
                {"applicable": True, "mode": "finalizing"},
            )
        if (
            self.expected_validator_sha256
            and validation.validator_sha256 != self.expected_validator_sha256
        ):
            return FinalizationDecision(
                FinalizationAction.BLOCK,
                "design-completion",
                "validator_identity_changed",
                "Final delivery blocked: the trusted design validator changed during this runtime.",
                {
                    "applicable": True,
                    "mode": "finalizing",
                    "validator_identity_valid": False,
                },
            )
        if not validation.passed:
            return FinalizationDecision(
                FinalizationAction.BLOCK,
                "design-completion",
                str(validation.reason_code),
                "Final delivery blocked: the deterministic design contract did not pass.",
                {
                    "applicable": True,
                    "mode": "finalizing",
                    "validator_exit_code": validation.exit_code,
                    "validator_sha256": validation.validator_sha256,
                },
            )

        try:
            local_receipt = _load_json(root / "REVIEW-RECEIPT.json")
            if not isinstance(local_receipt, dict):
                raise ValueError("receipt must be an object")
            subject = str(local_receipt.get("subject_sha256", ""))
            current_subject = self.subject_hasher(root, self.validator_path)
            if subject != current_subject:
                raise ValueError("local review receipt is stale")
            report_hash = str(local_receipt.get("report_sha256", ""))
            report = root / "INDEPENDENT-REVIEW.md"
            actual_report_hash = hashlib.sha256(report.read_bytes()).hexdigest()
            if report_hash != actual_report_hash:
                raise ValueError("review report changed after receipt")
            trusted = self.receipt_verifier(
                parent_session_id=context.session_id,
                subject_sha256=subject,
                report_sha256=report_hash,
            )
        except Exception:
            trusted = False
            subject = ""
            report_hash = ""
        if not trusted:
            return FinalizationDecision(
                FinalizationAction.BLOCK,
                "design-completion",
                "trusted_review_missing_or_stale",
                "Final delivery blocked: a fresh runtime-verified independent review is required.",
                {
                    "applicable": True,
                    "mode": "finalizing",
                    "validator_passed": True,
                    "trusted_review": False,
                },
            )

        return FinalizationDecision(
            FinalizationAction.ALLOW,
            "design-completion",
            "design_completion_passed",
            "",
            {
                "applicable": True,
                "mode": "finalizing",
                "validator_exit_code": validation.exit_code,
                "validator_sha256": validation.validator_sha256,
                "subject_sha256": subject,
                "report_sha256": report_hash,
                "trusted_review": True,
            },
        )
