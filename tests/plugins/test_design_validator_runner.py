from pathlib import Path

from plugins.policies.design_enforcement.validator_runner import run_validator


def _script(path: Path, body: str) -> Path:
    path.write_text("import sys\n" + body + "\n", encoding="utf-8")
    return path


def test_validator_requires_zero_exit_and_exact_pass_marker(tmp_path):
    script = _script(tmp_path / "validator.py", 'print("DESIGN DECISIONS: CONTRACT PASSED")')
    result = run_validator(tmp_path, validator_path=script, timeout_seconds=1)
    assert result.passed is True
    assert result.exit_code == 0
    assert result.reason_code == "ledger_valid"
    assert not hasattr(result, "validator_sha256")


def test_zero_exit_without_marker_blocks(tmp_path):
    script = _script(tmp_path / "validator.py", 'print("looks good")')
    result = run_validator(tmp_path, validator_path=script, timeout_seconds=1)
    assert result.passed is False
    assert result.reason_code == "validator_execution_error"


def test_ledger_diagnostics_are_structured_without_provenance(tmp_path):
    script = _script(
        tmp_path / "validator.py",
        'print("DESIGN DECISIONS: NOT YET COMPLETE")\n'
        'print("- Unresolved consequential decisions: D-004, D-009")\n'
        "sys.exit(1)",
    )
    result = run_validator(tmp_path, validator_path=script, timeout_seconds=1)
    assert result.reason_code == "unresolved_decisions"
    assert result.diagnostics == (
        "Unresolved consequential decisions: D-004, D-009",
    )


def test_nonzero_timeout_and_oversized_output_block(tmp_path):
    failing = _script(tmp_path / "fail.py", 'print("bad", file=sys.stderr)\nsys.exit(3)')
    result = run_validator(tmp_path, validator_path=failing, timeout_seconds=1)
    assert result.passed is False
    assert result.exit_code == 3

    slow = _script(tmp_path / "slow.py", "import time\ntime.sleep(2)")
    result = run_validator(tmp_path, validator_path=slow, timeout_seconds=0.02)
    assert result.reason_code == "validator_timeout"

    noisy = _script(tmp_path / "noisy.py", 'print("x" * 10000)')
    result = run_validator(
        tmp_path, validator_path=noisy, timeout_seconds=1, max_output_bytes=100
    )
    assert result.reason_code == "validator_output_too_large"
