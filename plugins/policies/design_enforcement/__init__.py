"""Bundled, auto-loaded fail-closed design completion policy."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from agent.runtime_cwd import resolve_context_cwd
from hermes_constants import get_hermes_home

from .policy import DesignCompletionPolicy
from .receipt import TrustedReceiptStore
from .reviewer import ReviewOrchestrator


_REPO_ROOT = Path(__file__).resolve().parents[3]
_SKILL_ROOT = _REPO_ROOT / "skills" / "design" / "comprehensive-designer-cognition"
_VALIDATOR = _SKILL_ROOT / "scripts" / "validate_design_completion.py"
_SKILL = _SKILL_ROOT / "SKILL.md"


def _review_tool_schema() -> dict[str, Any]:
    return {
        "name": "design_review_request",
        "description": (
            "Create a host-owned immutable design snapshot, launch an independent "
            "Hermes reviewer child, and issue runtime-bound review receipts. Use "
            "after builder-owned completion artifacts are finalized and before "
            "claiming completion."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "project_root": {
                    "type": "string",
                    "description": "Canonical project root. Defaults to the active project cwd.",
                },
                "reviewer_model": {
                    "type": "string",
                    "description": "Optional reviewer model override.",
                },
                "timeout_seconds": {
                    "type": "number",
                    "minimum": 30,
                    "maximum": 1800,
                    "default": 600,
                },
            },
            "additionalProperties": False,
        },
    }


def register(ctx) -> None:
    def verify_receipt(*, parent_session_id: str, subject_sha256: str, report_sha256: str) -> bool:
        receipt_store = TrustedReceiptStore(
            get_hermes_home() / "enforcement" / "design-receipts"
        )
        path = receipt_store.find(
            parent_session_id=parent_session_id,
            subject_sha256=subject_sha256,
        )
        return receipt_store.verify(
            path,
            parent_session_id=parent_session_id,
            subject_sha256=subject_sha256,
            report_sha256=report_sha256,
        )

    policy = DesignCompletionPolicy(
        validator_path=_VALIDATOR,
        receipt_verifier=verify_receipt,
        expected_validator_sha256=hashlib.sha256(_VALIDATOR.read_bytes()).hexdigest(),
    )
    ctx.register_finalization_policy(
        id="design-completion",
        callback=policy.evaluate,
        required=True,
        timeout_seconds=45.0,
        turn_predicate=policy.applies_to_turn,
    )

    # Load the full standalone protocol into one frozen, cache-stable system
    # prompt section so markdown structure and fenced examples remain intact.
    skill_text = _SKILL.read_text(encoding="utf-8")
    required_skill_prompt = (
        "MANDATORY REQUIRED POLICY SKILL. Follow this complete protocol for "
        "every applicable design task. Core—not model prose—owns final release.\n\n"
        + skill_text
    )
    ctx.register_system_prompt_section(
        "design-enforcement.skill",
        lambda session_info: (
            required_skill_prompt
            if "design-completion"
            in str(session_info.get("active_finalization_policy_ids", "")).split(",")
            else ""
        ),
        max_chars=min(40_000, len(required_skill_prompt)),
    )

    def handle_review(args: dict[str, Any], session_id: str = "", **_: Any) -> str:
        home = get_hermes_home()
        receipt_store = TrustedReceiptStore(
            home / "enforcement" / "design-receipts"
        )
        reviewer = ReviewOrchestrator(
            lifecycle=ctx.subagent_lifecycle,
            validator_path=_VALIDATOR,
            receipt_store=receipt_store,
            snapshot_root=home / "enforcement" / "design-snapshots",
        )
        project_arg = str(args.get("project_root") or "").strip()
        if project_arg:
            root = Path(project_arg).expanduser().resolve(strict=True)
        else:
            root = (resolve_context_cwd() or Path.cwd()).resolve(strict=True)
        result = reviewer.run(
            root,
            parent_session_id=str(session_id or ""),
            reviewer_model=str(args.get("reviewer_model") or ""),
            timeout_seconds=float(args.get("timeout_seconds") or 600),
        )
        return json.dumps(
            {
                "passed": result.passed,
                "reason_code": result.reason_code,
                "reviewer_session_id": result.reviewer_session_id,
                "subject_sha256": result.subject_sha256,
            },
            sort_keys=True,
        )

    ctx.register_tool(
        name="design_review_request",
        toolset="design-enforcement",
        schema=_review_tool_schema(),
        handler=handle_review,
        emoji="🛡️",
    )
