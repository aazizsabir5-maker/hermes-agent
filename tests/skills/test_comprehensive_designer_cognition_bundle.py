"""The fork ships the audited design protocol as a portable skill bundle."""

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills" / "design" / "comprehensive-designer-cognition"


def test_design_protocol_bundle_contains_runtime_contract():
    required = {
        "SKILL.md",
        "scripts/init_design_protocol.py",
        "scripts/validate_design_completion.py",
        "scripts/create_review_receipt.py",
        "templates/DESIGN-COMPLETION.json",
        "templates/INDEPENDENT-REVIEW.md",
        "templates/REVIEW-RECEIPT.json",
        "templates/enforcement.json",
    }
    assert {str(path.relative_to(SKILL)) for path in SKILL.rglob("*") if path.is_file()} >= required
    skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert "trusted `design_review_request` tool" in skill_text
    assert "does not satisfy a trusted runtime receipt requirement" in skill_text


def test_design_protocol_bundle_is_machine_path_portable():
    for path in SKILL.rglob("*"):
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            assert "/Users/ariansabir" not in text


def test_validator_and_helpers_compile():
    for name in (
        "init_design_protocol.py",
        "validate_design_completion.py",
        "create_review_receipt.py",
    ):
        source = (SKILL / "scripts" / name).read_text(encoding="utf-8")
        compile(source, str(SKILL / "scripts" / name), "exec")


def test_initializer_enables_working_mode_enforcement(tmp_path):
    subprocess.run(
        [sys.executable, str(SKILL / "scripts" / "init_design_protocol.py"), str(tmp_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert (tmp_path / ".hermes" / "enforcement.json").read_text(
        encoding="utf-8"
    ) == (SKILL / "templates" / "enforcement.json").read_text(encoding="utf-8")
