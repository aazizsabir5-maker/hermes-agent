"""Mode-free completion-claim policy for observable design decisions."""

from __future__ import annotations

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


_DEFAULT_LEDGER_TEMPLATE = (
    Path(__file__).resolve().parents[3]
    / "skills"
    / "design"
    / "comprehensive-designer-cognition"
    / "templates"
    / "DESIGN-DECISIONS.md"
)
_EXPLICIT_DESIGN_RE = re.compile(
    r"\b(design|redesign|architect|prototype)\b",
    re.IGNORECASE,
)
_EXPLANATORY_RE = re.compile(
    r"^\s*(explain|define|what\s+(?:is|are|does|do)|how\s+(?:does|do)|"
    r"tell\s+me\s+about|why\s+(?:is|are|does|do))\b",
    re.IGNORECASE,
)
_BUILD_DESIGN_RE = re.compile(
    r"\b(build|create|develop|make|plan|revamp|shape)\b.{0,80}\b("
    r"service|interaction|workflow|policy|product|organization|space|identity|"
    r"interface|website|dashboard|checkout|page|screen|mobile app|application|"
    r"brand|logo|presentation|deck|diagram|visual|layout)\b",
    re.IGNORECASE,
)
_FINISH_REQUEST_RE = re.compile(
    r"\b(finish|complete|finalize|deliver|ship)\b.{0,40}\b(project|design|work|it)\b|"
    r"\b(project|design|work|it)\b.{0,40}\b(finished|complete|finalized|delivered|shipped)\b",
    re.IGNORECASE,
)
_COMPLETION_CLAIM_RE = re.compile(
    r"\b(is|are|'s|has been|have been)\s+(?:now\s+)?(?:fully\s+)?"
    r"(complete|completed|finished|finalized|done|delivered|shipped)\b|"
    r"\b(production[- ]ready|fully designed|final delivery|completion claim)\b|"
    r"\b(?:i|we)(?:'ve| have)?\s+(?:now\s+)?(?:fully\s+)?"
    r"(?:completed|finished|finalized|delivered|shipped)\b|"
    r"\b(?:i|we)(?:'m| am| are)\s+(?:now\s+)?done\b|"
    r"^(?:done|complete|completed|finished|finalized|delivered|shipped)[.!]?$",
    re.IGNORECASE | re.MULTILINE,
)
_PROVISIONAL_RE = re.compile(
    r"\b(provisional|not (?:yet )?(?:complete|finished|done)|"
    r"ready for (?:the )?(?:next|another) (?:iteration|commitment)|"
    r"validation pending|partially specified)\b",
    re.IGNORECASE,
)


def _stringify(value: Any) -> str:
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    except Exception:
        return str(value)


def _enabled(value: bool | Callable[[], bool]) -> bool:
    return bool(value() if callable(value) else value)


def _is_design_request(text: str) -> bool:
    if _EXPLANATORY_RE.search(text):
        return False
    return bool(_EXPLICIT_DESIGN_RE.search(text) or _BUILD_DESIGN_RE.search(text))


class DesignCompletionPolicy:
    def __init__(
        self,
        *,
        validator_path: str | Path,
        validator_runner: Callable[..., Any] = run_validator,
        enforced: bool | Callable[[], bool] = True,
        ledger_template_path: str | Path | None = None,
        timeout_seconds: float = 30.0,
    ):
        self.validator_path = Path(validator_path)
        self.validator_runner = validator_runner
        self.enforced = enforced
        derived_template = (
            self.validator_path.parent.parent / "templates" / "DESIGN-DECISIONS.md"
        )
        self.ledger_template_path = Path(
            ledger_template_path
            or (derived_template if derived_template.is_file() else _DEFAULT_LEDGER_TEMPLATE)
        )
        self.timeout_seconds = timeout_seconds

    def _ensure_ledger(self, root: Path) -> None:
        ledger = root / "DESIGN-DECISIONS.md"
        if ledger.exists() or ledger.is_symlink() or not root.is_dir():
            return
        try:
            content = self.ledger_template_path.read_text(encoding="utf-8")
            with ledger.open("x", encoding="utf-8") as handle:
                handle.write(content)
        except FileExistsError:
            return
        except (OSError, UnicodeError):
            # Completion validation will report the missing/unreadable ledger.
            return

    def applies_to_turn(self, project_root: str, user_message: Any) -> bool:
        if not _enabled(self.enforced):
            return False
        text = _stringify(user_message)
        design_request = _is_design_request(text)
        finish_request = bool(_FINISH_REQUEST_RE.search(text))
        if design_request:
            root = Path(project_root).expanduser().resolve(strict=False)
            self._ensure_ledger(root)
        return design_request or finish_request

    def evaluate(self, context: FinalizationContext) -> FinalizationDecision:
        if not _enabled(self.enforced):
            return FinalizationDecision(
                FinalizationAction.ALLOW,
                "design-completion",
                "not_enforced_launch",
                "",
            )

        request_text = _stringify(context.user_message)
        runtime_active = "design-completion" in set(
            context.metadata.get("active_policy_ids", ())
        )
        applicable = (
            runtime_active
            or _is_design_request(request_text)
            or bool(_FINISH_REQUEST_RE.search(request_text))
        )
        if not applicable:
            return FinalizationDecision(
                FinalizationAction.ALLOW,
                "design-completion",
                "not_applicable",
                "",
            )

        response = context.response_text or ""
        completion_claim = bool(_COMPLETION_CLAIM_RE.search(response))
        if _PROVISIONAL_RE.search(response):
            completion_claim = False
        if not completion_claim:
            return FinalizationDecision(
                FinalizationAction.ALLOW,
                "design-completion",
                "working_response",
                "",
                evidence={"applicable": True},
            )

        root = Path(context.project_root).expanduser().resolve(strict=False)
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
                "This design is not yet complete. The decision ledger could not be validated.",
            )
        if validation.passed:
            return FinalizationDecision(
                FinalizationAction.ALLOW,
                "design-completion",
                "decision_ledger_valid",
                "",
                evidence={"ledger_valid": True},
            )

        diagnostics = tuple(getattr(validation, "diagnostics", ()) or ())
        if not diagnostics:
            diagnostics = tuple(
                line[2:] if line.startswith("- ") else line
                for line in str(getattr(validation, "stdout", "")).splitlines()
                if line.strip() and "NOT YET COMPLETE" not in line
            )
        detail = "; ".join(diagnostics[:8]) or "Required decision evidence is missing."
        return FinalizationDecision(
            FinalizationAction.BLOCK,
            "design-completion",
            str(getattr(validation, "reason_code", "ledger_invalid")),
            f"This design is not yet complete. {detail}",
            evidence={"ledger_valid": False, "diagnostics": diagnostics[:8]},
        )
