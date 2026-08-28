from pathlib import Path

from hermes_cli.plugins import PluginContext, PluginManager, PluginManifest
from plugins.policies.design_enforcement import register
from tools.registry import registry


def test_bundled_design_plugin_registers_required_policy_tool_and_full_skill(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "plugins.policies.design_enforcement.get_hermes_home", lambda: tmp_path / "home"
    )
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
    context = PluginContext(manifest, manager)
    try:
        register(context)
        policies = manager.iter_finalization_policies()
        assert len(policies) == 1
        assert policies[0].id == "design-completion"
        assert policies[0].required is True
        assert registry.get_entry("design_review_request") is not None

        rendered = manager.render_system_prompt_sections(
            {
                "session_id": "s",
                "cwd": str(tmp_path),
                "active_finalization_policy_ids": "design-completion",
            }
        )
        combined = "\n".join(section.content for section in rendered)
        skill = (
            Path(__file__).resolve().parents[2]
            / "skills"
            / "design"
            / "comprehensive-designer-cognition"
            / "SKILL.md"
        ).read_text(encoding="utf-8")
        assert skill[:500] in combined
        assert skill[-500:] in combined
        inactive = manager.render_system_prompt_sections(
            {"session_id": "other", "cwd": str(tmp_path)}
        )
        assert all(section.id != "design-enforcement.skill" for section in inactive)
    finally:
        # Per-file test subprocess isolation tears down the registry.
        pass
