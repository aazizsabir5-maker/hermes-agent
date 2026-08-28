"""Bounded subprocess runner for the structural decision-ledger validator."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


PASS_MARKER = "DESIGN DECISIONS: CONTRACT PASSED"


@dataclass(frozen=True)
class ValidatorResult:
    passed: bool
    reason_code: str
    exit_code: int | None
    stdout: str
    stderr: str
    diagnostics: tuple[str, ...]
    supported_claim: str = ""


def run_validator(
    project_root: str | Path,
    *,
    validator_path: str | Path,
    timeout_seconds: float = 30.0,
    max_output_bytes: int = 65_536,
) -> ValidatorResult:
    root = Path(project_root).expanduser().resolve(strict=False)
    validator = Path(validator_path).expanduser().resolve(strict=True)
    try:
        completed = subprocess.run(
            [sys.executable, str(validator), str(root)],
            cwd=str(root),
            capture_output=True,
            timeout=float(timeout_seconds),
            check=False,
        )
    except subprocess.TimeoutExpired:
        return ValidatorResult(False, "validator_timeout", None, "", "", (), "")
    except Exception:
        return ValidatorResult(False, "validator_execution_error", None, "", "", (), "")

    stdout_bytes = completed.stdout or b""
    stderr_bytes = completed.stderr or b""
    if len(stdout_bytes) + len(stderr_bytes) > max_output_bytes:
        return ValidatorResult(
            False, "validator_output_too_large", completed.returncode, "", "", (), ""
        )
    stdout = stdout_bytes.decode("utf-8", errors="replace")
    stderr = stderr_bytes.decode("utf-8", errors="replace")
    diagnostics = tuple(
        line[2:].strip()
        for line in stdout.splitlines()
        if line.startswith("- ") and line[2:].strip()
    )
    supported_claim = next(
        (
            line.removeprefix("SUPPORTED CLAIM:").strip()
            for line in stdout.splitlines()
            if line.startswith("SUPPORTED CLAIM:")
        ),
        "",
    )
    passed = completed.returncode == 0 and PASS_MARKER in {
        line.strip() for line in stdout.splitlines()
    }
    if passed:
        reason = "ledger_valid"
    elif any("DESIGN-DECISIONS.md is missing" in item for item in diagnostics):
        reason = "missing_ledger"
    elif any(item.startswith("Unresolved consequential decisions:") for item in diagnostics):
        reason = "unresolved_decisions"
    else:
        reason = "ledger_invalid" if completed.returncode == 1 else "validator_execution_error"
    return ValidatorResult(
        passed,
        reason,
        completed.returncode,
        stdout,
        stderr,
        diagnostics,
        supported_claim,
    )
