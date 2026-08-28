import hashlib
import json
from types import SimpleNamespace

from agent.finalization_policy import FinalizationAction, FinalizationContext
from plugins.policies.design_enforcement.policy import DesignCompletionPolicy


def _context(
    root,
    *,
    user="Design a service",
    response="Here is a direction.",
    session="builder",
    metadata=None,
):
    return FinalizationContext.for_response(
        session_id=session,
        task_id="task",
        turn_id="turn",
        platform="cli",
        model="provider/model",
        project_root=str(root),
        user_message=user,
        response_text=response,
        mode="working",
        metadata=metadata,
    )


def _pass_result():
    return SimpleNamespace(
        passed=True,
        reason_code="validator_passed",
        exit_code=0,
        stdout="DESIGN COMPLETION: CONTRACT PASSED\n",
        stderr="",
        validator_sha256="a" * 64,
    )


def test_non_design_and_working_design_responses_are_allowed(tmp_path):
    policy = DesignCompletionPolicy(
        validator_path=tmp_path / "validator.py",
        validator_runner=lambda *_a, **_kw: (_ for _ in ()).throw(AssertionError()),
        receipt_verifier=lambda **_kw: False,
    )
    non_design = policy.evaluate(_context(tmp_path, user="What is the weather?"))
    assert policy.applies_to_turn(str(tmp_path), "What is the weather?") is False
    assert non_design.action is FinalizationAction.ALLOW
    assert non_design.reason_code == "not_applicable"

    working = policy.evaluate(_context(tmp_path, response="We should compare two approaches."))
    assert policy.applies_to_turn(str(tmp_path), "Design a service") is True
    assert working.action is FinalizationAction.ALLOW
    assert working.reason_code == "working_mode"


def test_design_completion_claim_without_contract_blocks(tmp_path):
    policy = DesignCompletionPolicy(
        validator_path=tmp_path / "validator.py",
        validator_runner=lambda *_a, **_kw: SimpleNamespace(
            passed=False,
            reason_code="validator_nonzero_exit",
            exit_code=1,
            stdout="",
            stderr="missing artifacts",
            validator_sha256="a" * 64,
        ),
        receipt_verifier=lambda **_kw: False,
    )
    decision = policy.evaluate(
        _context(tmp_path, response="The full design is complete and ready for delivery.")
    )
    assert decision.action is FinalizationAction.BLOCK
    assert decision.reason_code == "validator_nonzero_exit"
    assert "missing artifacts" not in decision.user_message


def test_domain_neutral_product_design_prompts_and_short_delivery_claims_block(tmp_path):
    policy = DesignCompletionPolicy(
        validator_path=tmp_path / "validator.py",
        validator_runner=lambda *_a, **_kw: SimpleNamespace(
            passed=False,
            reason_code="validator_nonzero_exit",
            exit_code=1,
            stdout="",
            stderr="missing artifacts",
            validator_sha256="a" * 64,
        ),
        receipt_verifier=lambda **_kw: False,
    )
    for request, response in (
        ("Build me a checkout page", "Here it is."),
        ("Create a mobile app", "Shipped for you."),
    ):
        assert policy.applies_to_turn(str(tmp_path), request) is True
        decision = policy.evaluate(_context(tmp_path, user=request, response=response))
        assert decision.action is FinalizationAction.BLOCK


def test_present_invalid_project_policy_blocks_even_without_design_keyword(tmp_path):
    (tmp_path / ".hermes").mkdir()
    (tmp_path / ".hermes" / "enforcement.json").write_text(
        '{"schema_version":1,"required_policies":[],"design":{"mode":"bogus"}}',
        encoding="utf-8",
    )
    policy = DesignCompletionPolicy(
        validator_path=tmp_path / "validator.py",
        validator_runner=lambda *_a, **_kw: (_ for _ in ()).throw(AssertionError()),
        receipt_verifier=lambda **_kw: False,
    )
    decision = policy.evaluate(
        _context(tmp_path, user="Continue", response="A normal response.")
    )
    assert decision.action is FinalizationAction.BLOCK
    assert decision.reason_code == "configuration_invalid"


def test_turn_start_activation_survives_project_policy_removal(tmp_path):
    policy = DesignCompletionPolicy(
        validator_path=tmp_path / "validator.py",
        validator_runner=lambda *_a, **_kw: SimpleNamespace(
            passed=False,
            reason_code="validator_nonzero_exit",
            exit_code=1,
            stdout="",
            stderr="missing artifacts",
            validator_sha256="a" * 64,
        ),
        receipt_verifier=lambda **_kw: False,
    )
    decision = policy.evaluate(
        _context(
            tmp_path,
            user="Continue",
            response="Here it is.",
            metadata={
                "active_policy_ids": ("design-completion",),
                "project_required_policy_ids_at_turn_start": ("design-completion",),
            },
        )
    )
    assert decision.action is FinalizationAction.BLOCK


def test_explicit_project_finalizing_mode_requires_trusted_runtime_receipt(tmp_path):
    (tmp_path / ".hermes").mkdir()
    (tmp_path / ".hermes" / "enforcement.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "required_policies": ["design-completion"],
                "design": {"applicable": True, "mode": "finalizing"},
            }
        ),
        encoding="utf-8",
    )
    report = tmp_path / "INDEPENDENT-REVIEW.md"
    report.write_text("review", encoding="utf-8")
    report_hash = hashlib.sha256(report.read_bytes()).hexdigest()
    (tmp_path / "REVIEW-RECEIPT.json").write_text(
        json.dumps({"subject_sha256": "c" * 64, "report_sha256": report_hash}),
        encoding="utf-8",
    )
    calls = []
    policy = DesignCompletionPolicy(
        validator_path=tmp_path / "validator.py",
        validator_runner=lambda *_a, **_kw: _pass_result(),
        receipt_verifier=lambda **kw: calls.append(kw) or True,
        subject_hasher=lambda *_args: "c" * 64,
    )
    decision = policy.evaluate(_context(tmp_path, response="A bounded answer."))
    assert decision.action is FinalizationAction.ALLOW
    assert decision.reason_code == "design_completion_passed"
    assert calls[0]["parent_session_id"] == "builder"
    assert calls[0]["subject_sha256"] == "c" * 64
    assert calls[0]["report_sha256"] == report_hash


def test_validator_pass_without_trusted_receipt_blocks(tmp_path):
    report = tmp_path / "INDEPENDENT-REVIEW.md"
    report.write_text("review", encoding="utf-8")
    (tmp_path / "REVIEW-RECEIPT.json").write_text(
        json.dumps(
            {
                "subject_sha256": "c" * 64,
                "report_sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
            }
        ),
        encoding="utf-8",
    )
    policy = DesignCompletionPolicy(
        validator_path=tmp_path / "validator.py",
        validator_runner=lambda *_a, **_kw: _pass_result(),
        receipt_verifier=lambda **_kw: False,
        subject_hasher=lambda *_args: "c" * 64,
    )
    decision = policy.evaluate(
        _context(tmp_path, response="The design is complete and delivered.")
    )
    assert decision.action is FinalizationAction.BLOCK
    assert decision.reason_code == "trusted_review_missing_or_stale"


def test_trusted_receipt_subject_must_match_live_subject_even_if_validator_claims_pass(tmp_path):
    report = tmp_path / "INDEPENDENT-REVIEW.md"
    report.write_text("review", encoding="utf-8")
    (tmp_path / "REVIEW-RECEIPT.json").write_text(
        json.dumps(
            {
                "subject_sha256": "c" * 64,
                "report_sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
            }
        ),
        encoding="utf-8",
    )
    policy = DesignCompletionPolicy(
        validator_path=tmp_path / "validator.py",
        validator_runner=lambda *_a, **_kw: _pass_result(),
        receipt_verifier=lambda **_kw: True,
        subject_hasher=lambda *_args: "d" * 64,
    )
    decision = policy.evaluate(
        _context(tmp_path, response="The design is complete and delivered.")
    )
    assert decision.action is FinalizationAction.BLOCK
    assert decision.reason_code == "trusted_review_missing_or_stale"
