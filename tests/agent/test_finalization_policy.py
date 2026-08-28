"""Generic completion-policy evaluation without provenance state."""

import time
from contextvars import ContextVar

from agent.finalization_policy import (
    FinalizationAction,
    FinalizationContext,
    FinalizationDecision,
    RegisteredFinalizationPolicy,
    evaluate_finalization_policies,
    policy_buffers_turn,
)


def _context(text="finished"):
    return FinalizationContext.for_response(
        session_id="session",
        task_id="task",
        turn_id="turn",
        platform="cli",
        model="provider/model",
        project_root="/tmp/project",
        user_message="finish the design",
        response_text=text,
        metadata={"active_policy_ids": ("decision",)},
    )


def _policy(callback, *, required=True, timeout=0.2):
    return RegisteredFinalizationPolicy(
        "decision", callback, required=required, timeout_seconds=timeout
    )


def _allow():
    return FinalizationDecision(FinalizationAction.ALLOW, "decision", "valid", "")


def test_context_contains_no_mode_hash_or_receipt_identity():
    context = _context()
    assert not hasattr(context, "mode")
    assert not hasattr(context, "response_sha256")
    assert not hasattr(context, "receipt")


def test_turn_predicate_scopes_policy_and_errors_fail_closed():
    scoped = _policy(lambda _context: _allow())
    scoped = RegisteredFinalizationPolicy(
        "decision", scoped.callback, turn_predicate=lambda _root, _message: False
    )
    assert policy_buffers_turn(scoped, "/tmp", "hello") == (False, None)
    broken = RegisteredFinalizationPolicy(
        "decision",
        lambda _context: _allow(),
        turn_predicate=lambda *_args: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    assert policy_buffers_turn(broken, "/tmp", "hello") == (
        True,
        "turn_predicate_error",
    )


def test_policy_thread_preserves_contextvars():
    value = ContextVar("value", default="none")
    token = value.set("profile")
    try:
        observed = []
        result = evaluate_finalization_policies(
            _context(), [_policy(lambda _context: observed.append(value.get()) or _allow())]
        )
        assert result.action is FinalizationAction.ALLOW
        assert observed == ["profile"]
    finally:
        value.reset(token)


def test_required_block_uses_specific_message():
    denial = FinalizationDecision(
        FinalizationAction.BLOCK,
        "decision",
        "missing_ledger",
        "This design is not yet complete. DESIGN-DECISIONS.md is missing",
    )
    result = evaluate_finalization_policies(_context(), [_policy(lambda _ctx: denial)])
    assert result.action is FinalizationAction.BLOCK
    assert result.user_message == denial.user_message


def test_required_exception_timeout_and_malformed_results_block():
    callbacks = [
        lambda _ctx: (_ for _ in ()).throw(RuntimeError("private detail")),
        lambda _ctx: None,
    ]
    for callback in callbacks:
        result = evaluate_finalization_policies(_context(), [_policy(callback)])
        assert result.action is FinalizationAction.BLOCK
        assert "private detail" not in result.user_message

    def slow(_context):
        time.sleep(1)
        return _allow()

    started = time.monotonic()
    result = evaluate_finalization_policies(
        _context(), [_policy(slow, timeout=0.02)]
    )
    assert time.monotonic() - started < 0.3
    assert result.action is FinalizationAction.BLOCK


def test_optional_failure_does_not_override_required_allow():
    optional = RegisteredFinalizationPolicy(
        "optional",
        lambda _ctx: (_ for _ in ()).throw(RuntimeError("boom")),
        required=False,
    )
    result = evaluate_finalization_policies(
        _context(), [_policy(lambda _ctx: _allow()), optional]
    )
    assert result.action is FinalizationAction.ALLOW


def test_no_policies_allows_ordinary_session():
    result = evaluate_finalization_policies(_context(), [])
    assert result.action is FinalizationAction.ALLOW
    assert result.decisions == ()
