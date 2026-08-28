"""Behavior contract for fail-closed required finalization policies."""

from __future__ import annotations

import hashlib
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


def _context(text: str = "finished") -> FinalizationContext:
    return FinalizationContext.for_response(
        session_id="session-1",
        task_id="task-1",
        turn_id="turn-1",
        platform="cli",
        model="provider/model",
        project_root="/tmp/project",
        user_message="build it",
        response_text=text,
        changed_paths=("DESIGN-BRIEF.md",),
        loaded_skills=("comprehensive-designer-cognition",),
        mode="finalizing",
    )


def _policy(policy_id: str, callback, *, required: bool = True, timeout: float = 0.2):
    return RegisteredFinalizationPolicy(
        id=policy_id,
        callback=callback,
        required=required,
        timeout_seconds=timeout,
        owner="test-plugin",
    )


def _allow(policy_id: str):
    return FinalizationDecision(
        action=FinalizationAction.ALLOW,
        policy_id=policy_id,
        reason_code="passed",
        user_message="",
        evidence={"validator_exit_code": 0},
    )


def test_context_hashes_exact_response_bytes():
    context = _context("café")
    assert context.response_sha256 == hashlib.sha256("café".encode("utf-8")).hexdigest()


def test_policy_timeout_thread_preserves_profile_contextvars():
    active_home = ContextVar("active_home", default="default")
    token = active_home.set("profile-home")
    try:
        observed = []

        def callback(_context):
            observed.append(active_home.get())
            return FinalizationDecision(
                FinalizationAction.ALLOW, "profile-aware", "ok", ""
            )

        result = evaluate_finalization_policies(
            _context(),
            [RegisteredFinalizationPolicy("profile-aware", callback)],
        )
        assert result.action is FinalizationAction.ALLOW
        assert observed == ["profile-home"]
    finally:
        active_home.reset(token)


def test_turn_predicate_scopes_buffering_and_fails_closed():
    scoped_out = RegisteredFinalizationPolicy(
        "scoped",
        lambda _context: _allow("scoped"),
        turn_predicate=lambda _root, _message: False,
    )
    assert policy_buffers_turn(scoped_out, "/tmp", "hello") == (False, None)

    required_broken = RegisteredFinalizationPolicy(
        "required-broken",
        lambda _context: _allow("required-broken"),
        required=True,
        turn_predicate=lambda *_args: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    applies, error = policy_buffers_turn(required_broken, "/tmp", "hello")
    assert applies is True
    assert error == "turn_predicate_error"

    optional_broken = RegisteredFinalizationPolicy(
        "optional-broken",
        lambda _context: _allow("optional-broken"),
        required=False,
        turn_predicate=required_broken.turn_predicate,
    )
    assert policy_buffers_turn(optional_broken, "/tmp", "hello") == (
        False,
        "turn_predicate_error",
    )


def test_all_required_policies_must_allow():
    result = evaluate_finalization_policies(
        _context(),
        [_policy("one", lambda _ctx: _allow("one")), _policy("two", lambda _ctx: _allow("two"))],
    )
    assert result.action is FinalizationAction.ALLOW
    assert [item.policy_id for item in result.decisions] == ["one", "two"]


def test_single_required_block_wins_over_other_allows():
    denial = FinalizationDecision(
        action=FinalizationAction.BLOCK,
        policy_id="deny",
        reason_code="validator_failed",
        user_message="Final delivery blocked: validator failed.",
    )
    result = evaluate_finalization_policies(
        _context(),
        [_policy("allow", lambda _ctx: _allow("allow")), _policy("deny", lambda _ctx: denial)],
    )
    assert result.action is FinalizationAction.BLOCK
    assert result.user_message == denial.user_message


def test_required_policy_exception_blocks_without_exposing_exception_text():
    def explode(_ctx):
        raise RuntimeError("secret callback detail")

    result = evaluate_finalization_policies(_context(), [_policy("broken", explode)])
    assert result.action is FinalizationAction.BLOCK
    assert result.reason_code == "required_policy_error"
    assert "secret callback detail" not in result.user_message


def test_required_policy_timeout_blocks_promptly():
    def slow(_ctx):
        time.sleep(1)
        return _allow("slow")

    started = time.monotonic()
    result = evaluate_finalization_policies(_context(), [_policy("slow", slow, timeout=0.02)])
    assert time.monotonic() - started < 0.3
    assert result.action is FinalizationAction.BLOCK
    assert result.reason_code == "required_policy_timeout"


def test_required_policy_none_or_malformed_result_blocks():
    for callback in (lambda _ctx: None, lambda _ctx: {"action": "allow"}):
        result = evaluate_finalization_policies(_context(), [_policy("malformed", callback)])
        assert result.action is FinalizationAction.BLOCK
        assert result.reason_code == "required_policy_malformed"


def test_policy_cannot_report_another_policy_identity():
    result = evaluate_finalization_policies(
        _context(),
        [_policy("expected", lambda _ctx: _allow("different"))],
    )
    assert result.action is FinalizationAction.BLOCK
    assert result.reason_code == "required_policy_malformed"


def test_non_json_or_oversized_evidence_blocks_required_policy():
    non_json = FinalizationDecision(
        action=FinalizationAction.ALLOW,
        policy_id="bad",
        reason_code="passed",
        user_message="",
        evidence={"not_json": object()},
    )
    huge = FinalizationDecision(
        action=FinalizationAction.ALLOW,
        policy_id="huge",
        reason_code="passed",
        user_message="",
        evidence={"payload": "x" * 512},
    )
    result = evaluate_finalization_policies(
        _context(), [_policy("bad", lambda _ctx: non_json)], max_evidence_bytes=128
    )
    assert result.action is FinalizationAction.BLOCK
    result = evaluate_finalization_policies(
        _context(), [_policy("huge", lambda _ctx: huge)], max_evidence_bytes=128
    )
    assert result.action is FinalizationAction.BLOCK


def test_optional_policy_failure_does_not_override_required_allow():
    result = evaluate_finalization_policies(
        _context(),
        [
            _policy("required", lambda _ctx: _allow("required")),
            _policy("optional", lambda _ctx: (_ for _ in ()).throw(RuntimeError("boom")), required=False),
        ],
    )
    assert result.action is FinalizationAction.ALLOW
    assert result.decisions[1].reason_code == "optional_policy_error"


def test_no_policies_is_allow_for_unprotected_sessions():
    result = evaluate_finalization_policies(_context(), [])
    assert result.action is FinalizationAction.ALLOW
    assert result.decisions == ()
