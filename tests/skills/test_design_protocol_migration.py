from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MIGRATOR = (
    ROOT
    / "skills"
    / "design"
    / "comprehensive-designer-cognition"
    / "scripts"
    / "migrate_to_decision_ledger.py"
)


def _legacy_project(root: Path) -> dict[str, str]:
    files = {
        "DESIGN-BRIEF.md": """# Design Brief

## Design object
Exitn incident-response console

## Intended effect
Let an operator coordinate a safe evacuation without losing accountability.

## Decision boundary
- Decision levels in scope: intent, workflow, and operational detail
- Included actors: incident commander and floor wardens
- Included surfaces or scenarios: live incident dashboard and handoff
- Intentional exclusions: responder staffing policy
- Target fidelity: tested operational prototype
""",
        "DECISION-MAP.md": """# Decision Map

## Decision tree
DM-010 Incident ownership [committed] (record: DR-010)
└── DM-020 Offline handoff [reopened] (record: DR-020)

## Unresolved in-scope nodes
- DM-020 — Offline handoff after the radio test invalidated the first choice.
""",
        "DECISION-RECORDS.md": """# Decision Records

## DR-010 — Single incident commander
- **Level:** Workflow
- **Status:** committed
- **Question:** Who can issue the evacuation order?
- **Criteria:** speed, accountability, and recovery from error
- **Alternative A:** any floor warden
- **Alternative B:** one incident commander
- **Selection:** one incident commander
- **Tradeoffs and failure modes:** creates a bottleneck if the commander is unreachable
- **Evidence:** tabletop exercise E-010
- **Assumptions:** the duty roster identifies a reachable commander
- **Downstream consequences:** every ward must show command identity
- **Validation method and result:** tabletop exercise passed
- **Reopen if:** commander reachability falls below the response target

## DR-020 — Offline handoff
- **Level:** Operational detail
- **Status:** reopened
- **Question:** How does command transfer without network access?
- **Criteria:** continuity and unambiguous authority
- **Alternative A:** radio phrase
- **Alternative B:** signed paper card
- **Selection:** unresolved after radio test
- **Tradeoffs and failure modes:** paper can be delayed; radio can be ambiguous
- **Evidence:** radio test E-020 exposed ambiguity
- **Assumptions:** wardens carry printed kits
- **Downstream consequences:** handoff state remains unresolved
- **Validation method and result:** failed radio test E-020
- **Reopen if:** already reopened because E-020 failed
""",
        "DESIGN-COMPLETION.json": """{
  "fidelity": "tested operational prototype",
  "completion": {"allowed": false, "qualified_claim": "", "blockers": ["DM-020"]}
}
""",
    }
    for name, content in files.items():
        (root / name).write_text(content, encoding="utf-8")
    return files


def test_migrates_legacy_manifests_once_without_mutating_sources(tmp_path):
    sources = _legacy_project(tmp_path)

    completed = subprocess.run(
        [sys.executable, str(MIGRATOR), str(tmp_path)],
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    ledger = (tmp_path / "DESIGN-DECISIONS.md").read_text(encoding="utf-8")
    assert "Exitn incident-response console" in ledger
    assert "tested operational prototype" in ledger
    assert "incident commander and floor wardens" in ledger
    assert "D-010" in ledger and "Single incident commander" in ledger
    assert "D-020" in ledger and "Offline handoff" in ledger
    assert "commander reachability falls below the response target" in ledger
    assert "already reopened because E-020 failed" in ledger
    assert "D-020 — Offline handoff after the radio test" in ledger
    assert "D-001" not in ledger
    for name, original in sources.items():
        assert (tmp_path / name).read_text(encoding="utf-8") == original
        assert name in completed.stdout
    assert "legacy" in completed.stdout.lower()


def test_refuses_to_overwrite_an_existing_ledger(tmp_path):
    _legacy_project(tmp_path)
    ledger = tmp_path / "DESIGN-DECISIONS.md"
    ledger.write_text("keep reviewed ledger", encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, str(MIGRATOR), str(tmp_path)],
        capture_output=True,
        text=True,
    )

    assert completed.returncode != 0
    assert ledger.read_text(encoding="utf-8") == "keep reviewed ledger"
    assert "already exists" in (completed.stdout + completed.stderr).lower()
