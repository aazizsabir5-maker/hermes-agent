"""Immutable, content-addressed snapshots for independent review."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path


_SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache"}
_SENSITIVE_COMPONENTS = {".ssh", ".aws", ".gnupg", ".kube"}
_SENSITIVE_NAMES = {
    ".env",
    ".netrc",
    "auth.json",
    "credentials",
    "credentials.json",
    "secrets.json",
}
_SENSITIVE_SUFFIXES = {".key", ".pem", ".p12", ".pfx"}


@dataclass(frozen=True)
class ReviewSnapshot:
    path: Path
    subject_sha256: str
    file_count: int
    total_bytes: int


def compute_snapshot_hash(path: str | Path) -> str:
    """Recompute the canonical hash of an already-materialized snapshot."""
    root = Path(path).resolve(strict=True)
    digest = hashlib.sha256()
    for candidate in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = candidate.relative_to(root).as_posix()
        encoded_path = relative.encode("utf-8")
        payload = candidate.read_bytes()
        digest.update(len(encoded_path).to_bytes(8, "big"))
        digest.update(encoded_path)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(hashlib.sha256(payload).digest())
    return digest.hexdigest()


def collect_design_subject_paths(project_root: str | Path) -> tuple[str, ...]:
    """Return only manifest, artifact, evidence, and attachment paths.

    This mirrors the standalone validator's subject inputs and deliberately
    excludes unrelated project files such as ``.env`` and credentials.
    """

    root = Path(project_root).expanduser().resolve(strict=True)
    manifest_path = root / "DESIGN-COMPLETION.json"

    def strict_pairs(pairs):
        data = {}
        for key, value in pairs:
            if key in data:
                raise ValueError(f"duplicate manifest member: {key}")
            data[key] = value
        return data

    data = json.loads(
        manifest_path.read_text(encoding="utf-8"),
        object_pairs_hook=strict_pairs,
        parse_constant=lambda item: (_ for _ in ()).throw(
            ValueError(f"non-finite manifest value: {item}")
        ),
    )
    if not isinstance(data, dict):
        raise ValueError("design completion manifest must be an object")
    paths = {"DESIGN-COMPLETION.json"}
    artifacts = data.get("artifacts")
    if isinstance(artifacts, dict):
        paths.update(value for value in artifacts.values() if isinstance(value, str))
    gates = data.get("gates")
    if isinstance(gates, dict):
        for name, gate in gates.items():
            if name == "independent_review" or not isinstance(gate, dict):
                continue
            evidence = gate.get("evidence")
            if not isinstance(evidence, list):
                continue
            for reference in evidence:
                if not isinstance(reference, dict):
                    continue
                path = reference.get("path")
                if isinstance(path, str):
                    paths.add(path)
                attachment = reference.get("attachment")
                if isinstance(attachment, dict) and isinstance(
                    attachment.get("path"), str
                ):
                    paths.add(attachment["path"])
    for raw_path in paths:
        candidate = Path(raw_path)
        lowered_parts = {part.lower() for part in candidate.parts}
        name = candidate.name.lower()
        if (
            lowered_parts & _SENSITIVE_COMPONENTS
            or name in _SENSITIVE_NAMES
            or candidate.suffix.lower() in _SENSITIVE_SUFFIXES
        ):
            raise ValueError(f"design subject references sensitive credential path: {raw_path}")
    return tuple(sorted(paths))


def create_review_snapshot(
    project_root: str | Path,
    snapshot_root: str | Path,
    *,
    max_total_bytes: int = 100 * 1024 * 1024,
    max_files: int = 10_000,
    include_paths: tuple[str, ...] | list[str] | None = None,
) -> ReviewSnapshot:
    root = Path(project_root).expanduser().resolve(strict=True)
    destination_root = Path(snapshot_root).expanduser().resolve(strict=False)
    try:
        destination_root.relative_to(root)
    except ValueError:
        pass
    else:
        raise ValueError("snapshot destination must be outside the project root")

    entries: list[tuple[str, Path, os.stat_result]] = []
    seen_inodes: set[tuple[int, int]] = set()
    total = 0
    if include_paths is None:
        candidates: list[tuple[str, Path]] = []
        for directory, dirnames, filenames in os.walk(root, followlinks=False):
            current = Path(directory)
            retained_dirs = []
            for dirname in sorted(dirnames):
                candidate = current / dirname
                if dirname in _SKIP_DIRS:
                    continue
                if candidate.is_symlink():
                    raise ValueError(f"snapshot rejects symlink: {candidate}")
                retained_dirs.append(dirname)
            dirnames[:] = retained_dirs
            for filename in sorted(filenames):
                source = current / filename
                candidates.append((source.relative_to(root).as_posix(), source))
    else:
        candidates = []
        seen_relative: set[str] = set()
        for raw_relative in sorted(include_paths):
            if not isinstance(raw_relative, str) or not raw_relative.strip():
                raise ValueError("snapshot include path must be a non-empty string")
            lexical = Path(raw_relative)
            if lexical.is_absolute() or ".." in lexical.parts:
                raise ValueError(f"snapshot path escapes project root: {raw_relative}")
            source = root / lexical
            resolved = source.resolve(strict=True)
            resolved.relative_to(root)
            if resolved != source.absolute() or source.is_symlink():
                raise ValueError(f"snapshot rejects symlink: {raw_relative}")
            relative = resolved.relative_to(root).as_posix()
            if relative not in seen_relative:
                candidates.append((relative, source))
                seen_relative.add(relative)

    for relative, source in candidates:
            if source.is_symlink():
                raise ValueError(f"snapshot rejects symlink: {relative}")
            stat = source.stat(follow_symlinks=False)
            if not source.is_file():
                raise ValueError(f"snapshot rejects non-regular file: {relative}")
            identity = (stat.st_dev, stat.st_ino)
            if identity in seen_inodes:
                raise ValueError(f"snapshot rejects hardlink alias: {relative}")
            seen_inodes.add(identity)
            total += stat.st_size
            if total > max_total_bytes:
                raise ValueError("snapshot exceeds maximum total bytes")
            entries.append((relative, source, stat))
            if len(entries) > max_files:
                raise ValueError("snapshot exceeds maximum file count")

    digest = hashlib.sha256()
    payloads: list[tuple[str, bytes]] = []
    for relative, source, before in entries:
        with source.open("rb") as handle:
            opened = os.fstat(handle.fileno())
            if (opened.st_dev, opened.st_ino, opened.st_size) != (
                before.st_dev,
                before.st_ino,
                before.st_size,
            ):
                raise ValueError(f"snapshot source changed during read: {relative}")
            payload = handle.read()
            after = os.fstat(handle.fileno())
            if (after.st_size, after.st_mtime_ns) != (before.st_size, before.st_mtime_ns):
                raise ValueError(f"snapshot source changed during read: {relative}")
        encoded_path = relative.encode("utf-8")
        digest.update(len(encoded_path).to_bytes(8, "big"))
        digest.update(encoded_path)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(hashlib.sha256(payload).digest())
        payloads.append((relative, payload))

    subject = digest.hexdigest()
    destination = destination_root / subject
    if not destination.exists():
        destination_root.mkdir(parents=True, exist_ok=True, mode=0o700)
        temp = Path(tempfile.mkdtemp(prefix=f".{subject}.", dir=destination_root))
        try:
            for relative, payload in payloads:
                target = temp / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(payload)
                target.chmod(0o400)
            try:
                temp.rename(destination)
            except FileExistsError:
                shutil.rmtree(temp)
            else:
                for directory, _, _ in os.walk(destination, topdown=False):
                    Path(directory).chmod(0o500)
        except Exception:
            try:
                for path in temp.rglob("*"):
                    if path.is_dir():
                        path.chmod(0o700)
                    else:
                        path.chmod(0o600)
                temp.chmod(0o700)
                shutil.rmtree(temp)
            except Exception:
                pass
            raise
    return ReviewSnapshot(destination, subject, len(entries), total)
