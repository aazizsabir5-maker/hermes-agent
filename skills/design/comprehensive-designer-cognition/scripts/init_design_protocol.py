#!/usr/bin/env python3
"""Create the single design-decision ledger when it is absent."""

from __future__ import annotations

import argparse
from pathlib import Path


LEDGER_NAME = "DESIGN-DECISIONS.md"
TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / LEDGER_NAME


def initialize(project_root: str | Path) -> tuple[Path, bool]:
    root = Path(project_root).expanduser().resolve(strict=False)
    root.mkdir(parents=True, exist_ok=True)
    ledger = root / LEDGER_NAME
    if ledger.exists() or ledger.is_symlink():
        return ledger, False
    ledger.write_text(TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")
    return ledger, True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", default=".")
    args = parser.parse_args(argv)
    ledger, created = initialize(args.project_root)
    if created:
        print(f"Created {ledger}")
    else:
        print(f"{ledger} already exists; left unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

