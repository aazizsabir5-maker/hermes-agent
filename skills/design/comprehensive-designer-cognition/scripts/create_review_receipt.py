#!/usr/bin/env python3
"""Create a freshness-bound independent-review receipt.

This helper standardizes the receipt but cannot prove reviewer independence by
itself. It must be run by the separately delegated reviewer, not the builder.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def load_validator(script_dir: Path):
    path = script_dir / "validate_design_completion.py"
    spec = importlib.util.spec_from_file_location("design_completion_validator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load design completion validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_root")
    parser.add_argument("--reviewer-session-id", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--invocation", default="delegate_task")
    parser.add_argument("--disposition", choices=("pass", "conditional pass", "fail"), required=True)
    parser.add_argument("--blocking-finding", action="append", default=[])
    args = parser.parse_args(argv[1:])

    root = Path(args.project_root).resolve()
    validator = load_validator(Path(__file__).resolve().parent)
    errors: list[str] = []
    manifest = validator.load_json(root / validator.MANIFEST, errors, validator.MANIFEST)
    digest = validator.subject_hash(root, manifest, errors) if manifest else ""
    if manifest and args.reviewer_session_id == manifest.get("builder_session_id"):
        errors.append("reviewer session must differ from builder session")
    report = root / validator.REVIEW_REPORT
    if not report.is_file():
        errors.append(f"missing {validator.REVIEW_REPORT}")
    else:
        report_text = validator.read_text_checked(report, errors, validator.REVIEW_REPORT)
        if report_text is not None:
            report_structural = validator.markdown_structural_text(report_text)
            report_headings = validator.markdown_headings(report_structural)
            for required in ("Review scope", "Disposition", "Blocking findings"):
                if report_headings.count(validator.normalized_heading(required)) != 1:
                    errors.append(f"review report must contain exactly one section: {required}")
            review_scope = validator.markdown_section(report_structural, "Review scope") or ""
            disposition_section = validator.markdown_section(report_structural, "Disposition") or ""
            declared_subjects = re.findall(r"^-\s*Subject hash reviewed:\s*([0-9a-f]{64})\s*$", review_scope, re.I | re.M)
            if len(declared_subjects) != 1 or declared_subjects[0].lower() != digest:
                errors.append("Review scope must declare exactly one current subject SHA-256 before receipt creation")
            declared_reviewers = re.findall(r"^-\s*Reviewer session:\s*(\S+)\s*$", review_scope, re.I | re.M)
            if len(declared_reviewers) != 1 or declared_reviewers[0] != args.reviewer_session_id:
                errors.append("Review scope must declare exactly one reviewer session matching --reviewer-session-id")
            declared_dispositions = re.findall(r"^Disposition:\s*(pass|conditional pass|fail)\s*$", disposition_section, re.I | re.M)
            if len(declared_dispositions) != 1 or declared_dispositions[0].lower() != args.disposition:
                errors.append("Disposition section must declare exactly one disposition matching --disposition")
            if args.disposition == "pass":
                blocker_section = validator.markdown_section(report_structural, "Blocking findings")
                if blocker_section is None or not re.fullmatch(r"None\.?", blocker_section.strip(), re.IGNORECASE):
                    errors.append("a passing report must contain only `None` under Blocking findings")
    if not args.model.strip():
        errors.append("--model must be non-empty")
    if not args.invocation.strip():
        errors.append("--invocation must be non-empty")
    if args.disposition == "pass" and args.blocking_finding:
        errors.append("a pass receipt cannot contain blocking findings")
    if errors:
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    receipt = {
        "schema_version": 1,
        "subject_sha256": digest,
        "report_sha256": validator.sha256_file(report),
        "reviewer": {
            "session_id": args.reviewer_session_id,
            "role": "independent-reviewer",
            "model": args.model,
            "invocation": args.invocation,
        },
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
        "disposition": args.disposition,
        "blocking_findings": args.blocking_finding,
    }
    destination = root / validator.REVIEW_RECEIPT
    destination.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
