"""Portable bundle contract for the lean comprehensive-design skill."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills" / "design" / "comprehensive-designer-cognition"
INVARIANT = (
    "Before Hermes may claim a substantial design is finished, every consequential "
    "in-scope decision must be traceable from intent to implementation and must record "
    "its alternatives, selected direction, tradeoff, evidence or assumption, downstream "
    "consequence, validation status, and reopening condition; unresolved consequential "
    "decisions must be disclosed as unresolved rather than silently treated as complete."
)


def test_skill_preserves_comprehensive_decision_philosophy():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert INVARIANT in text
    assert "Expand the graph progressively" in text
    for level in (
        "Situation",
        "Intent",
        "Frame",
        "Strategy",
        "System",
        "Experience and Behavior",
        "Form and Language",
        "Detail",
        "Realization and Evolution",
    ):
        assert level in text


def test_skill_requires_one_observable_ledger_with_proportionate_evidence():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert "one `DESIGN-DECISIONS.md` ledger" in text
    assert "Evidence should match consequence" in text
    assert "Independent review is optional" in text
    assert "risk" in text[text.index("Independent review is optional") :][:400]
    for field in (
        "Question",
        "Criteria",
        "Alternatives",
        "Selection",
        "Tradeoff",
        "Evidence",
        "Assumptions",
        "Consequences",
        "Validation",
        "Reopen if",
    ):
        assert f"- {field}" in text


def test_skill_does_not_require_lifecycle_or_provenance_ceremony():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8").lower()
    for forbidden in (
        "working mode",
        "completion mode",
        "finalizing mode",
        "design_review_request",
        "review receipt",
        "reviewer session",
        "immutable snapshot",
        "subject hash",
    ):
        assert forbidden not in text


def test_ledger_template_has_the_complete_minimum_structure():
    template = (SKILL / "templates" / "DESIGN-DECISIONS.md").read_text(
        encoding="utf-8"
    )
    for heading in (
        "# Design Decisions",
        "## Boundary",
        "## Decision map",
        "## Consequential decisions",
        "## Unresolved consequential decisions",
        "## Completion status",
    ):
        assert heading in template
    for field in (
        "Design object",
        "Intended effect",
        "In scope",
        "Out of scope",
        "Target fidelity",
        "Level",
        "Question",
        "Criteria",
        "Alternatives",
        "Selection",
        "Tradeoff",
        "Evidence",
        "Assumptions",
        "Consequences",
        "Validation",
        "Reopen if",
        "Fidelity",
        "Supported claim",
        "Known limitations",
    ):
        assert f"- {field}" in template


def test_bundle_is_machine_path_portable_and_python_helpers_compile():
    for path in SKILL.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        assert "/Users/ariansabir" not in text
        if path.suffix == ".py":
            compile(text, str(path), "exec")
