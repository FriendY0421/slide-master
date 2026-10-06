#!/usr/bin/env python3
"""Fail-closed project initializer for every new Slide Master deck."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from project_manager import ProjectManager  # noqa: E402
from template_gate import load_selection_result, write_project_gate  # noqa: E402
from storyline_gate import load_storyline_approval, write_project_gate as write_storyline_gate  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Initialize a new deck only after template + production-preset selection is proven.",
    )
    parser.add_argument("project_name")
    parser.add_argument("--format", default="ppt169")
    parser.add_argument("--dir", default=None)
    parser.add_argument("--design-brief", type=Path, help="current workflow_version 2 task brief; binds requested slide count")
    parser.add_argument(
        "--template-selection-result",
        required=True,
        help="validated gate-v3 JSON result from record_template_choice_v2.py (template + production preset)",
    )
    parser.add_argument(
        "--storyline-approval-result",
        required=True,
        help="user-approved slide-by-slide storyline approval JSON from storyline_gate.py",
    )
    args = parser.parse_args(argv)

    try:
        record = load_selection_result(args.template_selection_result)
        storyline_approval = load_storyline_approval(args.storyline_approval_result)
        if args.design_brief:
            from presentation_brief import validate_brief
            from presentation_intake import validate_slide_count
            brief = json.loads(args.design_brief.read_text(encoding="utf-8"))
            report = validate_brief(brief, args.design_brief.resolve().parent)
            if brief.get("workflow_version") != 2 or brief.get("mode") != "builtin" or not report["ready_for_plan"]:
                raise ValueError("Require complete confirmed workflow_version 2 builtin brief")
            if brief.get("template_id") != record.get("template") or brief.get("production_preset_id") != record.get("production_preset"):
                raise ValueError("Brief template/preset differs from confirmed selection")
            errors = validate_slide_count(brief, storyline_approval["slide_count"])
            if errors:
                raise ValueError("; ".join(errors))
            storyline_approval["requested_slide_count"] = brief["slide_count"]
    except (OSError, ValueError) as exc:
        print(f"[new-deck-init] FAIL — {exc}", file=sys.stderr)
        return 2

    manager = ProjectManager()
    try:
        project_path = manager.init_project(args.project_name, args.format, base_dir=args.dir)
        gate_path = write_project_gate(project_path, record)
        storyline_gate_path = write_storyline_gate(project_path, storyline_approval)
    except Exception as exc:
        print(f"[new-deck-init] FAIL — {exc}", file=sys.stderr)
        return 1

    print(f"[new-deck-init] PASS — {project_path}")
    print(f"TEMPLATE_GATE_FILE={gate_path}")
    print(f"STORYLINE_GATE_FILE={storyline_gate_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
