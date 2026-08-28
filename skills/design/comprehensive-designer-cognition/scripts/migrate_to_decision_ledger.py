#!/usr/bin/env python3
"""Migrate legacy design manifests into one observable decision ledger.

The migration is intentionally one-way. It creates ``DESIGN-DECISIONS.md``
without changing or archiving the legacy source files; review the ledger before
archiving those files yourself.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


LEGACY_FILES = (
    "ORIGINAL-REQUEST.md",
    "DESIGN-BRIEF.md",
    "DECISION-MAP.md",
    "DECISION-RECORDS.md",
    "SYSTEM-SPEC.md",
    "DESIGN-AUDIT.md",
    "VALIDATION-REPORT.md",
    "DESIGN-COMPLETION.json",
    "INDEPENDENT-REVIEW-PROMPT.md",
    "INDEPENDENT-REVIEW.md",
    "REVIEW-RECEIPT.json",
    "enforcement.json",
    ".hermes.md",
)
_MAP_RE = re.compile(
    r".*?DM-(\d{3,})\s+(.+?)\s+\[([^]]+)](?:\s+\(record:\s*DR-(\d{3,})\))?\s*$"
)
_RECORD_RE = re.compile(r"^##\s+DR-(\d{3,})\s+[—-]\s+(.+?)\s*$")
_FIELD_RE = re.compile(r"^-\s+\*\*([^*]+):\*\*\s*(.*?)\s*$")


@dataclass(frozen=True)
class LegacyRecord:
    decision_id: str
    title: str
    fields: dict[str, str]


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _section(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    marker = f"## {heading}"
    try:
        start = next(index for index, line in enumerate(lines) if line.strip() == marker) + 1
    except StopIteration:
        return []
    end = next(
        (index for index in range(start, len(lines)) if lines[index].startswith("## ")),
        len(lines),
    )
    return lines[start:end]


def _section_text(text: str, heading: str) -> str:
    return " ".join(line.strip() for line in _section(text, heading) if line.strip())


def _bullet_fields(lines: list[str]) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("-") or ":" not in stripped:
            continue
        name, value = stripped[1:].split(":", 1)
        fields[name.strip()] = value.strip()
    return fields


def _decision_id(value: str) -> str:
    return f"D-{value}"


def _parse_map(text: str) -> list[tuple[str, str, str, str | None]]:
    result = []
    for line in _section(text, "Decision tree"):
        match = _MAP_RE.match(line)
        if match:
            map_number, title, status, record_number = match.groups()
            result.append(
                (_decision_id(record_number or map_number), title.strip(), status.strip(), record_number)
            )
    return result


def _parse_records(text: str) -> list[LegacyRecord]:
    lines = text.splitlines()
    starts = []
    for index, line in enumerate(lines):
        match = _RECORD_RE.match(line.strip())
        if match:
            starts.append((index, match.group(1), match.group(2)))
    records = []
    for position, (start, number, title) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else len(lines)
        fields = {}
        for line in lines[start + 1 : end]:
            match = _FIELD_RE.match(line.strip())
            if match:
                fields[match.group(1).strip()] = match.group(2).strip()
        records.append(LegacyRecord(_decision_id(number), title.strip(), fields))
    return records


def _value(fields: dict[str, str], *names: str) -> str:
    for name in names:
        value = fields.get(name, "").strip()
        if value:
            return value
    return "Not captured in the legacy manifests"


def _alternatives(fields: dict[str, str]) -> str:
    values = [
        fields.get("Alternative A", "").strip(),
        fields.get("Alternative B", "").strip(),
        fields.get("Other credible alternatives, including status quo or no intervention", "").strip(),
    ]
    alternatives = "; ".join(value for value in values if value)
    return alternatives or "No alternatives were captured in the legacy manifests"


def _completion_fidelity(root: Path, boundary: dict[str, str]) -> str:
    try:
        payload = json.loads(_read(root / "DESIGN-COMPLETION.json"))
        fidelity = payload.get("fidelity")
        if isinstance(fidelity, str) and fidelity.strip():
            return fidelity.strip()
    except (json.JSONDecodeError, TypeError):
        pass
    return boundary.get("Target fidelity", "Not captured in the legacy manifests")


def migrate(root: Path) -> tuple[Path, tuple[str, ...]]:
    root = root.expanduser().resolve(strict=False)
    ledger_path = root / "DESIGN-DECISIONS.md"
    if ledger_path.exists() or ledger_path.is_symlink():
        raise FileExistsError(f"{ledger_path} already exists; migration will not overwrite it")

    brief = _read(root / "DESIGN-BRIEF.md")
    map_text = _read(root / "DECISION-MAP.md")
    records_text = _read(root / "DECISION-RECORDS.md")
    map_entries = _parse_map(map_text)
    records = _parse_records(records_text)
    if not map_entries or not records:
        raise ValueError("legacy DECISION-MAP.md and DECISION-RECORDS.md are required")

    boundary = _bullet_fields(_section(brief, "Decision boundary"))
    design_object = _section_text(brief, "Design object") or "Not captured in the legacy manifests"
    intended_effect = _section_text(brief, "Intended effect") or "Not captured in the legacy manifests"
    in_scope_parts = [
        boundary.get("Decision levels in scope", ""),
        boundary.get("Included actors", ""),
        boundary.get("Included surfaces or scenarios", ""),
        boundary.get("Included states and edge conditions", ""),
    ]
    in_scope = "; ".join(part for part in in_scope_parts if part) or "Not captured in the legacy manifests"
    out_of_scope = boundary.get("Intentional exclusions", "Not captured in the legacy manifests")
    fidelity = _completion_fidelity(root, boundary)

    map_lines = []
    parent_id = "design boundary"
    for decision_id, title, status, _record in map_entries:
        map_lines.append(f"- {decision_id} [{status}] {parent_id} → {title}")
        parent_id = decision_id

    record_lines = []
    for record in records:
        fields = record.fields
        record_lines.extend(
            (
                f"### {record.decision_id} — {record.title}",
                f"- Level: {_value(fields, 'Level')}",
                f"- Question: {_value(fields, 'Question')}",
                f"- Criteria: {_value(fields, 'Criteria')}",
                f"- Alternatives: {_alternatives(fields)}",
                f"- Selection: {_value(fields, 'Selection')}",
                f"- Tradeoff: {_value(fields, 'Tradeoffs and failure modes')}",
                f"- Evidence: {_value(fields, 'Evidence')}",
                f"- Assumptions: {_value(fields, 'Assumptions')}",
                f"- Consequences: {_value(fields, 'Downstream consequences')}",
                f"- Validation: {_value(fields, 'Validation method and result')}",
                f"- Reopen if: {_value(fields, 'Reopen if')}",
                "",
            )
        )

    unresolved = []
    for line in _section(map_text, "Unresolved in-scope nodes"):
        stripped = line.strip()
        if stripped.startswith("-"):
            unresolved.append(re.sub(r"\bDM-(\d{3,})\b", r"D-\1", stripped))
    known_unresolved_ids = " ".join(unresolved)
    for decision_id, title, status, _record in map_entries:
        if status.lower() in {"open", "provisional", "reopened", "blocked"} and decision_id not in known_unresolved_ids:
            unresolved.append(f"- {decision_id} — {title} [{status}]")
    if not unresolved:
        unresolved = ["- None"]

    known_limitations = (
        "; ".join(item[2:].strip() for item in unresolved)
        if unresolved != ["- None"]
        else "Only the scope and evidence captured in the migrated legacy manifests"
    )
    supported_claim = (
        "No completion claim while consequential migrated decisions remain unresolved"
        if unresolved != ["- None"]
        else f"Legacy decision evidence migrated at {fidelity} fidelity; review before claiming completion"
    )
    ledger = "\n".join(
        [
            "# Design Decisions",
            "",
            "## Boundary",
            f"- Design object: {design_object}",
            f"- Intended effect: {intended_effect}",
            f"- In scope: {in_scope}",
            f"- Out of scope: {out_of_scope}",
            f"- Target fidelity: {fidelity}",
            "",
            "## Decision map",
            *map_lines,
            "",
            "## Consequential decisions",
            *record_lines,
            "## Unresolved consequential decisions",
            *unresolved,
            "",
            "## Completion status",
            f"- Fidelity: {fidelity}",
            f"- Supported claim: {supported_claim}",
            f"- Known limitations: {known_limitations}",
            "",
        ]
    )
    with ledger_path.open("x", encoding="utf-8") as handle:
        handle.write(ledger)
    legacy = tuple(name for name in LEGACY_FILES if (root / name).exists())
    return ledger_path, legacy


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", default=".")
    args = parser.parse_args(argv)
    try:
        ledger_path, legacy = migrate(Path(args.project_root))
    except (FileExistsError, OSError, ValueError) as exc:
        print(f"Migration failed: {exc}", file=sys.stderr)
        return 1
    print(f"Created {ledger_path}")
    print("Legacy files left untouched; review the ledger before archiving them:")
    for name in legacy:
        print(f"- {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
