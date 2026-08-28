import json
from types import SimpleNamespace

from plugins.policies.design_enforcement.receipt import TrustedReceiptStore
from plugins.policies.design_enforcement.reviewer import ReviewOrchestrator


class FakeLifecycle:
    def __init__(self, subject):
        self.subject = subject
        self.requests = []
        self.handle = SimpleNamespace(
            subagent_id="reviewer-runtime-1",
            parent_session_id="builder-1",
            provider="provider",
            model="review-model",
        )

    def launch(self, request):
        self.requests.append(request)
        return self.handle

    def wait(self, handle, *, timeout_seconds=None):
        assert handle is self.handle
        return SimpleNamespace(completed=True, timed_out=False, state="SUCCEEDED")

    def result(self, handle):
        return SimpleNamespace(
            ready=True,
            terminal_state="SUCCEEDED",
            summary=json.dumps(
                {
                    "schema_version": 1,
                    "subject_sha256": self.subject,
                    "disposition": "pass",
                    "blocking_findings": [],
                    "non_blocking_findings": ["Monitor the rollout."],
                    "evidence_reviewed": ["DESIGN-BRIEF.md"],
                }
            ),
            result_hash="d" * 64,
        )


def test_review_uses_runtime_child_identity_and_issues_both_receipts(tmp_path):
    subject = "c" * 64
    project = tmp_path / "project"
    project.mkdir()
    (project / "DESIGN-BRIEF.md").write_text("brief", encoding="utf-8")
    (project / "DESIGN-COMPLETION.json").write_text(
        json.dumps({"artifacts": {"brief": "DESIGN-BRIEF.md"}, "gates": {}}),
        encoding="utf-8",
    )
    lifecycle = FakeLifecycle(subject)
    store = TrustedReceiptStore(tmp_path / "trusted", secret=b"k" * 32)
    reviewer = ReviewOrchestrator(
        lifecycle=lifecycle,
        validator_path=tmp_path / "validator.py",
        receipt_store=store,
        snapshot_root=tmp_path / "snapshots",
        subject_hasher=lambda _root: subject,
    )

    result = reviewer.run(
        project,
        parent_session_id="builder-1",
        reviewer_model="review-model",
        timeout_seconds=2,
    )

    assert result.passed is True
    request = lifecycle.requests[0]
    assert request.parent_session_id == "builder-1"
    assert request.allowed_toolsets == ("file-readonly",)
    assert request.blocked_tools == ()
    assert request.timeout_seconds is None
    assert request.working_directory != str(project)
    report = (project / "INDEPENDENT-REVIEW.md").read_text(encoding="utf-8")
    assert "Reviewer session: reviewer-runtime-1" in report
    local = json.loads((project / "REVIEW-RECEIPT.json").read_text(encoding="utf-8"))
    assert local["reviewer"]["session_id"] == "reviewer-runtime-1"
    assert local["reviewer"]["model"] == "review-model"
    trusted = store.find(parent_session_id="builder-1", subject_sha256=subject)
    assert store.verify(
        trusted,
        parent_session_id="builder-1",
        subject_sha256=subject,
        report_sha256=local["report_sha256"],
    )


def test_self_review_or_nonpass_child_is_rejected(tmp_path):
    subject = "c" * 64
    project = tmp_path / "project"
    project.mkdir()
    (project / "a.md").write_text("a", encoding="utf-8")
    (project / "DESIGN-COMPLETION.json").write_text(
        json.dumps({"artifacts": {"a": "a.md"}, "gates": {}}),
        encoding="utf-8",
    )
    lifecycle = FakeLifecycle(subject)
    lifecycle.handle.subagent_id = "builder-1"
    reviewer = ReviewOrchestrator(
        lifecycle=lifecycle,
        validator_path=tmp_path / "validator.py",
        receipt_store=TrustedReceiptStore(tmp_path / "trusted", secret=b"k" * 32),
        snapshot_root=tmp_path / "snapshots",
        subject_hasher=lambda _root: subject,
    )
    result = reviewer.run(project, parent_session_id="builder-1", reviewer_model="m")
    assert result.passed is False
    assert result.reason_code == "reviewer_not_independent"
    assert not (project / "REVIEW-RECEIPT.json").exists()


def test_subject_mutation_during_snapshot_blocks_before_reviewer_launch(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "a.md").write_text("a", encoding="utf-8")
    (project / "DESIGN-COMPLETION.json").write_text(
        json.dumps({"artifacts": {"a": "a.md"}, "gates": {}}),
        encoding="utf-8",
    )
    lifecycle = FakeLifecycle("a" * 64)
    hashes = iter(("a" * 64, "b" * 64))
    reviewer = ReviewOrchestrator(
        lifecycle=lifecycle,
        validator_path=tmp_path / "validator.py",
        receipt_store=TrustedReceiptStore(tmp_path / "trusted", secret=b"k" * 32),
        snapshot_root=tmp_path / "snapshots",
        subject_hasher=lambda _root: next(hashes),
    )

    result = reviewer.run(project, parent_session_id="builder-1", reviewer_model="m")

    assert result.passed is False
    assert result.reason_code == "review_subject_changed_during_snapshot"
    assert lifecycle.requests == []
