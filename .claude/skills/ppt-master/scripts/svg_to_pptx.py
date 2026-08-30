#!/usr/bin/env python3
"""PPT Master - SVG to PPTX Tool (guarded thin wrapper).

Validates the repository-level presentation entry gate **before** importing the
PPTX conversion engine. This ordering is intentional: a missing dependency must
never mask a missing template-selection record.

New decks must carry a real template selection record; direct/resume routes that
legitimately bypass the picker must carry a documented exemption record instead.
"""

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from console_encoding import configure_utf8_stdio
from template_gate import validate_project_gate
from storyline_gate import (
    project_requires_storyline_gate,
    validate_project_gate as validate_storyline_project_gate,
)

configure_utf8_stdio()


def _gate_project_from_argv(argv: list[str]) -> int:
    if not argv or argv[0] in {"-h", "--help"}:
        return 0
    project_path = argv[0]
    errors = validate_project_gate(project_path)
    if errors:
        print("[template-gate] EXPORT BLOCKED", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        print(
            "  Complete the template + production-preset selection gate before export.",
            file=sys.stderr,
        )
        return 1

    storyline_errors = (
        validate_storyline_project_gate(project_path)
        if project_requires_storyline_gate(project_path)
        else []
    )
    if storyline_errors:
        print("[storyline-gate] EXPORT BLOCKED", file=sys.stderr)
        for error in storyline_errors:
            print(f"  - {error}", file=sys.stderr)
        print(
            "  Present the slide-by-slide storyline/content preview, apply user revisions, "
            "and record explicit user approval before export.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == '__main__':
    gate_status = _gate_project_from_argv(sys.argv[1:])
    if gate_status:
        raise SystemExit(gate_status)
    from svg_to_pptx import main
    raise SystemExit(main())
