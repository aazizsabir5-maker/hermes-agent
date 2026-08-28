#!/usr/bin/env python3
"""Validate the design-completion evidence contract.

Usage:
    python validate_design_completion.py [project-root]
    python validate_design_completion.py --subject-hash [project-root]

A pass proves structural consistency and review freshness, not design quality,
evidence truth, or reviewer independence. Runtime enforcement must still make a
successful validation mandatory before delivering a completion claim.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

MANIFEST = "DESIGN-COMPLETION.json"
REQUEST_FILE = "ORIGINAL-REQUEST.md"
REVIEW_REPORT = "INDEPENDENT-REVIEW.md"
REVIEW_RECEIPT = "REVIEW-RECEIPT.json"

REQUIRED_ARTIFACTS = (
    REQUEST_FILE,
    "DESIGN-BRIEF.md",
    "DECISION-MAP.md",
    "DECISION-RECORDS.md",
    "SYSTEM-SPEC.md",
    "DESIGN-AUDIT.md",
    "VALIDATION-REPORT.md",
)

REQUIRED_HEADINGS = {
    REQUEST_FILE: ("Original request", "Request source", "Boundary reconciliation"),
    "DESIGN-BRIEF.md": (
        "Design object", "Situation", "Intended effect", "Decision boundary",
        "Success, failure, and harm criteria", "Constraints", "Evidence",
        "Assumptions", "Non-goals", "Open questions and blockers",
    ),
    "DECISION-MAP.md": (
        "Decision tree", "Active frontier", "Cross-cutting decisions", "Unresolved in-scope nodes",
        "Expansion audit",
    ),
    "DECISION-RECORDS.md": ("Decision records",),
    "SYSTEM-SPEC.md": (
        "System boundary and theory", "Repeated family", "Novel-extension test",
        "Cross-system coherence rules",
    ),
    "DESIGN-AUDIT.md": (
        "Evidence index", "Applicable diagnostic views",
        "Context and transformation audit", "Bottom-up critique", "Findings",
    ),
    "VALIDATION-REPORT.md": (
        "Claim inventory", "Deterministic checks", "Direct inspection",
        "Repeated-system extension tests", "Unresolved evidence gaps",
        "Pre-review validation output",
    ),
}

REQUIRED_GATES = (
    "decision_boundary",
    "progressive_expansion",
    "consequential_records",
    "repeated_system_specification",
    "novel_extension",
    "artifact_and_perceptual_audit",
    "context_and_transformation_audit",
    "bottom_up_critique",
    "automated_validation",
    "independent_review",
)

NON_WAIVABLE_GATES = {
    "decision_boundary",
    "progressive_expansion",
    "consequential_records",
    "artifact_and_perceptual_audit",
    "bottom_up_critique",
    "automated_validation",
    "independent_review",
}

FIDELITY_TO_CLAIM = {
    "concept": "Concept complete",
    "system-specification": "System specified",
    "high-fidelity-artifact": "High-fidelity artifact complete",
    "production-implementation": "Production implementation complete",
}

PLACEHOLDERS = (
    "REPLACE_ME", "[Name the", "[Current reality", "[Observable change",
    "[Paste the", "[List every", "[Rules that", "[Only questions",
)
MAP_NODE_PATTERN = re.compile(
    r"^(?P<prefix>[^\n]*?)(?P<id>DM-[0-9]{3,})\s+.+?\s+\[(?P<status>open|provisional|committed|validated|reopened|out-of-scope|blocked)\](?:\s+\(record:\s*(?P<record>DR-[0-9]{3,})\))?\s*$",
    re.IGNORECASE,
)
RECORD_HEADING_PATTERN = re.compile(r"^##\s+(DR-[0-9]{3,})\s+[—-]\s+.+$", re.MULTILINE)
REQUIRED_RECORD_FIELDS = (
    "Level", "Status", "Question", "Affected people or systems", "Criteria",
    "Alternative A", "Alternative B", "Selection", "Tradeoffs and failure modes",
    "Evidence", "Assumptions", "Downstream consequences", "Consequence if wrong",
    "Reversibility", "Uncertainty", "Validation method and result", "Reopen if",
)
TEXT_EVIDENCE_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".csv", ".html"}
EVIDENCE_ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]{0,31}-[0-9]{3,}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(nonempty_string(v) for v in value)


class DuplicateJSONKeyError(ValueError):
    pass


def reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJSONKeyError(f"duplicate object member: {key}")
        result[key] = value
    return result


def json_structure_error(value: Any, max_depth: int = 100) -> str | None:
    stack: list[tuple[Any, int]] = [(value, 0)]
    while stack:
        current, depth = stack.pop()
        if depth > max_depth:
            return f"JSON nesting exceeds {max_depth} levels"
        if isinstance(current, str):
            if any(0xD800 <= ord(char) <= 0xDFFF for char in current):
                return "contains an invalid lone Unicode surrogate"
        elif isinstance(current, float) and not math.isfinite(current):
            return "contains a non-finite JSON number"
        elif isinstance(current, dict):
            for key, item in current.items():
                stack.append((key, depth + 1))
                stack.append((item, depth + 1))
        elif isinstance(current, list):
            stack.extend((item, depth + 1) for item in current)
    return None


class InvalidJSONConstantError(ValueError):
    pass


def reject_json_constant(value: str) -> None:
    raise InvalidJSONConstantError(f"non-JSON numeric constant: {value}")


def strict_json_loads(text: str) -> Any:
    return json.loads(
        text,
        object_pairs_hook=reject_duplicate_json_keys,
        parse_constant=reject_json_constant,
    )


def resolve_json_pointer(value: Any, pointer: str) -> tuple[bool, Any]:
    if pointer == "":
        return True, value
    if not pointer.startswith("/"):
        return False, None
    current = value
    for raw_part in pointer[1:].split("/"):
        if re.search(r"~(?![01])", raw_part):
            return False, None
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict):
            if part not in current:
                return False, None
            current = current[part]
        elif isinstance(current, list):
            if not re.fullmatch(r"0|[1-9][0-9]*", part):
                return False, None
            index = int(part)
            if index >= len(current):
                return False, None
            current = current[index]
        else:
            return False, None
    return True, current


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def safe_child(root: Path, value: str) -> Path | None:
    try:
        candidate = (root / value).resolve()
        candidate.relative_to(root)
        return candidate
    except (OSError, ValueError):
        return None


def normalized_heading(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()


def markdown_structural_text(text: str) -> str:
    """Remove fenced code while preserving line boundaries."""
    output: list[str] = []
    fence_char: str | None = None
    fence_length = 0
    for line in text.splitlines(keepends=True):
        body = line.rstrip("\r\n")
        newline = line[len(body):]
        if fence_char is None:
            opening = re.match(r"^ {0,3}(?P<fence>`{3,}|~{3,})(?P<info>.*)$", body)
            if opening and not (
                opening.group("fence")[0] == "`" and "`" in opening.group("info")
            ):
                fence_char = opening.group("fence")[0]
                fence_length = len(opening.group("fence"))
                output.append(newline)
            else:
                output.append(line)
        else:
            closing = re.match(
                rf"^ {{0,3}}{re.escape(fence_char)}{{{fence_length},}}[ \t]*$",
                body,
            )
            output.append(newline)
            if closing:
                fence_char = None
                fence_length = 0
    return "".join(output)


def atx_headings(text: str, *, strip_fences: bool = True) -> list[tuple[str, int, int, int]]:
    source = markdown_structural_text(text) if strip_fences else text
    headings: list[tuple[str, int, int, int]] = []
    pattern = re.compile(
        r"^ {0,3}(?P<marks>#{1,6})(?:[ \t]+(?P<content>[^\r\n]*))?[ \t]*$",
        re.MULTILINE,
    )
    for match in pattern.finditer(source):
        content = match.group("content") or ""
        content = re.sub(r"[ \t]+#+[ \t]*$", "", content).strip()
        headings.append((normalized_heading(content), len(match.group("marks")), match.start(), match.end()))
    return headings


def markdown_headings(text: str) -> list[str]:
    return [title for title, _level, _start, _end in atx_headings(text)]


def markdown_section(text: str, heading: str) -> str | None:
    structural = markdown_structural_text(text)
    target = normalized_heading(heading)
    headings = atx_headings(structural, strip_fences=False)
    for index, (title, level, _start, end) in enumerate(headings):
        if title != target:
            continue
        section_end = len(structural)
        for _next_title, next_level, next_start, _next_end in headings[index + 1:]:
            if next_level <= level:
                section_end = next_start
                break
        return structural[end:section_end].strip()
    return None


def text_before_heading(text: str, heading: str) -> str:
    target = normalized_heading(heading)
    for title, _level, start, _end in atx_headings(text, strip_fences=False):
        if title == target:
            return text[:start]
    return text


def read_text_checked(path: Path, errors: list[str], label: str) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"missing {label}")
    except (OSError, UnicodeError) as exc:
        errors.append(f"cannot read {label} as UTF-8: {exc}")
    return None


def load_json(path: Path, errors: list[str], label: str) -> dict[str, Any]:
    text = read_text_checked(path, errors, label)
    if text is None:
        return {}
    try:
        data = strict_json_loads(text)
    except (json.JSONDecodeError, DuplicateJSONKeyError, InvalidJSONConstantError) as exc:
        errors.append(f"invalid JSON in {label}: {exc}")
        return {}
    except (RecursionError, MemoryError) as exc:
        errors.append(f"JSON in {label} is too deeply nested or large: {type(exc).__name__}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"{label} must contain a JSON object")
        return {}
    structure_error = json_structure_error(data)
    if structure_error:
        errors.append(f"{label} {structure_error}")
        return {}
    return data


def manifest_subject_projection(data: dict[str, Any]) -> dict[str, Any]:
    gates = data.get("gates") if isinstance(data.get("gates"), dict) else {}
    subject_gates = {k: v for k, v in gates.items() if k != "independent_review"}
    return {
        "schema_version": data.get("schema_version"),
        "design_object": data.get("design_object"),
        "fidelity": data.get("fidelity"),
        "builder_session_id": data.get("builder_session_id"),
        "request_sha256": data.get("request_sha256"),
        "scope": data.get("scope"),
        "artifacts": data.get("artifacts"),
        "gates": subject_gates,
    }


def subject_hash(root: Path, data: dict[str, Any], errors: list[str]) -> str:
    payload: dict[str, Any] = {
        "manifest": manifest_subject_projection(data),
        "files": {},
    }
    file_roles: dict[Path, set[str]] = {}

    def add_subject_file(path: Path | None, role: str, display: str) -> None:
        if path is None or not path.is_file():
            errors.append(f"cannot compute review subject: missing {display}")
            return
        file_roles.setdefault(path, set()).add(role)

    artifacts = data.get("artifacts")
    if not isinstance(artifacts, dict):
        errors.append("cannot compute review subject: artifacts must be an object")
        return ""
    for name in REQUIRED_ARTIFACTS:
        rel = artifacts.get(name)
        if not nonempty_string(rel):
            errors.append(f"cannot compute review subject: missing artifacts.{name}")
            continue
        add_subject_file(safe_child(root, rel), f"artifact:{name}", f"artifact {rel}")

    gates = data.get("gates")
    if isinstance(gates, dict):
        for gate_name, gate in gates.items():
            if gate_name == "independent_review" or not isinstance(gate, dict):
                continue
            evidence = gate.get("evidence")
            if not isinstance(evidence, list):
                continue
            for ref in evidence:
                if not isinstance(ref, dict):
                    continue
                rel = ref.get("path")
                if nonempty_string(rel):
                    add_subject_file(safe_child(root, rel), f"evidence:{gate_name}", f"gate evidence {rel}")
                attachment = ref.get("attachment")
                if isinstance(attachment, dict) and nonempty_string(attachment.get("path")):
                    attachment_rel = attachment["path"]
                    add_subject_file(
                        safe_child(root, attachment_rel),
                        f"attachment:{gate_name}",
                        f"gate attachment {attachment_rel}",
                    )

    for path, roles in sorted(file_roles.items(), key=lambda item: item[0].as_posix()):
        try:
            relative = path.relative_to(root).as_posix()
            digest = sha256_file(path)
        except (OSError, ValueError) as exc:
            errors.append(f"cannot hash review subject file {path}: {exc}")
            continue
        payload["files"][relative] = {"sha256": digest, "roles": sorted(roles)}
    if errors:
        return ""
    try:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    except (RecursionError, MemoryError, UnicodeError, ValueError) as exc:
        errors.append(f"cannot serialize review subject: {type(exc).__name__}: {exc}")
        return ""
    return sha256_bytes(canonical.encode("utf-8"))


def validate_evidence_reference(root: Path, gate_name: str, ref: Any, errors: list[str]) -> None:
    if not isinstance(ref, dict):
        errors.append(f"gate {gate_name} evidence entries must be objects")
        return
    rel = ref.get("path")
    if not nonempty_string(rel):
        errors.append(f"gate {gate_name} evidence is missing path")
        return
    path = safe_child(root, rel)
    if path is None or not path.is_file():
        errors.append(f"gate {gate_name} evidence path does not exist: {rel}")
        return
    if path.stat().st_size == 0:
        errors.append(f"gate {gate_name} evidence path is empty: {rel}")
        return
    if path.suffix.lower() not in TEXT_EVIDENCE_SUFFIXES:
        errors.append(
            f"gate {gate_name} evidence must use a textual evidence index; "
            f"binary files belong in attachment: {rel}"
        )
        return
    text = read_text_checked(path, errors, f"gate {gate_name} evidence {rel}")
    if text is None:
        return
    section = ref.get("section")
    evidence_id = ref.get("evidence_id")
    json_pointer = ref.get("json_pointer")
    json_pointer_present = isinstance(json_pointer, str)
    locators = [
        nonempty_string(section),
        nonempty_string(evidence_id),
        json_pointer_present,
    ]
    if sum(locators) != 1:
        errors.append(
            f"gate {gate_name} evidence {rel} needs exactly one locator: "
            "section, evidence_id, or json_pointer"
        )
        return
    suffix = path.suffix.lower()
    if nonempty_string(section):
        if suffix != ".md":
            errors.append(f"gate {gate_name} section references require Markdown evidence: {rel}")
        else:
            section_matches = markdown_headings(text).count(normalized_heading(section))
            if section_matches != 1:
                errors.append(
                    f"gate {gate_name} evidence section must resolve exactly once in {rel}: {section}"
                )
    elif nonempty_string(evidence_id):
        if not EVIDENCE_ID_PATTERN.fullmatch(evidence_id):
            errors.append(
                f"gate {gate_name} evidence_id must match PREFIX-### using uppercase letters, digits, or underscores: {evidence_id}"
            )
        elif suffix == ".md":
            structural = markdown_structural_text(text)
            escaped = re.escape(evidence_id)
            patterns = (
                rf"^#{{1,6}}\s+{escaped}(?=\s*$|\s+(?:[—:]\s*)?.+$)",
                rf"^\|\s*{escaped}\s*\|",
                rf"^\s*(?:[-*+]\s+)?{escaped}(?=\s*$|\s+(?:[—:]\s*)?.+$)",
            )
            match_count = sum(len(re.findall(pattern, structural, re.MULTILINE)) for pattern in patterns)
            if match_count != 1:
                errors.append(
                    f"gate {gate_name} evidence_id must resolve to exactly one Markdown anchor in {rel}: {evidence_id}"
                )
        elif suffix == ".html":
            html_ids = re.findall(
                rf"\bid\s*=\s*['\"]{re.escape(evidence_id)}['\"]",
                text,
            )
            if len(html_ids) != 1:
                errors.append(
                    f"gate {gate_name} evidence_id must resolve to exactly one HTML id in {rel}: {evidence_id}"
                )
        else:
            tokens = re.findall(
                rf"(?<![A-Z0-9_-]){re.escape(evidence_id)}(?![A-Z0-9_-])",
                text,
            )
            if len(tokens) != 1:
                errors.append(
                    f"gate {gate_name} evidence_id must resolve to exactly one delimited token in {rel}: {evidence_id}"
                )
    else:
        if suffix != ".json":
            errors.append(f"gate {gate_name} json_pointer requires JSON evidence: {rel}")
        else:
            try:
                json_value = strict_json_loads(text)
            except (json.JSONDecodeError, DuplicateJSONKeyError, InvalidJSONConstantError) as exc:
                errors.append(f"gate {gate_name} evidence is invalid JSON {rel}: {exc}")
            except (RecursionError, MemoryError) as exc:
                errors.append(f"gate {gate_name} JSON evidence is too deeply nested or large {rel}: {type(exc).__name__}")
            else:
                structure_error = json_structure_error(json_value)
                if structure_error:
                    errors.append(f"gate {gate_name} JSON evidence {rel} {structure_error}")
                else:
                    found, _value = resolve_json_pointer(json_value, json_pointer)
                    if not found:
                        errors.append(f"gate {gate_name} json_pointer is invalid or not found in {rel}: {json_pointer}")

    attachment = ref.get("attachment")
    if attachment is None:
        return
    if not isinstance(attachment, dict):
        errors.append(f"gate {gate_name} attachment must be an object")
        return
    attachment_rel = attachment.get("path")
    attachment_hash = attachment.get("sha256")
    if not nonempty_string(attachment_rel) or not isinstance(attachment_hash, str) or not SHA256_PATTERN.fullmatch(attachment_hash):
        errors.append(f"gate {gate_name} attachment needs path and lowercase sha256")
        return
    attachment_path = safe_child(root, attachment_rel)
    if attachment_path is None or not attachment_path.is_file() or attachment_path.stat().st_size == 0:
        errors.append(f"gate {gate_name} attachment does not exist or is empty: {attachment_rel}")
        return
    try:
        actual_hash = sha256_file(attachment_path)
    except OSError as exc:
        errors.append(f"cannot hash gate {gate_name} attachment {attachment_rel}: {exc}")
        return
    if actual_hash != attachment_hash:
        errors.append(f"gate {gate_name} attachment hash mismatch: {attachment_rel}")
    if attachment_rel not in text:
        errors.append(f"gate {gate_name} textual evidence index does not contain attachment path: {attachment_rel}")
    if attachment_hash not in text:
        errors.append(f"gate {gate_name} textual evidence index does not contain attachment hash: {attachment_rel}")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    root = root.resolve()
    data = load_json(root / MANIFEST, errors, MANIFEST)
    if not data:
        return errors

    serialized = json.dumps(data, sort_keys=True)
    if any(marker in serialized for marker in PLACEHOLDERS) or " | " in str(data.get("fidelity", "")):
        errors.append(f"{MANIFEST} still contains template placeholders")

    if data.get("schema_version") != 2:
        errors.append("schema_version must equal 2")
    if not nonempty_string(data.get("design_object")):
        errors.append("design_object must be a non-empty string")
    if not nonempty_string(data.get("builder_session_id")):
        errors.append("builder_session_id must be a non-empty session identifier")

    fidelity = data.get("fidelity")
    if fidelity not in FIDELITY_TO_CLAIM:
        errors.append("fidelity must be one of: " + ", ".join(FIDELITY_TO_CLAIM))

    scope = data.get("scope")
    if not isinstance(scope, dict):
        errors.append("scope must be an object")
        scope = {}
    for key in (
        "decision_levels", "surfaces_scenarios_or_actors",
        "states_and_edge_conditions", "exclusions",
    ):
        if not string_list(scope.get(key)):
            errors.append(f"scope.{key} must be a non-empty list of strings")
    for key in ("has_repeated_families", "has_context_transformations"):
        if not isinstance(scope.get(key), bool):
            errors.append(f"scope.{key} must be boolean")
    repeated = scope.get("repeated_families")
    if scope.get("has_repeated_families") is True and not string_list(repeated):
        errors.append("scope.repeated_families must list each repeated family")
    if scope.get("has_repeated_families") is False and repeated not in ([], None):
        errors.append("scope.repeated_families must be empty when has_repeated_families is false")
    if not nonempty_string(scope.get("definition_of_done")):
        errors.append("scope.definition_of_done must be a non-empty qualified definition")

    artifacts = data.get("artifacts")
    resolved_artifacts: dict[str, Path] = {}
    artifact_texts: dict[str, str] = {}
    artifact_paths: list[Path] = []
    artifact_identities: list[tuple[int, int]] = []
    if not isinstance(artifacts, dict):
        errors.append("artifacts must be an object")
        artifacts = {}
    for name in REQUIRED_ARTIFACTS:
        rel = artifacts.get(name)
        if not nonempty_string(rel):
            errors.append(f"artifacts.{name} must point to evidence")
            continue
        path = safe_child(root, rel)
        if path is None:
            errors.append(f"artifact path escapes project root: {rel}")
            continue
        artifact_paths.append(path)
        resolved_artifacts[name] = path
        if not path.is_file():
            errors.append(f"missing artifact: {rel}")
            continue
        stat = path.stat()
        if stat.st_ino:
            artifact_identities.append((stat.st_dev, stat.st_ino))
        text = read_text_checked(path, errors, f"artifact {rel}")
        if text is None:
            continue
        artifact_texts[name] = text
        if len(text.strip()) < 160:
            errors.append(f"artifact is effectively empty: {rel}")
        if any(marker in text for marker in PLACEHOLDERS):
            errors.append(f"artifact still contains template placeholders: {rel}")
        headings = markdown_headings(text)
        for required in REQUIRED_HEADINGS.get(name, ()):
            heading_count = headings.count(normalized_heading(required))
            if heading_count != 1:
                errors.append(
                    f"artifact {rel} must contain exactly one section: {required} (found {heading_count})"
                )
    if len(artifact_paths) != len(set(artifact_paths)):
        errors.append("required artifacts must resolve to distinct canonical paths")
    if len(artifact_identities) != len(set(artifact_identities)):
        errors.append("required artifacts must be distinct files, not symlink or hardlink aliases")

    request_path = resolved_artifacts.get(REQUEST_FILE)
    if request_path and request_path.is_file():
        try:
            actual_request_hash = sha256_file(request_path)
        except OSError as exc:
            errors.append(f"cannot hash {REQUEST_FILE}: {exc}")
            actual_request_hash = ""
        request_hash = data.get("request_sha256")
        if not isinstance(request_hash, str) or not SHA256_PATTERN.fullmatch(request_hash):
            errors.append("request_sha256 must be a lowercase SHA-256 hex digest")
        elif request_hash != actual_request_hash:
            errors.append("request_sha256 does not match ORIGINAL-REQUEST.md")

    record_data: dict[str, dict[str, str]] = {}
    records = resolved_artifacts.get("DECISION-RECORDS.md")
    records_text = artifact_texts.get("DECISION-RECORDS.md")
    if records and records.is_file() and records_text is not None:
        records_structural = markdown_structural_text(records_text)
        matches = list(RECORD_HEADING_PATTERN.finditer(records_structural))
        if not matches:
            errors.append("DECISION-RECORDS.md contains no `## DR-### — name` record heading")
        for index, match in enumerate(matches):
            record_id = match.group(1).upper()
            if record_id in record_data:
                errors.append(f"duplicate decision record identifier: {record_id}")
                continue
            end = matches[index + 1].start() if index + 1 < len(matches) else len(records_structural)
            block = records_structural[match.end():end]
            fields: dict[str, str] = {}
            for field in REQUIRED_RECORD_FIELDS:
                field_matches = re.findall(
                    rf"^-\s+\*\*{re.escape(field)}:\*\*\s*(.*?)\s*$",
                    block,
                    re.MULTILINE | re.IGNORECASE,
                )
                if len(field_matches) != 1:
                    errors.append(
                        f"decision record {record_id} must contain exactly one field: {field}"
                    )
                elif not field_matches[0].strip():
                    errors.append(f"decision record {record_id} is missing non-empty field: {field}")
                else:
                    fields[field.casefold()] = field_matches[0].strip()
            record_data[record_id] = fields
            record_status = fields.get("status", "").lower()
            if record_status and record_status not in {"open", "provisional", "committed", "validated", "reopened", "blocked", "out-of-scope"}:
                errors.append(f"decision record {record_id} has invalid status: {record_status}")

    decision_map = resolved_artifacts.get("DECISION-MAP.md")
    decision_map_text = artifact_texts.get("DECISION-MAP.md")
    map_nodes: dict[str, tuple[str, str | None]] = {}
    referenced_records: set[str] = set()
    if decision_map and decision_map.is_file() and decision_map_text is not None:
        tree_text = markdown_section(decision_map_text, "Decision tree") or ""
        candidate_lines = [
            line.strip()
            for line in tree_text.splitlines()
            if re.search(r"\bDM-[0-9]{3,}\b", line, re.IGNORECASE)
        ]
        if not candidate_lines:
            errors.append("DECISION-MAP.md contains no DM-### decision nodes")
        for line in candidate_lines:
            dm_tokens = re.findall(r"\bDM-[0-9]{3,}\b", line, re.IGNORECASE)
            dr_tokens = re.findall(r"\bDR-[0-9]{3,}\b", line, re.IGNORECASE)
            if len(dm_tokens) != 1:
                errors.append(f"decision-map node must contain exactly one DM-### identifier: {line}")
                continue
            if len(dr_tokens) > 1:
                errors.append(f"decision-map node may contain at most one DR-### reference: {line}")
                continue
            match = MAP_NODE_PATTERN.match(line)
            if not match:
                errors.append(f"malformed decision-map node; each DM node needs one ID and status on the same line: {line}")
                continue
            node_id = match.group("id").upper()
            status = match.group("status").lower()
            record_id = match.group("record")
            record_id = record_id.upper() if record_id else None
            if dr_tokens and record_id != dr_tokens[0].upper():
                errors.append(f"DR-### reference must appear only in the terminal `(record: DR-###)` field: {line}")
                continue
            if node_id in map_nodes:
                errors.append(f"duplicate decision-map node identifier: {node_id}")
                continue
            map_nodes[node_id] = (status, record_id)
            if status in {"committed", "validated"} and not record_id:
                errors.append(f"{node_id} is {status} but has no DR-### record reference")
            if record_id:
                referenced_records.add(record_id)
                if record_id not in record_data:
                    errors.append(f"{node_id} references missing decision record: {record_id}")
                else:
                    record_status = record_data[record_id].get("status", "").lower()
                    if record_status and record_status != status:
                        errors.append(f"status mismatch: {node_id} is {status}, but {record_id} is {record_status}")
        orphan_records = sorted(set(record_data) - referenced_records)
        if orphan_records:
            errors.append("decision records not referenced by DECISION-MAP.md: " + ", ".join(orphan_records))

    gates = data.get("gates")
    if not isinstance(gates, dict):
        errors.append("gates must be an object")
        gates = {}
    missing = [name for name in REQUIRED_GATES if name not in gates]
    extra = [name for name in gates if name not in REQUIRED_GATES]
    if missing:
        errors.append("missing gates: " + ", ".join(missing))
    if extra:
        errors.append("unknown gates: " + ", ".join(extra))
    for name in REQUIRED_GATES:
        gate = gates.get(name)
        if not isinstance(gate, dict):
            errors.append(f"gate {name} must be an object")
            continue
        status = gate.get("status")
        if status not in {"pass", "not_applicable"}:
            errors.append(f"gate {name} is not complete: {status!r}")
            continue
        if status == "not_applicable":
            if name in NON_WAIVABLE_GATES:
                errors.append(f"gate {name} is non-waivable")
            if not nonempty_string(gate.get("reason")):
                errors.append(f"gate {name} is not_applicable without a reason")
            if name in {"repeated_system_specification", "novel_extension"} and scope.get("has_repeated_families") is not False:
                errors.append(f"gate {name} can be not_applicable only when has_repeated_families is false")
            if name == "context_and_transformation_audit" and scope.get("has_context_transformations") is not False:
                errors.append("context_and_transformation_audit can be not_applicable only when has_context_transformations is false")
            continue
        evidence = gate.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"gate {name} passed without structured evidence")
            continue
        for ref in evidence:
            validate_evidence_reference(root, name, ref, errors)

    subject_errors: list[str] = []
    actual_subject_hash = subject_hash(root, data, subject_errors)
    errors.extend(subject_errors)

    review = data.get("review")
    if not isinstance(review, dict):
        errors.append("review must be an object")
        review = {}
    if review.get("status") != "pass":
        errors.append("independent review status must be pass")
    if review.get("report") != REVIEW_REPORT:
        errors.append(f"review.report must equal {REVIEW_REPORT}")
    if review.get("receipt") != REVIEW_RECEIPT:
        errors.append(f"review.receipt must equal {REVIEW_RECEIPT}")
    blockers = review.get("blocking_findings")
    if not isinstance(blockers, list) or blockers:
        errors.append("review.blocking_findings must be an empty list")

    report_path = root / REVIEW_REPORT
    receipt_path = root / REVIEW_RECEIPT
    if not report_path.is_file():
        errors.append(f"missing independent review report: {REVIEW_REPORT}")
    receipt = load_json(receipt_path, errors, REVIEW_RECEIPT)
    if receipt:
        if receipt.get("schema_version") != 1:
            errors.append("review receipt schema_version must equal 1")
        reviewer = receipt.get("reviewer")
        if not isinstance(reviewer, dict):
            errors.append("review receipt reviewer must be an object")
            reviewer = {}
        reviewer_session = reviewer.get("session_id")
        if not nonempty_string(reviewer_session):
            errors.append("review receipt reviewer.session_id is missing")
        elif reviewer_session == data.get("builder_session_id"):
            errors.append("reviewer session must differ from builder session")
        if reviewer.get("role") != "independent-reviewer":
            errors.append("review receipt reviewer.role must equal independent-reviewer")
        if not nonempty_string(reviewer.get("model")):
            errors.append("review receipt reviewer.model is missing")
        if not nonempty_string(reviewer.get("invocation")):
            errors.append("review receipt reviewer.invocation is missing")
        reviewed_at = receipt.get("reviewed_at")
        try:
            parsed_review_time = datetime.fromisoformat(str(reviewed_at).replace("Z", "+00:00"))
            if parsed_review_time.tzinfo is None or parsed_review_time.utcoffset() is None:
                raise ValueError("timestamp lacks timezone")
        except (ValueError, TypeError):
            errors.append("review receipt reviewed_at must be a timezone-aware ISO-8601 timestamp")
        if receipt.get("disposition") != "pass":
            errors.append("review receipt disposition must be pass")
        receipt_blockers = receipt.get("blocking_findings")
        if not isinstance(receipt_blockers, list) or receipt_blockers:
            errors.append("review receipt blocking_findings must be an empty list")
        if actual_subject_hash and receipt.get("subject_sha256") != actual_subject_hash:
            errors.append("review receipt is stale: subject_sha256 does not match current artifacts and manifest")
        if report_path.is_file():
            try:
                current_report_hash = sha256_file(report_path)
            except OSError as exc:
                errors.append(f"cannot hash {REVIEW_REPORT}: {exc}")
            else:
                if receipt.get("report_sha256") != current_report_hash:
                    errors.append("review receipt report_sha256 does not match INDEPENDENT-REVIEW.md")

    if report_path.is_file():
        report_text = read_text_checked(report_path, errors, REVIEW_REPORT)
        if report_text is not None:
            report_structural = markdown_structural_text(report_text)
            report_headings = markdown_headings(report_structural)
            for required in ("Review scope", "Disposition", "Blocking findings", "Non-blocking findings", "Evidence reviewed"):
                heading_count = report_headings.count(normalized_heading(required))
                if heading_count != 1:
                    errors.append(f"independent review report must contain exactly one section: {required}")
            review_scope_section = markdown_section(report_structural, "Review scope") or ""
            disposition_section = markdown_section(report_structural, "Disposition") or ""
            blocker_section = markdown_section(report_structural, "Blocking findings")
            dispositions = re.findall(
                r"^Disposition:\s*(pass|conditional pass|fail)\s*$",
                disposition_section,
                re.IGNORECASE | re.MULTILINE,
            )
            if len(dispositions) != 1 or dispositions[0].lower() != "pass":
                errors.append("independent review Disposition section must contain exactly one `Disposition: pass`")
            if blocker_section is None or not re.fullmatch(r"None\.?", blocker_section.strip(), re.IGNORECASE):
                errors.append("a passing independent review must contain only `None` under Blocking findings")
            declared_subjects = re.findall(
                r"^-\s*Subject hash reviewed:\s*([0-9a-f]{64})\s*$",
                review_scope_section,
                re.IGNORECASE | re.MULTILINE,
            )
            if len(declared_subjects) != 1:
                errors.append("independent review report must declare exactly one reviewed subject SHA-256")
            elif receipt and declared_subjects[0].lower() != str(receipt.get("subject_sha256", "")).lower():
                errors.append("independent review report subject hash does not match review receipt")
            declared_reviewers = re.findall(
                r"^-\s*Reviewer session:\s*(\S+)\s*$",
                review_scope_section,
                re.IGNORECASE | re.MULTILINE,
            )
            receipt_reviewer = receipt.get("reviewer", {}) if isinstance(receipt.get("reviewer"), dict) else {}
            if len(declared_reviewers) != 1:
                errors.append("independent review report must declare exactly one reviewer session")
            elif receipt and declared_reviewers[0] != receipt_reviewer.get("session_id"):
                errors.append("independent review report reviewer session does not match review receipt")

    completion = data.get("completion")
    if not isinstance(completion, dict):
        errors.append("completion must be an object")
        completion = {}
    if completion.get("allowed") is not True:
        errors.append("completion.allowed must be true")
    completion_blockers = completion.get("blockers")
    if not isinstance(completion_blockers, list) or completion_blockers:
        errors.append("completion.blockers must be an empty list")
    expected = FIDELITY_TO_CLAIM.get(fidelity)
    if completion.get("qualified_claim") != expected:
        errors.append(f"completion.qualified_claim must equal {expected!r} for fidelity {fidelity!r}")

    return errors


def main(argv: list[str]) -> int:
    subject_mode = False
    args = list(argv[1:])
    if args and args[0] == "--subject-hash":
        subject_mode = True
        args.pop(0)
    if len(args) > 1:
        print("usage: validate_design_completion.py [--subject-hash] [project-root]", file=sys.stderr)
        return 2
    root = (Path(args[0]) if args else Path.cwd()).resolve()
    if subject_mode:
        errors: list[str] = []
        data = load_json(root / MANIFEST, errors, MANIFEST)
        digest = subject_hash(root, data, errors) if data else ""
        if errors:
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1
        print(digest)
        return 0
    errors = validate(root)
    if errors:
        print("DESIGN COMPLETION: BLOCKED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("DESIGN COMPLETION: CONTRACT PASSED")
    print("This verifies structure, consistency, and review freshness—not design quality, evidence truth, or reviewer independence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
