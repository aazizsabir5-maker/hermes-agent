from hermes_cli.plugins import (
    PluginContext,
    PluginManager,
    PluginManifest,
    _record_manifest_winner,
)


def _manifest(source: str):
    return PluginManifest(
        name="design_enforcement",
        version="1.0.0",
        description="test",
        kind="backend",
        source=source,
        key="policies/design_enforcement",
        path=f"/tmp/{source}/policies/design_enforcement",
    )


def test_non_bundled_manifest_cannot_shadow_trusted_policy_key():
    winners = {}
    bundled = _manifest("bundled")
    _record_manifest_winner(winners, bundled)
    _record_manifest_winner(winners, _manifest("user"))
    _record_manifest_winner(winners, _manifest("project"))

    assert winners["policies/design_enforcement"] is bundled


def test_public_unload_cannot_remove_trusted_policy_registration(tmp_path):
    from agent.finalization_policy import FinalizationAction, FinalizationDecision

    manager = PluginManager(scope_key=str(tmp_path))
    context = PluginContext(_manifest("bundled"), manager)
    context.register_finalization_policy(
        id="design-completion",
        callback=lambda _ctx: FinalizationDecision(
            action=FinalizationAction.ALLOW,
            policy_id="design-completion",
            reason_code="ok",
            user_message="",
        ),
    )

    assert manager.unload("policies/design_enforcement") is False
    policies = manager.iter_finalization_policies()
    assert [policy.id for policy in policies] == ["design-completion"]
