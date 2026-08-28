from types import SimpleNamespace

import pytest

from agent.finalization_policy import (
    FinalizationAction,
    FinalizationDecision,
    RegisteredFinalizationPolicy,
)
from gateway.run import GatewayRunner


@pytest.mark.asyncio
async def test_proxy_refuses_to_stream_when_required_policy_applies(monkeypatch):
    policy = RegisteredFinalizationPolicy(
        "design-completion",
        lambda _context: FinalizationDecision(
            FinalizationAction.ALLOW,
            "design-completion",
            "unused",
            "",
        ),
        required=True,
        turn_predicate=lambda _root, message: "design" in str(message).lower(),
    )
    manager = SimpleNamespace(iter_finalization_policies=lambda: (policy,))
    monkeypatch.setattr("hermes_cli.plugins.get_plugin_manager", lambda: manager)

    result = await GatewayRunner._run_agent_via_proxy(
        SimpleNamespace(),
        message="Design a checkout page",
        context_prompt="",
        history=[],
        source=SimpleNamespace(),
        session_id="session",
    )

    assert result["failed"] is True
    assert result["finalization"]["reason_code"] == "untrusted_remote_execution"
    assert "checkout" not in result["final_response"].lower()
