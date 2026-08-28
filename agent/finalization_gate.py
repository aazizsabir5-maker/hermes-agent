"""Small in-memory response gate for registered completion policies."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from agent.finalization_policy import (
    DEFAULT_BLOCK_MESSAGE,
    FinalizationAction,
    FinalizationContext,
    FinalizationDecision,
    RegisteredFinalizationPolicy,
    evaluate_finalization_policies,
)


@dataclass(frozen=True)
class FinalizationGateResult:
    applied: bool
    allowed: bool
    response_text: str
    reason_code: str
    decisions: tuple[FinalizationDecision, ...]


def apply_finalization_gate(
    context: FinalizationContext,
    policies: Iterable[RegisteredFinalizationPolicy],
    *,
    max_evidence_bytes: int = 65_536,
) -> FinalizationGateResult:
    policy_snapshot = tuple(policies)
    if not policy_snapshot:
        return FinalizationGateResult(
            applied=False,
            allowed=True,
            response_text=context.response_text,
            reason_code="no_finalization_policies",
            decisions=(),
        )
    evaluation = evaluate_finalization_policies(
        context, policy_snapshot, max_evidence_bytes=max_evidence_bytes
    )
    allowed = evaluation.action is FinalizationAction.ALLOW
    return FinalizationGateResult(
        applied=True,
        allowed=allowed,
        response_text=(
            context.response_text
            if allowed
            else evaluation.user_message or DEFAULT_BLOCK_MESSAGE
        ),
        reason_code=evaluation.reason_code,
        decisions=evaluation.decisions,
    )
