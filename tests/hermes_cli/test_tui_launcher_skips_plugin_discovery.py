
"""Regression test: the TUI launcher must not spend time on plugin discovery.

`hermes --tui` just spawns a Node process; the spawned tui_gateway backend
performs its own plugin discovery. Running discover_plugins() in the
launcher added ~0.5s to every `hermes --tui` startup for work the backend
then redoes. Plain chat must still discover plugins.
"""

from __future__ import annotations

from argparse import Namespace
import os
import subprocess
import sys
import types

from hermes_cli import main as main_mod


def _install_discover_spy(monkeypatch):
    calls = []

    def _discover():
        calls.append("discover")

    monkeypatch.setitem(
        sys.modules,
        "hermes_cli.plugins",
        types.SimpleNamespace(
            discover_plugins=_discover,
            # main.py now kicks discovery off in a background thread; both
            # entry points count as "discovery work happened in the launcher".
            start_background_plugin_discovery=_discover,
        ),
    )
    return calls


def _args(**overrides):
    base = {
        "accept_hooks": False,
        "yolo": False,
        "safe_mode": False,
        "command": None,
        "query": None,
        "image": None,
    }
    base.update(overrides)
    return Namespace(**base)


def test_plugin_discovery_skipped_for_tui_launch(monkeypatch):
    calls = _install_discover_spy(monkeypatch)
    main_mod._prepare_agent_startup(_args(tui=True))
    assert calls == [], (
        "Plugin discovery must not run in the TUI launcher: the spawned "
        "tui_gateway backend discovers plugins itself."
    )


def test_plugin_discovery_runs_for_plain_chat(monkeypatch):
    calls = _install_discover_spy(monkeypatch)
    main_mod._prepare_agent_startup(_args(tui=False, command="chat"))
    assert calls == ["discover"]


def test_decision_launch_marker_reaches_the_tui_backend_child(monkeypatch):
    marker = "HERMES_INTERNAL_DECISION_ENFORCED"
    monkeypatch.delenv(marker, raising=False)
    _install_discover_spy(monkeypatch)

    main_mod._prepare_agent_startup(
        _args(tui=True, decision_enforced=True)
    )

    assert os.environ.get(marker) == "1"
    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            "from plugins.policies.design_enforcement import "
            "decision_enforcement_enabled; print(decision_enforcement_enabled())",
        ],
        cwd=main_mod.PROJECT_ROOT,
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        check=True,
    )
    assert completed.stdout.strip() == "True"
