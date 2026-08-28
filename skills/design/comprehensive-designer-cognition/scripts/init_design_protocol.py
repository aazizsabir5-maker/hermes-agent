#!/usr/bin/env python3
"""Initialize the mandatory design-completion protocol in a project.

Existing files are never overwritten.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

TEMPLATE_MAP = {
    "ORIGINAL-REQUEST.md": "ORIGINAL-REQUEST.md",
    "DESIGN-BRIEF.md": "DESIGN-BRIEF.md",
    "DECISION-MAP.md": "DECISION-MAP.md",
    "DECISION-RECORDS.md": "DECISION-RECORDS.md",
    "SYSTEM-SPEC.md": "SYSTEM-SPEC.md",
    "DESIGN-AUDIT.md": "DESIGN-AUDIT.md",
    "VALIDATION-REPORT.md": "VALIDATION-REPORT.md",
    "DESIGN-COMPLETION.json": "DESIGN-COMPLETION.json",
    "project.hermes.md": ".hermes.md",
    "enforcement.json": ".hermes/enforcement.json",
}


def main(argv: list[str]) -> int:
    if len(argv) > 2:
        print("usage: init_design_protocol.py [project-root]", file=sys.stderr)
        return 2
    root = (Path(argv[1]) if len(argv) == 2 else Path.cwd()).resolve()
    if not root.exists() or not root.is_dir():
        print(f"project root is not a directory: {root}", file=sys.stderr)
        return 2
    templates = Path(__file__).resolve().parent.parent / "templates"
    created: list[str] = []
    preserved: list[str] = []
    for source_name, destination_name in TEMPLATE_MAP.items():
        source = templates / source_name
        destination = root / destination_name
        if destination.exists():
            preserved.append(destination_name)
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        created.append(destination_name)
    print("DESIGN PROTOCOL INITIALIZED")
    print("created: " + (", ".join(created) if created else "none"))
    print("preserved: " + (", ".join(preserved) if preserved else "none"))
    print("Next: capture the original request, reconcile the boundary, replace all placeholders, and keep the evidence contract current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
