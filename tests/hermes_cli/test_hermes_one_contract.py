from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LAUNCHER = ROOT / "scripts" / "hermes-one"


def test_launcher_targets_fork_profile_and_internal_marker():
    text = LAUNCHER.read_text(encoding="utf-8")
    assert "/Users/ariansabir/Developer/hermes-agent-enforced/.venv/bin/hermes" in text
    assert "--profile decision" in text
    assert "--decision-enforced" in text
    assert "enforcement.json" not in text


def test_launcher_forwards_arguments_from_any_writable_directory(tmp_path):
    fake = tmp_path / "fake-hermes"
    fake.write_text("#!/bin/sh\nprintf '%s\\n' \"$@\"\n", encoding="utf-8")
    fake.chmod(0o755)

    completed = subprocess.run(
        [str(LAUNCHER), "--version"],
        cwd=tmp_path,
        env={"PATH": "/usr/bin:/bin", "HERMES_ONE_EXECUTABLE": str(fake)},
        capture_output=True,
        text=True,
        check=True,
    )
    assert completed.stdout.splitlines() == [
        "--profile",
        "decision",
        "--decision-enforced",
        "--version",
    ]


def test_launcher_failure_has_one_copyable_repair_command(tmp_path):
    missing = tmp_path / "missing-hermes"
    completed = subprocess.run(
        [str(LAUNCHER), "--version"],
        cwd=tmp_path,
        env={"PATH": "/usr/bin:/bin", "HERMES_ONE_EXECUTABLE": str(missing)},
        capture_output=True,
        text=True,
    )
    assert completed.returncode != 0
    assert "python -m venv /Users/ariansabir/Developer/hermes-agent-enforced/.venv" in completed.stderr
    assert "falling back" not in completed.stderr.lower()


def test_policy_prompt_has_no_user_managed_lifecycle(monkeypatch):
    import plugins.policies.design_enforcement as plugin

    registered = {}

    class Context:
        def register_finalization_policy(self, **kwargs):
            registered["policy"] = kwargs

        def register_system_prompt_section(self, section_id, callback, **kwargs):
            registered["section_id"] = section_id
            registered["prompt"] = callback(
                {"decision_enforced": "true", "active_finalization_policy_ids": "design-completion"}
            )

        def register_tool(self, **kwargs):
            raise AssertionError("lean policy must not register a review lifecycle tool")

    monkeypatch.setattr(plugin, "decision_enforcement_enabled", lambda: True)
    plugin.register(Context())

    prompt = registered["prompt"].lower()
    assert "comprehensive" in prompt
    for forbidden in (
        "working mode",
        "finalizing mode",
        "design_review_request",
        "review receipt",
        "reviewer session",
        "immutable snapshot",
    ):
        assert forbidden not in prompt

