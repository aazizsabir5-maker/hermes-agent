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
_QUESTION_DESIGN_INTENT_RE = re.compile(
    r"^\s*(?:how\s+do\s+(?:we|i|you)|what\s+is\s+(?:the\s+)?"
    r"(?:best|right|safest|simplest)\s+way\s+to)\b.{0,80}\b"
    r"(?:design|redesign|architect|prototype)\b",
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
_CONTINUATION_RE = re.compile(
    r"^\s*(?:continue|go on|proceed|keep going|carry on|next|finish it|complete it)"
    r"(?:\s+(?:please|now))?[.!?]?\s*$",
    re.IGNORECASE,
)
_COMPLETION_CLAIM_RE = re.compile(
    r"\b(is|are|'s|has been|have been)\s+(?:now\s+)?(?:fully\s+)?"
    r"(complete|completed|finished|finalized|done|delivered|shipped)\b|"
    r"(?<!not )\b(production[- ]ready|fully designed|completion claim)\b|"
    r"(?<!not )(?<!not a )(?<!not yet )\bfinal delivery\b|"
    r"\b(?:i|we)(?:'ve| have)?\s+(?:now\s+)?(?:fully\s+)?"
    r"(?:completed|finished|finalized|delivered|shipped)\b|"
    r"\b(?:i|we)(?:'m| am| are)\s+(?:now\s+)?done\b|"
    r"\b(?:concept|prototype|system|high[- ]fidelity|production(?:[- ]implementation)?)"
    r"[- ](?:fidelity[- ]?)?(?:design|artifact|implementation)?\s+complete\b|"
    r"\bsystem\s+specified\b|"
    r"\b(?:meets all requirements|ready for handoff)\b|"
    r"\b(?:is\s+)?ready\s+(?:to ship|for delivery)\b|"
    r"\brequirements\s+(?:are\s+)?satisfied\b|"
    r"^(?:done|complete|completed|finished|finalized|delivered|shipped)[.!]?$",
    re.IGNORECASE | re.MULTILINE,
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


def _normalized_claim(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().rstrip(".!?").casefold()


def _completion_claim_fragments(value: str) -> tuple[str, ...]:
    fragments = re.split(r"[.!?]+(?:\s+|$)|\n+", value)
    return tuple(
        fragment.strip()
        for fragment in fragments
        if fragment.strip() and _COMPLETION_CLAIM_RE.search(fragment)
    )


def _is_design_request(text: str) -> bool:
    if _EXPLANATORY_RE.search(text) and not _QUESTION_DESIGN_INTENT_RE.search(text):
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
        root = Path(project_root).expanduser().resolve(strict=False)
        if (root / "DESIGN-DECISIONS.md").is_file() and _CONTINUATION_RE.search(text):
            return True
        design_request = _is_design_request(text)
        finish_request = bool(_FINISH_REQUEST_RE.search(text))
        if design_request:
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
        completion_claim_fragments = _completion_claim_fragments(response)
        if not completion_claim_fragments:
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
            supported_claim = str(getattr(validation, "supported_claim", "") or "").strip()
            supported_normalized = _normalized_claim(supported_claim)
            candidate_claims = tuple(
                _normalized_claim(fragment) for fragment in completion_claim_fragments
            )
            if (
                not supported_normalized
                or not candidate_claims
                or any(claim != supported_normalized for claim in candidate_claims)
            ):
                return FinalizationDecision(
                    FinalizationAction.BLOCK,
                    "design-completion",
                    "candidate_claim_unqualified",
                    "This design is not yet complete. Use the ledger's fidelity- and "
                    "scope-qualified supported claim before declaring completion.",
                    evidence={"ledger_valid": True, "candidate_claim_qualified": False},
                )
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
