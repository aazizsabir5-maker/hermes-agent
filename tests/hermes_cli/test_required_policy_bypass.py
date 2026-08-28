import json
from types import SimpleNamespace

import pytest

from hermes_cli.main import _reject_required_policy_bypass


def test_safe_mode_and_ignore_rules_are_refused_for_enforced_project(tmp_path):
    (tmp_path / ".hermes").mkdir()
    (tmp_path / ".hermes" / "enforcement.json").write_text(
        json.dumps(
            {"schema_version": 1, "required_policies": ["design-completion"]}
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="cannot use --safe-mode"):
        _reject_required_policy_bypass(
            SimpleNamespace(safe_mode=True, ignore_rules=True), tmp_path
        )
    with pytest.raises(ValueError, match="cannot use --ignore-rules"):
        _reject_required_policy_bypass(
            SimpleNamespace(safe_mode=False, ignore_rules=True), tmp_path
        )


def test_bypass_flags_are_unchanged_outside_enforced_projects(tmp_path):
    _reject_required_policy_bypass(
        SimpleNamespace(safe_mode=True, ignore_rules=True), tmp_path
    )
