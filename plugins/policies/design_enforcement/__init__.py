"""Bundled policy that injects the decision philosophy for ``hermes 1``."""

from __future__ import annotations

import os
from pathlib import Path

from .policy import DesignCompletionPolicy


_REPO_ROOT = Path(__file__).resolve().parents[3]
_SKILL_ROOT = _REPO_ROOT / "skills" / "design" / "comprehensive-designer-cognition"
_VALIDATOR = _SKILL_ROOT / "scripts" / "validate_design_completion.py"
_LEDGER_TEMPLATE = _SKILL_ROOT / "templates" / "DESIGN-DECISIONS.md"
_SKILL = _SKILL_ROOT / "SKILL.md"
DECISION_LAUNCH_ENV = "HERMES_INTERNAL_DECISION_ENFORCED"
_decision_enforced = os.environ.get(DECISION_LAUNCH_ENV) == "1"


def enable_decision_enforcement() -> None:
    """Mark this process as launched through the internal ``hermes 1`` entry point."""
    global _decision_enforced
    _decision_enforced = True
    os.environ[DECISION_LAUNCH_ENV] = "1"


def decision_enforcement_enabled() -> bool:
    return _decision_enforced


def register(ctx) -> None:
    policy = DesignCompletionPolicy(
        validator_path=_VALIDATOR,
        ledger_template_path=_LEDGER_TEMPLATE,
        enforced=decision_enforcement_enabled,
    )
    ctx.register_finalization_policy(
        id="design-completion",
        callback=policy.evaluate,
        required=True,
        timeout_seconds=35.0,
        turn_predicate=policy.applies_to_turn,
    )

    skill_text = _SKILL.read_text(encoding="utf-8")
    required_skill_prompt = (
        "MANDATORY DECISION PHILOSOPHY FOR THIS ENFORCED DESIGN SESSION. "
        "Apply it proportionately and maintain DESIGN-DECISIONS.md automatically.\n\n"
        + skill_text
    )
    ctx.register_system_prompt_section(
        "design-enforcement.skill",
        lambda session_info: (
            required_skill_prompt
            if decision_enforcement_enabled()
            or str(session_info.get("decision_enforced", "")).lower() == "true"
            else ""
        ),
        max_chars=min(40_000, len(required_skill_prompt)),
    )
