"""Bounded subprocess runner for the audited design validator."""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


PASS_MARKER = "DESIGN COMPLETION: CONTRACT PASSED"


@dataclass(frozen=True)
class ValidatorResult:
    passed: bool
    reason_code: str
    exit_code: int | None
    stdout: str
    stderr: str
    validator_sha256: str


def run_validator(
    project_root: str | Path,
    *,
    validator_path: str | Path,
    timeout_seconds: float = 30.0,
    max_output_bytes: int = 65_536,
) -> ValidatorResult:
    root = Path(project_root).expanduser().resolve(strict=True)
    validator = Path(validator_path).expanduser().resolve(strict=True)
    digest = hashlib.sha256(validator.read_bytes()).hexdigest()
    env = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "PYTHONUTF8": "1",
    }
    try:
        completed = subprocess.run(
            [sys.executable, str(validator), str(root)],
            cwd=str(root),
            env=env,
            capture_output=True,
            timeout=float(timeout_seconds),
            check=False,
        )
    except subprocess.TimeoutExpired:
        return ValidatorResult(False, "validator_timeout", None, "", "", digest)
    except Exception:
        return ValidatorResult(False, "validator_execution_error", None, "", "", digest)

    stdout_bytes = completed.stdout or b""
    stderr_bytes = completed.stderr or b""
    if len(stdout_bytes) + len(stderr_bytes) > max_output_bytes:
        return ValidatorResult(
            False,
            "validator_output_too_large",
            completed.returncode,
            "",
            "",
            digest,
        )
    stdout = stdout_bytes.decode("utf-8", errors="replace")
    stderr = stderr_bytes.decode("utf-8", errors="replace")
    if completed.returncode != 0:
        reason = "validator_nonzero_exit"
        passed = False
    elif PASS_MARKER not in {line.strip() for line in stdout.splitlines()}:
        reason = "missing_pass_marker"
        passed = False
    else:
        reason = "validator_passed"
        passed = True
    return ValidatorResult(
        passed,
        reason,
        completed.returncode,
        stdout,
        stderr,
        digest,
    )
