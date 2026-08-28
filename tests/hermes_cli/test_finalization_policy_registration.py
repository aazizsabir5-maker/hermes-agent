"""Plugin registration contract for required finalization policies."""

from __future__ import annotations

import pytest

from agent.finalization_policy import FinalizationDecision
from hermes_cli.plugins import PluginContext, PluginManager, PluginManifest


def _context(manager: PluginManager, name: str = "policy-plugin") -> PluginContext:
    return PluginContext(PluginManifest(name=name, key=name), manager)


def test_plugin_can_register_and_dispose_finalization_policy():
    manager = PluginManager(scope_key="/tmp/finalization-policy-test")
    context = _context(manager)
    predicate = lambda _root, _message: True

    handle = context.register_finalization_policy(
        id="design-completion",
        callback=lambda _ctx: FinalizationDecision,
        required=True,
        timeout_seconds=12,
        turn_predicate=predicate,
    )

    policies = manager.iter_finalization_policies()
    assert len(policies) == 1
    assert policies[0].id == "design-completion"
    assert policies[0].owner == "policy-plugin"
    assert policies[0].required is True
    assert policies[0].timeout_seconds == 12
    assert policies[0].turn_predicate is predicate

    handle.dispose()
    assert manager.iter_finalization_policies() == ()


def test_duplicate_policy_id_is_rejected_without_replacing_owner():
    manager = PluginManager(scope_key="/tmp/finalization-policy-test")
    first = _context(manager, "first")
    second = _context(manager, "second")
    first.register_finalization_policy(id="same", callback=lambda _ctx: None)

    with pytest.raises(ValueError, match="already registered"):
        second.register_finalization_policy(id="same", callback=lambda _ctx: None)

    assert manager.iter_finalization_policies()[0].owner == "first"


@pytest.mark.parametrize("policy_id", ["", "UPPER", "spaces are bad", "../escape"])
def test_policy_id_validation(policy_id):
    manager = PluginManager(scope_key="/tmp/finalization-policy-test")
    with pytest.raises(ValueError):
        _context(manager).register_finalization_policy(id=policy_id, callback=lambda _ctx: None)


def test_registration_rejects_bad_callback_and_timeout():
    manager = PluginManager(scope_key="/tmp/finalization-policy-test")
    context = _context(manager)
    with pytest.raises(TypeError):
        context.register_finalization_policy(id="bad-callback", callback=None)
    with pytest.raises(ValueError):
        context.register_finalization_policy(
            id="bad-timeout", callback=lambda _ctx: None, timeout_seconds=0
        )


def test_policy_snapshot_is_registration_order():
    manager = PluginManager(scope_key="/tmp/finalization-policy-test")
    context = _context(manager)
    context.register_finalization_policy(id="first", callback=lambda _ctx: None)
    context.register_finalization_policy(id="second", callback=lambda _ctx: None)
    assert [item.id for item in manager.iter_finalization_policies()] == ["first", "second"]
