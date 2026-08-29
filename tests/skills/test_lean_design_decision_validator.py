from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills" / "design" / "comprehensive-designer-cognition"
VALIDATOR = SKILL / "scripts" / "validate_design_completion.py"
INITIALIZER = SKILL / "scripts" / "init_design_protocol.py"


def _load_validator():
    spec = importlib.util.spec_from_file_location("lean_design_validator", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _valid_ledger() -> str:
    return """# Design Decisions

## Boundary
- Design object: A checkout flow
- Intended effect: Reduce avoidable abandonment
- In scope: Cart through confirmation
- Out of scope: Fulfilment operations
- Target fidelity: Tested prototype

## Decision map
- D-001 [context] situation → intent
- D-002 [validated] D-001 → implementation

## Consequential decisions
### D-002 — Guest checkout
- Level: Experience and Behavior
- Question: Must purchase require an account?
- Criteria: Completion effort, recovery, and support cost
- Alternatives: Require account; allow guest checkout
- Selection: Allow guest checkout with optional account creation after purchase
- Tradeoff: Less identity data before purchase in exchange for lower friction
- Evidence: Prototype test E-001 showed users completed the shorter path
- Assumptions: The identity service can link a later-created account
- Consequences: Confirmation and recovery must work without an account
- Validation: Validated in prototype test E-001
- Reopen if: Fraud or recovery failures exceed the agreed threshold

## Unresolved consequential decisions
- None

## Completion status
- Fidelity: Tested prototype
- Supported claim: Prototype-fidelity design complete for cart through confirmation
- Known limitations: Production fraud controls were not tested
"""


def _write(root: Path, text: str | None = None) -> Path:
    path = root / "DESIGN-DECISIONS.md"
    path.write_text(text if text is not None else _valid_ledger(), encoding="utf-8")
    return path


def test_smallest_honest_ledger_passes(tmp_path):
    validator = _load_validator()
    _write(tmp_path)
    result = validator.validate_project(tmp_path)
    assert result.passed is True
    assert result.reason_code == "ledger_valid"
    assert result.diagnostics == ()


@pytest.mark.parametrize(
    ("mutation", "diagnostic"),
    [
        (lambda text: text.replace("## Boundary", "## Missing boundary"), "Boundary"),
        (
            lambda text: text.replace(
                "- D-001 [context] situation → intent",
                "- D-001 [committed] situation → intent",
            ),
            "D-001",
        ),
        (
            lambda text: text.replace(
                "Require account; allow guest checkout", "Allow guest checkout"
            ),
            "Alternatives",
        ),
        (lambda text: text.replace("- Tradeoff:", "- Missing tradeoff:"), "Tradeoff"),
        (lambda text: text.replace("- Assumptions:", "- Missing assumptions:"), "Assumptions"),
        (lambda text: text.replace("- Consequences:", "- Missing consequences:"), "Consequences"),
        (lambda text: text.replace("- Validation:", "- Missing validation:"), "Validation"),
        (lambda text: text.replace("- Reopen if:", "- Missing reopen:"), "Reopen if"),
    ],
)
def test_one_mutation_has_an_actionable_failure(tmp_path, mutation, diagnostic):
    validator = _load_validator()
    _write(tmp_path, mutation(_valid_ledger()))
    result = validator.validate_project(tmp_path)
    assert result.passed is False
    assert diagnostic in "\n".join(result.diagnostics)


def test_no_credible_alternative_requires_a_reason(tmp_path):
    validator = _load_validator()
    valid = _valid_ledger().replace(
        "Require account; allow guest checkout",
        "No credible alternative: payment regulation requires this route",
    )
    _write(tmp_path, valid)
    assert validator.validate_project(tmp_path).passed is True

    invalid = valid.replace(
        "No credible alternative: payment regulation requires this route",
        "No credible alternative",
    )
    _write(tmp_path, invalid)
    result = validator.validate_project(tmp_path)
    assert result.passed is False
    assert "reason" in "\n".join(result.diagnostics).lower()


def test_unresolved_decisions_and_unqualified_claim_fail_with_ids(tmp_path):
    validator = _load_validator()
    text = _valid_ledger().replace("- None", "- D-009 — Production fraud threshold")
    text = text.replace(
        "Prototype-fidelity design complete for cart through confirmation",
        "The design is complete",
    )
    _write(tmp_path, text)
    result = validator.validate_project(tmp_path)
    assert result.passed is False
    joined = "\n".join(result.diagnostics)
    assert "D-009" in joined
    assert "qualified" in joined.lower()


def test_completion_requires_a_decision_record_and_fidelity_qualified_claim(tmp_path):
    validator = _load_validator()
    without_records = _valid_ledger().replace(
        "- D-002 [validated] D-001 → implementation",
        "- D-002 [context] D-001 → implementation",
    )
    start = without_records.index("### D-002")
    end = without_records.index("## Unresolved consequential decisions")
    without_records = without_records[:start] + without_records[end:]
    _write(tmp_path, without_records)
    result = validator.validate_project(tmp_path)
    assert result.passed is False
    assert "record" in "\n".join(result.diagnostics).lower()

    unqualified = _valid_ledger().replace(
        "Prototype-fidelity design complete for cart through confirmation",
        "The design is complete",
    )
    _write(tmp_path, unqualified)
    result = validator.validate_project(tmp_path)
    assert result.passed is False
    assert "fidelity" in "\n".join(result.diagnostics).lower()


def test_open_map_status_must_be_disclosed_and_short_fidelity_must_qualify_claim(
    tmp_path,
):
    validator = _load_validator()
    silently_open = _valid_ledger().replace(
        "- D-001 [context] situation → intent",
        "- D-001 [open] situation → intent",
    )
    _write(tmp_path, silently_open)
    result = validator.validate_project(tmp_path)
    assert result.passed is False
    assert "D-001" in "\n".join(result.diagnostics)

    short_fidelity = _valid_ledger().replace("Tested prototype", "MVP")
    short_fidelity = short_fidelity.replace(
        "Prototype-fidelity design complete for cart through confirmation",
        "The design is complete",
    )
    _write(tmp_path, short_fidelity)
    result = validator.validate_project(tmp_path)
    assert result.passed is False
    assert "fidelity" in "\n".join(result.diagnostics).lower()


def test_every_decision_record_must_appear_in_the_decision_map(tmp_path):
    validator = _load_validator()
    orphan = _valid_ledger().replace(
        "## Unresolved consequential decisions",
        """### D-099 — Orphaned record
- Level: Detail
- Question: Which local detail should change?
- Criteria: Traceability and consistency
- Alternatives: Keep it; change it
- Selection: Change it
- Tradeoff: More implementation work for clearer behavior
- Evidence: Inspection found an inconsistency
- Assumptions: The parent decision remains valid
- Consequences: The detail changes in the artifact
- Validation: Inspected after implementation
- Reopen if: The parent decision changes

## Unresolved consequential decisions""",
    )
    _write(tmp_path, orphan)
    result = validator.validate_project(tmp_path)
    assert result.passed is False
    joined = "\n".join(result.diagnostics)
    assert "D-099" in joined
    assert "map" in joined.lower()


def test_supported_claim_must_name_its_scope(tmp_path):
    validator = _load_validator()
    scope_free = _valid_ledger().replace(
        "Prototype-fidelity design complete for cart through confirmation",
        "Prototype-fidelity design complete",
    )
    _write(tmp_path, scope_free)
    result = validator.validate_project(tmp_path)
    assert result.passed is False
    assert "scope" in "\n".join(result.diagnostics).lower()


def test_supported_claim_cannot_hide_mismatched_fidelity_after_completion(tmp_path):
    validator = _load_validator()
    mismatched = _valid_ledger().replace(
        "Prototype-fidelity design complete for cart through confirmation",
        "Production implementation complete for cart through confirmation; tested prototype",
    )
    _write(tmp_path, mismatched)
    result = validator.validate_project(tmp_path)
    assert result.passed is False
    assert "fidelity" in "\n".join(result.diagnostics).lower()


def test_unknown_decision_map_status_is_rejected(tmp_path):
    validator = _load_validator()
    unknown = _valid_ledger().replace(
        "- D-001 [context] situation → intent",
        "- D-001 [pending] situation → intent",
    )
    _write(tmp_path, unknown)
    result = validator.validate_project(tmp_path)
    assert result.passed is False
    joined = "\n".join(result.diagnostics)
    assert "D-001" in joined
    assert "status" in joined.lower()


def test_decision_map_requires_one_connected_hierarchy(tmp_path):
    validator = _load_validator()
    disconnected = _valid_ledger().replace(
        "- D-002 [validated] D-001 → implementation",
        "- D-002 [validated] orphan-root → isolated-child",
    )
    _write(tmp_path, disconnected)
    result = validator.validate_project(tmp_path)
    assert result.passed is False
    assert "D-002" in "\n".join(result.diagnostics)
    assert "parent" in "\n".join(result.diagnostics).lower()

    single_node = _valid_ledger().replace(
        "- D-002 [validated] D-001 → implementation\n",
        "",
    ).replace(
        "### D-002 — Guest checkout\n",
        "### D-001 — Guest checkout\n",
    )
    _write(tmp_path, single_node)
    result = validator.validate_project(tmp_path)
    assert result.passed is False
    assert "hierarchy" in "\n".join(result.diagnostics).lower()


def test_missing_ledger_and_malformed_utf8_fail_cleanly(tmp_path):
    validator = _load_validator()
    missing = validator.validate_project(tmp_path)
    assert missing.reason_code == "missing_ledger"
    assert "DESIGN-DECISIONS.md is missing" in missing.diagnostics

    (tmp_path / "DESIGN-DECISIONS.md").write_bytes(b"# Design Decisions\n\xff")
    malformed = validator.validate_project(tmp_path)
    assert malformed.reason_code == "malformed_ledger"
    assert any("UTF-8" in item for item in malformed.diagnostics)


def test_malformed_structure_and_duplicate_fields_fail(tmp_path):
    validator = _load_validator()
    text = _valid_ledger().replace(
        "- Question: Must purchase require an account?",
        "- Question: Must purchase require an account?\n- Question: Duplicate",
    )
    _write(tmp_path, text)
    result = validator.validate_project(tmp_path)
    assert result.passed is False
    assert any("duplicate" in item.lower() for item in result.diagnostics)


def test_cli_exit_and_diagnostics_match_result(tmp_path):
    _write(tmp_path, _valid_ledger().replace("- Validation:", "- Missing:"))
    completed = subprocess.run(
        [sys.executable, str(VALIDATOR), str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 1
    assert "Validation" in completed.stdout
    assert "receipt" not in completed.stdout.lower()
    assert "snapshot" not in completed.stdout.lower()


def test_initializer_creates_only_the_ledger_and_never_overwrites(tmp_path):
    before = {path.name for path in tmp_path.iterdir()}
    first = subprocess.run(
        [sys.executable, str(INITIALIZER), str(tmp_path)],
        capture_output=True,
        text=True,
        check=True,
    )
    ledger = tmp_path / "DESIGN-DECISIONS.md"
    assert ledger.is_file()
    assert "created" in first.stdout.lower()
    after = {path.name for path in tmp_path.iterdir()}
    assert after - before == {"DESIGN-DECISIONS.md"}

    ledger.write_text("preserve me", encoding="utf-8")
    second = subprocess.run(
        [sys.executable, str(INITIALIZER), str(tmp_path)],
        capture_output=True,
        text=True,
        check=True,
    )
    assert ledger.read_text(encoding="utf-8") == "preserve me"
    assert "already exists" in second.stdout.lower()
