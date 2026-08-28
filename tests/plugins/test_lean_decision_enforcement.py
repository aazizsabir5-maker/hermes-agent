from __future__ import annotations

from types import SimpleNamespace

from agent.finalization_policy import FinalizationAction, FinalizationContext
from plugins.policies.design_enforcement.policy import DesignCompletionPolicy


def _context(root, *, user="Design a checkout flow", response="A working direction."):
    return FinalizationContext.for_response(
        session_id="session",
        task_id="task",
        turn_id="turn",
        platform="cli",
        model="provider/model",
        project_root=str(root),
        user_message=user,
        response_text=response,
        metadata={},
    )


def _validation(*, passed: bool, reason: str = "ledger_valid", diagnostics=()):
    return SimpleNamespace(
        passed=passed,
        reason_code=reason,
        exit_code=0 if passed else 1,
        stdout="\n".join(diagnostics),
        stderr="",
        diagnostics=tuple(diagnostics),
    )


def _policy(tmp_path, validation=None, *, enforced=True):
    return DesignCompletionPolicy(
        validator_path=tmp_path / "validator.py",
        validator_runner=(
            (lambda *_args, **_kwargs: validation)
            if validation is not None
            else (lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError()))
        ),
        enforced=enforced,
    )


def test_non_design_conversation_does_not_interfere(tmp_path):
    policy = _policy(tmp_path)
    assert policy.applies_to_turn(str(tmp_path), "Explain Python tuples") is False
    decision = policy.evaluate(
        _context(
            tmp_path,
            user="Explain Python tuples",
            response="Tuples are immutable sequences.",
        )
    )
    assert decision.action is FinalizationAction.ALLOW
    assert decision.reason_code == "not_applicable"
    assert not (tmp_path / "DESIGN-DECISIONS.md").exists()


def test_exploratory_design_response_is_allowed_and_initializes_one_ledger(tmp_path):
    policy = _policy(tmp_path)
    assert policy.applies_to_turn(str(tmp_path), "Design a checkout flow") is True
    ledger = tmp_path / "DESIGN-DECISIONS.md"
    assert ledger.is_file()
    original = ledger.read_text(encoding="utf-8")

    decision = policy.evaluate(_context(tmp_path, response="We should compare two approaches."))
    assert decision.action is FinalizationAction.ALLOW
    assert decision.reason_code == "working_response"

    policy.applies_to_turn(str(tmp_path), "Continue the interface design")
    assert ledger.read_text(encoding="utf-8") == original
    assert not (tmp_path / ".hermes" / "enforcement.json").exists()


def test_completion_claim_without_ledger_is_blocked_specifically(tmp_path):
    policy = _policy(
        tmp_path,
        _validation(
            passed=False,
            reason="missing_ledger",
            diagnostics=("DESIGN-DECISIONS.md is missing",),
        ),
    )
    decision = policy.evaluate(
        _context(tmp_path, response="The substantial design is finished.")
    )
    assert decision.action is FinalizationAction.BLOCK
    assert decision.reason_code == "missing_ledger"
    assert "not yet complete" in decision.user_message.lower()
    assert "DESIGN-DECISIONS.md is missing" in decision.user_message


def test_completion_claim_lists_unresolved_decision_ids(tmp_path):
    policy = _policy(
        tmp_path,
        _validation(
            passed=False,
            reason="unresolved_decisions",
            diagnostics=("Unresolved consequential decisions: D-004, D-009",),
        ),
    )
    decision = policy.evaluate(_context(tmp_path, response="The design is complete."))
    assert decision.action is FinalizationAction.BLOCK
    assert "D-004" in decision.user_message
    assert "D-009" in decision.user_message


def test_completion_claim_with_valid_ledger_is_allowed_without_ceremony(tmp_path):
    policy = _policy(tmp_path, _validation(passed=True))
    decision = policy.evaluate(
        _context(tmp_path, response="At prototype fidelity, the design is complete.")
    )
    assert decision.action is FinalizationAction.ALLOW
    assert decision.reason_code == "decision_ledger_valid"
    assert not (tmp_path / "REVIEW-RECEIPT.json").exists()
    assert not (tmp_path / "INDEPENDENT-REVIEW.md").exists()


def test_provisional_or_next_iteration_language_is_allowed_with_unresolved_work(tmp_path):
    policy = _policy(tmp_path)
    for response in (
        "This is provisional; D-004 remains unresolved.",
        "The concept is ready for the next iteration, not final delivery.",
    ):
        decision = policy.evaluate(_context(tmp_path, response=response))
        assert decision.action is FinalizationAction.ALLOW
        assert decision.reason_code == "working_response"


def test_policy_is_inactive_without_hermes_one_launch_marker(tmp_path):
    policy = _policy(tmp_path, enforced=False)
    assert policy.applies_to_turn(str(tmp_path), "Design a checkout flow") is False
    decision = policy.evaluate(_context(tmp_path, response="The design is complete."))
    assert decision.action is FinalizationAction.ALLOW
    assert decision.reason_code == "not_enforced_launch"

