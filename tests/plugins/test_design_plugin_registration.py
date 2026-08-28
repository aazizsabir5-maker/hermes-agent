from pathlib import Path

from hermes_cli.plugins import PluginContext, PluginManager, PluginManifest
from plugins.policies.design_enforcement import (
    decision_enforcement_enabled,
    enable_decision_enforcement,
    register,
)
from tools.registry import registry


def _context() -> tuple[PluginManager, PluginContext]:
    manager = PluginManager()
    manifest = PluginManifest(
        name="policies/design_enforcement",
        version="0.1.0",
        description="test",
        kind="backend",
        source="bundled",
        key="policies/design_enforcement",
        path=str(
            Path(__file__).resolve().parents[2]
            / "plugins"
            / "policies"
            / "design_enforcement"
        ),
    )
    return manager, PluginContext(manifest, manager)


def test_bundled_design_plugin_registers_one_policy_and_no_review_tool():
    manager, context = _context()
    register(context)

    policies = manager.iter_finalization_policies()
    assert len(policies) == 1
    assert policies[0].id == "design-completion"
    assert policies[0].required is True
    assert registry.get_entry("design_review_request") is None


def test_skill_prompt_is_launch_scoped_and_complete(monkeypatch):
    monkeypatch.setattr(
        "plugins.policies.design_enforcement._decision_enforced", False
    )
    manager, context = _context()
    register(context)

    assert decision_enforcement_enabled() is False
    inactive = manager.render_system_prompt_sections(
        {"session_id": "plain", "cwd": "/tmp"}
    )
    assert all(section.id != "design-enforcement.skill" for section in inactive)

    enable_decision_enforcement()
    rendered = manager.render_system_prompt_sections(
        {"session_id": "enforced", "cwd": "/tmp"}
    )
    combined = "\n".join(section.content for section in rendered)
    skill = (
        Path(__file__).resolve().parents[2]
        / "skills"
        / "design"
        / "comprehensive-designer-cognition"
        / "SKILL.md"
    ).read_text(encoding="utf-8")
    assert skill.rstrip() in combined
