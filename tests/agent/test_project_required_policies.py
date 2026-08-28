import json

import pytest

from agent.finalization_policy import (
    ProjectPolicyRequirementError,
    project_required_policy_ids,
)


def test_project_required_policy_ids_are_strict_and_deduplicated(tmp_path):
    config_dir = tmp_path / ".hermes"
    config_dir.mkdir()
    (config_dir / "enforcement.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "required_policies": ["design-completion", "other.policy"],
                "design": {"applicable": True, "mode": "working"},
            }
        ),
        encoding="utf-8",
    )
    assert project_required_policy_ids(tmp_path) == (
        "design-completion",
        "other.policy",
    )


def test_absent_config_has_no_requirement(tmp_path):
    assert project_required_policy_ids(tmp_path) == ()


def test_malformed_duplicate_or_symlinked_config_fails_closed(tmp_path):
    config_dir = tmp_path / ".hermes"
    config_dir.mkdir()
    config = config_dir / "enforcement.json"
    config.write_text('{"schema_version":1,"schema_version":1,"required_policies":[]}', encoding="utf-8")
    with pytest.raises(ProjectPolicyRequirementError):
        project_required_policy_ids(tmp_path)

    config.unlink()
    target = tmp_path / "outside.json"
    target.write_text('{"schema_version":1,"required_policies":[]}', encoding="utf-8")
    config.symlink_to(target)
    with pytest.raises(ProjectPolicyRequirementError):
        project_required_policy_ids(tmp_path)
