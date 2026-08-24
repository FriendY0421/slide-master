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

configure_utf8_stdio()


def _gate_project_from_argv(argv: list[str]) -> int:
    if not argv or argv[0] in {"-h", "--help"}:
        return 0
    project_path = argv[0]
    errors = validate_project_gate(project_path)
    if not errors:
        return 0
    print("[template-gate] EXPORT BLOCKED", file=sys.stderr)
    for error in errors:
        print(f"  - {error}", file=sys.stderr)
    print(
        "  Complete the HTML/GUI template selection for a new deck, or record a "
        "documented route exemption with template_gate.py before export.",
        file=sys.stderr,
    )
    return 1


if __name__ == '__main__':
    gate_status = _gate_project_from_argv(sys.argv[1:])
    if gate_status:
        raise SystemExit(gate_status)
    from svg_to_pptx import main
    raise SystemExit(main())
