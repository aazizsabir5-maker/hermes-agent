import json
from pathlib import Path

from plugins.policies.design_enforcement.receipt import TrustedReceiptStore


def test_runtime_receipt_binds_subject_report_parent_and_reviewer(tmp_path):
    store = TrustedReceiptStore(tmp_path / "trusted", secret=b"k" * 32)
    receipt = store.issue(
        parent_session_id="builder-1",
        reviewer_session_id="reviewer-9",
        reviewer_model="provider/model",
        subject_sha256="a" * 64,
        report_sha256="b" * 64,
        disposition="pass",
    )
    assert store.verify(
        receipt,
        parent_session_id="builder-1",
        subject_sha256="a" * 64,
        report_sha256="b" * 64,
    ) is True
    assert store.verify(
        receipt,
        parent_session_id="other",
        subject_sha256="a" * 64,
        report_sha256="b" * 64,
    ) is False
    assert store.verify(
        receipt,
        parent_session_id="builder-1",
        subject_sha256="c" * 64,
        report_sha256="b" * 64,
    ) is False


def test_tampering_or_new_runtime_secret_invalidates_receipt(tmp_path):
    store = TrustedReceiptStore(tmp_path / "trusted", secret=b"k" * 32)
    path = store.issue(
        parent_session_id="builder-1",
        reviewer_session_id="reviewer-9",
        reviewer_model="provider/model",
        subject_sha256="a" * 64,
        report_sha256="b" * 64,
        disposition="pass",
    )
    data = json.loads(path.read_text(encoding="utf-8"))
    data["reviewer_session_id"] = "forged"
    path.write_text(json.dumps(data), encoding="utf-8")
    assert store.verify(
        path,
        parent_session_id="builder-1",
        subject_sha256="a" * 64,
        report_sha256="b" * 64,
    ) is False

    other = TrustedReceiptStore(tmp_path / "trusted", secret=b"z" * 32)
    assert other.verify(
        path,
        parent_session_id="builder-1",
        subject_sha256="a" * 64,
        report_sha256="b" * 64,
    ) is False


def test_builder_and_reviewer_must_differ(tmp_path):
    store = TrustedReceiptStore(tmp_path / "trusted", secret=b"k" * 32)
    try:
        store.issue(
            parent_session_id="same",
            reviewer_session_id="same",
            reviewer_model="provider/model",
            subject_sha256="a" * 64,
            report_sha256="b" * 64,
            disposition="pass",
        )
    except ValueError as exc:
        assert "differ" in str(exc)
    else:
        raise AssertionError("self-review receipt was issued")


def test_receipt_parent_session_cannot_escape_store_root(tmp_path):
    store = TrustedReceiptStore(tmp_path / "trusted", secret=b"k" * 32)
    try:
        store.issue(
            parent_session_id="../../escape",
            reviewer_session_id="reviewer",
            reviewer_model="model",
            subject_sha256="a" * 64,
            report_sha256="b" * 64,
            disposition="pass",
        )
    except ValueError as exc:
        assert "session" in str(exc)
    else:
        raise AssertionError("path-traversing parent session was accepted")
