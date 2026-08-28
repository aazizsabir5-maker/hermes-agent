"""The lean gate replaces a candidate response without provenance state."""

from agent.finalization_gate import apply_finalization_gate
from agent.finalization_policy import (
    FinalizationAction,
    FinalizationContext,
    FinalizationDecision,
    RegisteredFinalizationPolicy,
)


def _context(text="At prototype fidelity, the design is complete."):
    return FinalizationContext.for_response(
        session_id="session",
        task_id="task",
        turn_id="turn",
        platform="cli",
        model="provider/model",
        project_root="/tmp/project",
        user_message="Finish this design",
        response_text=text,
        metadata={"active_policy_ids": ("design-completion",)},
    )


def _policy(action, message=""):
    return RegisteredFinalizationPolicy(
        "design-completion",
        lambda _context: FinalizationDecision(
            action,
            "design-completion",
            "ledger_valid" if action is FinalizationAction.ALLOW else "missing_ledger",
            message,
        ),
    )


def test_allow_returns_candidate_without_writing_runtime_state(tmp_path):
    before = set(tmp_path.iterdir())
    result = apply_finalization_gate(
        _context(), [_policy(FinalizationAction.ALLOW)]
    )
    assert result.allowed is True
    assert result.response_text == _context().response_text
    assert set(tmp_path.iterdir()) == before
    assert not hasattr(result, "audit_id")
    assert not hasattr(result, "response_sha256")


def test_block_uses_specific_host_authored_policy_message():
    message = "This design is not yet complete. DESIGN-DECISIONS.md is missing"
    result = apply_finalization_gate(
        _context("candidate completion claim"),
        [_policy(FinalizationAction.BLOCK, message)],
    )
    assert result.allowed is False
    assert result.response_text == message
    assert "candidate completion claim" not in result.response_text


def test_no_policy_leaves_ordinary_response_unchanged():
    result = apply_finalization_gate(_context("ordinary response"), [])
    assert result.applied is False
    assert result.allowed is True
    assert result.response_text == "ordinary response"
