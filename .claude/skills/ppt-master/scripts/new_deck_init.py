#!/usr/bin/env python3
"""Fail-closed project initializer for every new Slide Master deck."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from project_manager import ProjectManager  # noqa: E402
from template_gate import load_selection_result, write_project_gate  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Initialize a new deck only after template selection is proven.",
    )
    parser.add_argument("project_name")
    parser.add_argument("--format", default="ppt169")
    parser.add_argument("--dir", default=None)
    parser.add_argument(
        "--template-selection-result",
        required=True,
        help="JSON result returned by template_gallery.py or record_template_choice.py",
    )
    args = parser.parse_args(argv)

    try:
        record = load_selection_result(args.template_selection_result)
    except ValueError as exc:
        print(f"[new-deck-init] FAIL — {exc}", file=sys.stderr)
        return 2

    manager = ProjectManager()
    try:
        project_path = manager.init_project(args.project_name, args.format, base_dir=args.dir)
        gate_path = write_project_gate(project_path, record)
    except Exception as exc:
        print(f"[new-deck-init] FAIL — {exc}", file=sys.stderr)
        return 1

    print(f"[new-deck-init] PASS — {project_path}")
    print(f"TEMPLATE_GATE_FILE={gate_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
