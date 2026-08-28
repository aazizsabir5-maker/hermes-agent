#!/usr/bin/env python3
"""Validate the observable structure of one design-decision ledger.

This validator checks traceability fields, not private cognition, evidence truth,
or design quality.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


LEDGER_NAME = "DESIGN-DECISIONS.md"
PASS_MARKER = "DESIGN DECISIONS: CONTRACT PASSED"
_DECISION_ID_RE = re.compile(r"\bD-\d{3,}\b")
_MAP_RE = re.compile(r"^-\s+(D-\d{3,})\s+\[([^]]+)]\s+(.+)$")
_RECORD_RE = re.compile(r"^###\s+(D-\d{3,})\s+[—-]\s+(.+?)\s*$")
_FIELD_RE = re.compile(r"^-\s+([^:]+):\s*(.*?)\s*$")
_REQUIRED_SECTIONS = (
    "Boundary",
    "Decision map",
    "Consequential decisions",
    "Unresolved consequential decisions",
    "Completion status",
)
_BOUNDARY_FIELDS = (
    "Design object",
    "Intended effect",
    "In scope",
    "Out of scope",
    "Target fidelity",
)
_DECISION_FIELDS = (
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
)
_COMPLETION_FIELDS = ("Fidelity", "Supported claim", "Known limitations")


@dataclass(frozen=True)
class ValidationResult:
    passed: bool
    reason_code: str
    diagnostics: tuple[str, ...]


def _section(lines: list[str], heading: str) -> list[str] | None:
    marker = f"## {heading}"
    positions = [index for index, line in enumerate(lines) if line.strip() == marker]
    if len(positions) != 1:
        return None
    start = positions[0] + 1
    end = next(
        (index for index in range(start, len(lines)) if lines[index].startswith("## ")),
        len(lines),
    )
    return lines[start:end]


def _fields(lines: Iterable[str], *, owner: str, diagnostics: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in lines:
        match = _FIELD_RE.match(line.strip())
        if not match:
            continue
        name, value = match.groups()
        if name in result:
            diagnostics.append(f"{owner} has duplicate field: {name}")
        else:
            result[name] = value.strip()
    return result


def _require_fields(
    fields: dict[str, str], required: Iterable[str], *, owner: str, diagnostics: list[str]
) -> None:
    for name in required:
        if not fields.get(name):
            diagnostics.append(f"{owner} is missing a meaningful {name} field")


def _parse_records(lines: list[str], diagnostics: list[str]) -> dict[str, dict[str, str]]:
    starts: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        match = _RECORD_RE.match(line.strip())
        if match:
            starts.append((index, match.group(1)))
    records: dict[str, dict[str, str]] = {}
    for position, (start, decision_id) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else len(lines)
        if decision_id in records:
            diagnostics.append(f"Duplicate consequential decision record: {decision_id}")
            continue
        fields = _fields(lines[start + 1 : end], owner=decision_id, diagnostics=diagnostics)
        records[decision_id] = fields
        _require_fields(fields, _DECISION_FIELDS, owner=decision_id, diagnostics=diagnostics)
        alternatives = fields.get("Alternatives", "")
        lowered = alternatives.lower()
        if lowered.startswith("no credible alternative"):
            _, separator, reason = alternatives.partition(":")
            if not separator or not reason.strip():
                diagnostics.append(
                    f"{decision_id} Alternatives must state a reason when no credible alternative exists"
                )
        elif not any(separator in alternatives for separator in (";", " | ", " versus ", " vs. ")):
            diagnostics.append(
                f"{decision_id} Alternatives must compare distinct options or state why none exists"
            )
    return records


def validate_project(project_root: str | Path) -> ValidationResult:
    root = Path(project_root).expanduser().resolve(strict=False)
    path = root / LEDGER_NAME
    if not path.is_file():
        return ValidationResult(False, "missing_ledger", (f"{LEDGER_NAME} is missing",))
    try:
        raw = path.read_bytes()
        if len(raw) > 1_000_000:
            raise ValueError("ledger exceeds the 1 MB structural-validation limit")
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return ValidationResult(
            False, "malformed_ledger", (f"{LEDGER_NAME} must be valid UTF-8",)
        )
    except (OSError, ValueError) as exc:
        return ValidationResult(False, "malformed_ledger", (str(exc),))

    lines = text.splitlines()
    diagnostics: list[str] = []
    if not lines or lines[0].strip() != "# Design Decisions":
        diagnostics.append("Ledger must start with exactly one # Design Decisions heading")

    sections: dict[str, list[str]] = {}
    for name in _REQUIRED_SECTIONS:
        content = _section(lines, name)
        if content is None:
            diagnostics.append(f"Missing or duplicate section: {name}")
        else:
            sections[name] = content

    boundary = _fields(
        sections.get("Boundary", ()), owner="Boundary", diagnostics=diagnostics
    )
    _require_fields(boundary, _BOUNDARY_FIELDS, owner="Boundary", diagnostics=diagnostics)

    records = _parse_records(sections.get("Consequential decisions", []), diagnostics)
    if not records:
        diagnostics.append(
            "Completion requires at least one consequential decision record"
        )
    map_ids: set[str] = set()
    committed_ids: set[str] = set()
    unresolved_status_ids: set[str] = set()
    for line in sections.get("Decision map", []):
        stripped = line.strip()
        if not stripped or not stripped.startswith("-"):
            continue
        match = _MAP_RE.match(stripped)
        if not match:
            diagnostics.append(f"Malformed decision-map entry: {stripped}")
            continue
        decision_id, status, relationship = match.groups()
        if decision_id in map_ids:
            diagnostics.append(f"Duplicate decision-map identifier: {decision_id}")
        map_ids.add(decision_id)
        if "→" not in relationship and "->" not in relationship:
            diagnostics.append(f"{decision_id} must trace a parent → child relationship")
        normalized_status = status.strip().lower()
        if normalized_status in {"committed", "validated"}:
            committed_ids.add(decision_id)
        elif normalized_status in {"open", "provisional", "reopened", "blocked"}:
            unresolved_status_ids.add(decision_id)
    if not map_ids:
        diagnostics.append("Decision map must contain at least one parent → child entry")
    for decision_id in sorted(committed_ids - records.keys()):
        diagnostics.append(f"{decision_id} is committed or validated but has no decision record")

    unresolved_lines = [
        line.strip()[1:].strip()
        for line in sections.get("Unresolved consequential decisions", [])
        if line.strip().startswith("-")
    ]
    unresolved = [item for item in unresolved_lines if item.lower() not in {"none", "none."}]
    disclosed_unresolved_ids = {
        decision_id
        for item in unresolved
        for decision_id in _DECISION_ID_RE.findall(item)
    }
    for decision_id in sorted(unresolved_status_ids - disclosed_unresolved_ids):
        diagnostics.append(
            f"{decision_id} has an unresolved map status but is not disclosed as unresolved"
        )
    if unresolved:
        ids = sorted({item for line in unresolved for item in _DECISION_ID_RE.findall(line)})
        detail = ", ".join(ids) if ids else "; ".join(unresolved)
        diagnostics.append(f"Unresolved consequential decisions: {detail}")

    completion = _fields(
        sections.get("Completion status", ()),
        owner="Completion status",
        diagnostics=diagnostics,
    )
    _require_fields(
        completion, _COMPLETION_FIELDS, owner="Completion status", diagnostics=diagnostics
    )
    fidelity = completion.get("Fidelity", "")
    supported_claim = completion.get("Supported claim", "")
    meaningful_fidelity_tokens = {
        token
        for token in re.findall(r"[a-z0-9]+", fidelity.casefold())
        if len(token) >= 2 and token not in {"fidelity", "tested", "target"}
    }
    if (
        fidelity
        and supported_claim
        and meaningful_fidelity_tokens
        and not any(token in supported_claim.casefold() for token in meaningful_fidelity_tokens)
    ):
        diagnostics.append(
            "Supported claim must be qualified by the stated completion fidelity"
        )
    if unresolved:
        diagnostics.append(
            "Completion claim is not qualified while consequential decisions remain unresolved"
        )

    if diagnostics:
        reason = "unresolved_decisions" if unresolved else "ledger_invalid"
        return ValidationResult(False, reason, tuple(dict.fromkeys(diagnostics)))
    return ValidationResult(True, "ledger_valid", ())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", default=".")
    args = parser.parse_args(argv)
    result = validate_project(args.project_root)
    if result.passed:
        print(PASS_MARKER)
        return 0
    print("DESIGN DECISIONS: NOT YET COMPLETE")
    for diagnostic in result.diagnostics:
        print(f"- {diagnostic}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
