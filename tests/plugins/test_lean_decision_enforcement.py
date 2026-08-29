from __future__ import annotations

from types import SimpleNamespace

import pytest

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


def _validation(
    *,
    passed: bool,
    reason: str = "ledger_valid",
    diagnostics=(),
    supported_claim="Prototype-fidelity design complete for cart through confirmation",
):
    return SimpleNamespace(
        passed=passed,
        reason_code=reason,
        exit_code=0 if passed else 1,
        stdout="\n".join(diagnostics),
        stderr="",
        diagnostics=tuple(diagnostics),
        supported_claim=supported_claim if passed else "",
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
        _context(
            tmp_path,
            response="Prototype-fidelity design complete for cart through confirmation.",
        )
    )
    assert decision.action is FinalizationAction.ALLOW
    assert decision.reason_code == "decision_ledger_valid"
    assert not (tmp_path / "REVIEW-RECEIPT.json").exists()
    assert not (tmp_path / "INDEPENDENT-REVIEW.md").exists()


def test_valid_ledger_does_not_release_unqualified_candidate_claim(tmp_path):
    policy = _policy(tmp_path, _validation(passed=True))
    decision = policy.evaluate(_context(tmp_path, response="The design is complete."))
    assert decision.action is FinalizationAction.BLOCK
    assert decision.reason_code == "candidate_claim_unqualified"
    assert "supported claim" in decision.user_message.lower()


def test_provisional_phrase_cannot_negate_an_affirmative_completion_claim(tmp_path):
    policy = _policy(
        tmp_path,
        _validation(
            passed=False,
            reason="unresolved_decisions",
            diagnostics=("Unresolved consequential decisions: D-013",),
        ),
    )
    decision = policy.evaluate(
        _context(
            tmp_path,
            response="The design is complete, although one detail is provisional.",
        )
    )
    assert decision.action is FinalizationAction.BLOCK
    assert "D-013" in decision.user_message


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


@pytest.mark.parametrize(
    "claim",
    (
        "I finished the design.",
        "I've completed the design.",
        "We have now delivered the project.",
        "The work is now done.",
    ),
)
def test_common_first_person_completion_claims_are_validated(tmp_path, claim):
    validation = _validation(
        passed=False,
        reason="unresolved_decisions",
        diagnostics=("Unresolved consequential decisions: D-007",),
    )
    policy = _policy(tmp_path, validation)
    decision = policy.evaluate(_context(tmp_path, response=claim))
    assert decision.action is FinalizationAction.BLOCK
    assert "D-007" in decision.user_message


@pytest.mark.parametrize(
    "user_text",
    (
        "Explain how the solar system works",
        "Explain CPU architecture",
        "What does prototyping mean?",
    ),
)
def test_generic_explanation_does_not_create_design_paperwork(tmp_path, user_text):
    policy = _policy(tmp_path)
    assert policy.applies_to_turn(tmp_path, user_text) is False
    assert not (tmp_path / "DESIGN-DECISIONS.md").exists()


@pytest.mark.parametrize(
    "user_text",
    (
        "How do we design a safer checkout?",
        "What is the best way to prototype this service?",
    ),
)
def test_question_form_design_requests_still_activate_enforcement(tmp_path, user_text):
    policy = _policy(tmp_path)
    assert policy.applies_to_turn(tmp_path, user_text) is True
    assert (tmp_path / "DESIGN-DECISIONS.md").is_file()


def test_existing_ledger_keeps_continuation_but_not_unrelated_turn_in_scope(tmp_path):
    policy = _policy(tmp_path)
    assert policy.applies_to_turn(tmp_path, "Design a checkout flow") is True
    assert policy.applies_to_turn(tmp_path, "Continue.") is True
    assert policy.applies_to_turn(tmp_path, "Explain Python tuples") is False


def test_completion_equivalent_ready_for_handoff_claim_is_validated(tmp_path):
    policy = _policy(
        tmp_path,
        _validation(
            passed=False,
            reason="unresolved_decisions",
            diagnostics=("Unresolved consequential decisions: D-021",),
        ),
    )
    decision = policy.evaluate(
        _context(
            tmp_path,
            response="The design meets all requirements and is ready for handoff.",
        )
    )
    assert decision.action is FinalizationAction.BLOCK
    assert "D-021" in decision.user_message


def test_ready_to_ship_claim_is_validated_but_negated_delivery_is_working_text(tmp_path):
    policy = _policy(
        tmp_path,
        _validation(
            passed=False,
            reason="unresolved_decisions",
            diagnostics=("Unresolved consequential decisions: D-022",),
        ),
    )
    blocked = policy.evaluate(
        _context(tmp_path, response="The design is ready to ship.")
    )
    assert blocked.action is FinalizationAction.BLOCK
    assert "D-022" in blocked.user_message

    working = policy.evaluate(
        _context(tmp_path, response="This is provisional and not a final delivery.")
    )
    assert working.action is FinalizationAction.ALLOW
    assert working.reason_code == "working_response"

    for response in (
        "This isn't a final delivery.",
        "We do not claim a final delivery.",
        "No final delivery is being claimed.",
        "Nothing about this design is complete.",
        "Neither the design nor the implementation is complete.",
        "This isn't production-ready.",
    ):
        working = policy.evaluate(_context(tmp_path, response=response))
        assert working.action is FinalizationAction.ALLOW, response
        assert working.reason_code == "working_response", response


def test_supported_claim_cannot_authorize_a_broader_piggyback_claim(tmp_path):
    policy = _policy(tmp_path, _validation(passed=True))
    response = (
        "Prototype-fidelity design complete for cart through confirmation. "
        "The whole production implementation is complete."
    )
    decision = policy.evaluate(_context(tmp_path, response=response))
    assert decision.action is FinalizationAction.BLOCK
    assert decision.reason_code == "candidate_claim_unqualified"


@pytest.mark.parametrize(
    "response",
    (
        "The design can now be considered complete.",
        "I consider the design complete.",
        "I consider this design complete.",
        "I consider our design complete.",
        "There is no doubt: the design is complete.",
        "No caveat: design is complete.",
        "Nothing about the implementation is complete but the design is complete.",
        "The design is launch-ready.",
    ),
)
def test_additional_common_completion_equivalents_are_validated(tmp_path, response):
    policy = _policy(
        tmp_path,
        _validation(
            passed=False,
            reason="unresolved_decisions",
            diagnostics=("Unresolved consequential decisions: D-023",),
        ),
    )
    decision = policy.evaluate(_context(tmp_path, response=response))
    assert decision.action is FinalizationAction.BLOCK
    assert "D-023" in decision.user_message
