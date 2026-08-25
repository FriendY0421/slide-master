#!/usr/bin/env python3
"""Record a final user-confirmed deck/layout/free template choice."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from console_encoding import configure_utf8_stdio  # noqa: E402
import template_catalog as catalog_core  # noqa: E402

configure_utf8_stdio()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Record final user-confirmed Slide Master template selection.")
    parser.add_argument("template", help="namespaced key such as deck:mckinsey or layout:ai_ops; bare unique ids remain compatible; 'free' for Free Design")
    parser.add_argument("--purpose", default="")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--confirmed", action="store_true", help="required final-confirmation flag after detail previews")
    args = parser.parse_args(argv)

    if not args.confirmed:
        print("ERROR: final confirmation is required after detail previews; pass --confirmed only after the user confirms", file=sys.stderr)
        return 2

    choice = args.template.strip()
    if choice == "free":
        result = {
            "gate_version": 1,
            "status": "selected",
            "template": "free",
            "template_kind": "free",
            "template_id": "free",
            "workspace": None,
            "summary": "Free Design",
            "purpose": args.purpose,
            "selection_method": "two_stage_explicit_user_confirmation",
            "selected_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "source_ref": "registered-local-catalog-v2",
        }
    else:
        try:
            catalog = catalog_core.load_catalog(None)
        except Exception as exc:
            print(f"ERROR: cannot read unified template catalog ({exc})", file=sys.stderr)
            return 2
        entry = catalog_core.resolve_choice(choice, catalog)
        if not entry:
            print(f"ERROR: unknown or ambiguous template choice: {choice}", file=sys.stderr)
            return 2
        result = {
            "gate_version": 1,
            "status": "selected",
            "template": entry["key"],
            "template_kind": entry["template_kind"],
            "template_id": entry["template_id"],
            "workspace": entry["workspace"],
            "summary": entry.get("summary", ""),
            "purpose": args.purpose,
            "selection_method": "two_stage_explicit_user_confirmation",
            "selected_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "source_ref": "registered-local-catalog-v2",
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    tmp = args.output.with_suffix(args.output.suffix + ".tmp")
    tmp.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, args.output)
    print("TEMPLATE_SELECTED=" + json.dumps(result, ensure_ascii=False))
    print(f"TEMPLATE_RESULT_FILE={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
