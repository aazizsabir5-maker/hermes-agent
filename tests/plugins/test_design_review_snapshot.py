from pathlib import Path

import pytest

import json

from plugins.policies.design_enforcement.review_snapshot import (
    collect_design_subject_paths,
    compute_snapshot_hash,
    create_review_snapshot,
)


def test_snapshot_is_content_addressed_and_read_only(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "DESIGN-BRIEF.md").write_text("brief", encoding="utf-8")
    (project / "nested").mkdir()
    (project / "nested" / "evidence.txt").write_text("proof", encoding="utf-8")
    destination = tmp_path / "snapshots"

    snapshot = create_review_snapshot(project, destination)
    assert len(snapshot.subject_sha256) == 64
    assert (snapshot.path / "DESIGN-BRIEF.md").read_text(encoding="utf-8") == "brief"
    assert snapshot.file_count == 2
    assert (snapshot.path / "DESIGN-BRIEF.md").stat().st_mode & 0o222 == 0


def test_snapshot_hash_changes_with_subject_and_rejects_symlinks(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    artifact = project / "artifact.md"
    artifact.write_text("one", encoding="utf-8")
    destination = tmp_path / "snapshots"
    first = create_review_snapshot(project, destination)
    artifact.write_text("two", encoding="utf-8")
    second = create_review_snapshot(project, destination)
    assert first.subject_sha256 != second.subject_sha256
    assert compute_snapshot_hash(first.path) == first.subject_sha256
    assert compute_snapshot_hash(second.path) == second.subject_sha256

    (project / "alias.md").symlink_to(artifact)
    with pytest.raises(ValueError, match="symlink"):
        create_review_snapshot(project, destination)


def test_design_subject_snapshot_excludes_unreferenced_secrets(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / ".env").write_text("SECRET=never-copy", encoding="utf-8")
    (project / "brief.md").write_text("brief", encoding="utf-8")
    (project / "evidence.md").write_text("evidence", encoding="utf-8")
    manifest = {
        "artifacts": {"brief": "brief.md"},
        "gates": {
            "validation": {
                "evidence": [{"path": "evidence.md"}],
            }
        },
    }
    (project / "DESIGN-COMPLETION.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    paths = collect_design_subject_paths(project)
    snapshot = create_review_snapshot(
        project, tmp_path / "snapshots", include_paths=paths
    )
    assert not (snapshot.path / ".env").exists()
    assert (snapshot.path / "DESIGN-COMPLETION.json").is_file()
    assert (snapshot.path / "brief.md").is_file()
    assert (snapshot.path / "evidence.md").is_file()


def test_declared_sensitive_credential_paths_are_rejected(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / ".env").write_text("TOKEN=secret", encoding="utf-8")
    (project / "DESIGN-COMPLETION.json").write_text(
        json.dumps({"artifacts": {"brief": ".env"}, "gates": {}}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="sensitive"):
        collect_design_subject_paths(project)
