"""The host release gate persists its decision before returning deliverable text."""

from __future__ import annotations

import json

from agent.finalization_gate import (
    AUDIT_FAILURE_MESSAGE,
    DEFAULT_BLOCK_MESSAGE,
    apply_finalization_gate,
)
from agent.finalization_policy import (
    FinalizationAction,
    FinalizationContext,
    FinalizationDecision,
    RegisteredFinalizationPolicy,
)


def _context(text="candidate secret"):
    return FinalizationContext.for_response(
        session_id="s1",
        task_id="task1",
        turn_id="turn1",
        platform="cli",
        model="provider/model",
        project_root="/tmp/project",
        user_message="finish it",
        response_text=text,
        mode="finalizing",
    )


def _policy(action=FinalizationAction.ALLOW):
    def callback(_ctx):
        return FinalizationDecision(
            action=action,
            policy_id="required",
            reason_code="passed" if action is FinalizationAction.ALLOW else "failed",
            user_message="" if action is FinalizationAction.ALLOW else "Completion blocked.",
            evidence={"subject_sha256": "a" * 64},
        )

    return RegisteredFinalizationPolicy(id="required", callback=callback, owner="test")


def test_allow_is_audited_before_candidate_is_released(tmp_path):
    audit = tmp_path / "audit.jsonl"
    result = apply_finalization_gate(_context(), [_policy()], audit_path=audit)
    assert result.allowed is True
    assert result.response_text == "candidate secret"
    record = json.loads(audit.read_text(encoding="utf-8"))
    assert record["decision"] == "allow"
    assert record["response_sha256"] == _context().response_sha256
    assert record["policy_ids"] == ["required"]
    assert result.audit_id == record["audit_id"]


def test_denial_discards_candidate_and_audits_block(tmp_path):
    audit = tmp_path / "audit.jsonl"
    result = apply_finalization_gate(
        _context(), [_policy(FinalizationAction.BLOCK)], audit_path=audit
    )
    assert result.allowed is False
    assert result.response_text == DEFAULT_BLOCK_MESSAGE
    assert "candidate secret" not in result.response_text
    assert json.loads(audit.read_text(encoding="utf-8"))["decision"] == "block"


def test_policy_cannot_echo_candidate_through_denial_message(tmp_path):
    policy = RegisteredFinalizationPolicy(
        "required",
        lambda context: FinalizationDecision(
            FinalizationAction.BLOCK,
            "required",
            "denied",
            context.response_text,
        ),
    )
    result = apply_finalization_gate(
        _context("CANDIDATE SECRET"),
        [policy],
        audit_path=tmp_path / "audit.jsonl",
    )
    assert result.response_text == DEFAULT_BLOCK_MESSAGE
    assert "CANDIDATE" not in result.response_text


def test_audit_write_failure_blocks_even_when_policy_allows(tmp_path):
    directory = tmp_path / "not-a-file"
    directory.mkdir()
    result = apply_finalization_gate(_context(), [_policy()], audit_path=directory)
    assert result.allowed is False
    assert result.reason_code == "finalization_audit_failed"
    assert "candidate secret" not in result.response_text


def test_unprotected_turn_is_unchanged_and_creates_no_audit(tmp_path):
    audit = tmp_path / "audit.jsonl"
    result = apply_finalization_gate(_context(), [], audit_path=audit)
    assert result.allowed is True
    assert result.response_text == "candidate secret"
    assert result.applied is False
    assert not audit.exists()


def test_audit_is_idempotent_for_same_turn_and_response(tmp_path):
    audit = tmp_path / "audit.jsonl"
    first = apply_finalization_gate(_context(), [_policy()], audit_path=audit)
    second = apply_finalization_gate(_context(), [_policy()], audit_path=audit)
    lines = audit.read_text(encoding="utf-8").splitlines()
    assert first.audit_id == second.audit_id
    assert len(lines) == 1


def test_torn_audit_tail_blocks_release(tmp_path):
    audit = tmp_path / "audit.jsonl"
    audit.write_text('{"audit_id":"truncated"', encoding="utf-8")

    result = apply_finalization_gate(_context(), [_policy()], audit_path=audit)

    assert result.allowed is False
    assert result.reason_code == "finalization_audit_failed"
    assert result.response_text == AUDIT_FAILURE_MESSAGE
