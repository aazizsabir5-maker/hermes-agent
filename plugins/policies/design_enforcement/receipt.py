"""Process-trusted review receipts bound to runtime child provenance."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from utils import atomic_json_write


_PROCESS_SECRET = secrets.token_bytes(32)
_SESSION_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$")


def _strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate receipt member: {key}")
        result[key] = value
    return result


def _canonical(data: dict[str, Any]) -> bytes:
    return json.dumps(
        data,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


class TrustedReceiptStore:
    """Issue HMAC receipts that normal builder subprocesses cannot forge.

    The default key is process-local by design.  Receipts therefore expire on
    host restart and a fresh independent review is required; no signing key is
    exposed through environment variables or the model's file tools.
    """

    def __init__(self, root: str | Path, *, secret: bytes | None = None):
        self.root = Path(root).expanduser().resolve(strict=False)
        self._secret = bytes(secret if secret is not None else _PROCESS_SECRET)
        if len(self._secret) < 32:
            raise ValueError("trusted receipt secret must be at least 32 bytes")

    def _sign(self, payload: dict[str, Any]) -> str:
        return hmac.new(self._secret, _canonical(payload), hashlib.sha256).hexdigest()

    def issue(
        self,
        *,
        parent_session_id: str,
        reviewer_session_id: str,
        reviewer_model: str,
        subject_sha256: str,
        report_sha256: str,
        disposition: str,
    ) -> Path:
        if not parent_session_id or not reviewer_session_id:
            raise ValueError("builder and reviewer session ids are required")
        if not _SESSION_ID_RE.fullmatch(parent_session_id) or not _SESSION_ID_RE.fullmatch(
            reviewer_session_id
        ):
            raise ValueError("builder and reviewer session ids are invalid")
        if hmac.compare_digest(parent_session_id, reviewer_session_id):
            raise ValueError("builder and reviewer session ids must differ")
        for name, digest in (
            ("subject_sha256", subject_sha256),
            ("report_sha256", report_sha256),
        ):
            if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
                raise ValueError(f"{name} must be a lowercase SHA-256 digest")
        if disposition != "pass":
            raise ValueError("trusted completion receipts require disposition pass")
        payload = {
            "schema_version": 1,
            "parent_session_id": parent_session_id,
            "reviewer_session_id": reviewer_session_id,
            "reviewer_model": reviewer_model,
            "subject_sha256": subject_sha256,
            "report_sha256": report_sha256,
            "disposition": disposition,
            "issued_at": datetime.now(timezone.utc).isoformat(),
            "nonce": secrets.token_hex(16),
        }
        receipt = dict(payload)
        receipt["signature"] = self._sign(payload)
        receipt_id = hashlib.sha256(
            f"{parent_session_id}\0{subject_sha256}".encode("utf-8")
        ).hexdigest()
        destination = self.root / parent_session_id / f"{receipt_id}.json"
        destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        atomic_json_write(destination, receipt, mode=0o600)
        return destination

    def find(self, *, parent_session_id: str, subject_sha256: str) -> Path:
        if not _SESSION_ID_RE.fullmatch(parent_session_id):
            raise ValueError("parent session id is invalid")
        receipt_id = hashlib.sha256(
            f"{parent_session_id}\0{subject_sha256}".encode("utf-8")
        ).hexdigest()
        return self.root / parent_session_id / f"{receipt_id}.json"

    def verify(
        self,
        receipt_path: str | Path,
        *,
        parent_session_id: str,
        subject_sha256: str,
        report_sha256: str,
    ) -> bool:
        try:
            path = Path(receipt_path).expanduser().resolve(strict=True)
            path.relative_to(self.root)
            data = json.loads(
                path.read_text(encoding="utf-8"),
                object_pairs_hook=_strict_object,
                parse_constant=lambda value: (_ for _ in ()).throw(
                    ValueError(f"non-finite value: {value}")
                ),
            )
            if not isinstance(data, dict):
                return False
            signature = data.pop("signature", None)
            if not isinstance(signature, str) or not hmac.compare_digest(
                signature, self._sign(data)
            ):
                return False
            return (
                data.get("schema_version") == 1
                and data.get("disposition") == "pass"
                and hmac.compare_digest(
                    str(data.get("parent_session_id", "")), parent_session_id
                )
                and str(data.get("reviewer_session_id", "")) != parent_session_id
                and hmac.compare_digest(
                    str(data.get("subject_sha256", "")), subject_sha256
                )
                and hmac.compare_digest(
                    str(data.get("report_sha256", "")), report_sha256
                )
            )
        except (OSError, ValueError, TypeError, UnicodeError, json.JSONDecodeError):
            return False
