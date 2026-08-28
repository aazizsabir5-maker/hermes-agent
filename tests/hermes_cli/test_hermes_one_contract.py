from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LAUNCHER = ROOT / "scripts" / "hermes-one"
FORK_EXECUTABLE = "/Users/ariansabir/Developer/hermes-agent-enforced/.venv/bin/hermes"


def _launcher_with_executable(tmp_path, executable: Path) -> Path:
    launcher = tmp_path / "hermes-one"
    launcher.write_text(
        LAUNCHER.read_text(encoding="utf-8").replace(FORK_EXECUTABLE, str(executable)),
        encoding="utf-8",
    )
    launcher.chmod(0o755)
    return launcher


def test_launcher_targets_fork_profile_and_internal_marker():
    text = LAUNCHER.read_text(encoding="utf-8")
    assert FORK_EXECUTABLE in text
    assert "--profile decision" in text
    assert "--decision-enforced" in text
    assert "enforcement.json" not in text


def test_launcher_forwards_arguments_from_any_writable_directory(tmp_path):
    fake = tmp_path / "fake-hermes"
    fake.write_text("#!/bin/sh\nprintf '%s\\n' \"$@\"\n", encoding="utf-8")
    fake.chmod(0o755)
    launcher = _launcher_with_executable(tmp_path, fake)

    completed = subprocess.run(
        [str(launcher), "--version"],
        cwd=tmp_path,
        env={"PATH": "/usr/bin:/bin"},
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
    launcher = _launcher_with_executable(tmp_path, missing)
    completed = subprocess.run(
        [str(launcher), "--version"],
        cwd=tmp_path,
        env={"PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
    )
    assert completed.returncode != 0
    assert "python -m venv /Users/ariansabir/Developer/hermes-agent-enforced/.venv" in completed.stderr
    assert "falling back" not in completed.stderr.lower()


def test_hidden_cli_marker_activates_decision_launch_context():
    from hermes_cli._parser import build_top_level_parser
    from plugins.policies import design_enforcement

    parser, _subparsers, _chat = build_top_level_parser()
    args = parser.parse_args(["--decision-enforced"])
    assert args.decision_enforced is True

    design_enforcement._decision_enforced = False
    from hermes_cli.main import _apply_decision_launch_marker

    _apply_decision_launch_marker(args)
    assert design_enforcement.decision_enforcement_enabled() is True


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
