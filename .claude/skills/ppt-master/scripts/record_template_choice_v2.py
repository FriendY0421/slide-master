#!/usr/bin/env python3
"""Record a final user-confirmed template choice and optional production preset."""
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
from picker_surface_gate import load_picker_evidence  # noqa: E402

configure_utf8_stdio()
GATE_VERSION = 2
REPO_ROOT = SCRIPTS_DIR.parents[3]
PRESETS_PATH = REPO_ROOT / "docs" / "gpts" / "PRODUCTION_PRESETS.json"


def load_preset(preset_id: str) -> dict | None:
    preset_id = str(preset_id or "").strip()
    if not preset_id:
        return None
    try:
        doc = json.loads(PRESETS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read production presets ({exc})") from exc
    presets = doc.get("presets", []) if isinstance(doc, dict) else []
    matches = [p for p in presets if isinstance(p, dict) and p.get("id") == preset_id]
    if len(matches) != 1:
        raise ValueError(f"unknown production preset: {preset_id}")
    return matches[0]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Record final user-confirmed Slide Master template selection.")
    parser.add_argument("template", help="deck:<id>, layout:<id>, a unique bare id, or 'free'")
    parser.add_argument("--purpose", default="")
    parser.add_argument("--preset", default="", help="optional production preset id from docs/gpts/PRODUCTION_PRESETS.json")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--confirmed", action="store_true", help="required final-confirmation flag")
    parser.add_argument("--picker-evidence", type=Path, default=None, help="required for recommendation flows after a visible picker rendered")
    parser.add_argument("--direct-template", action="store_true", help="only when the user directly specified this registered template before recommendation")
    args = parser.parse_args(argv)

    if not args.confirmed:
        print("ERROR: final confirmation is required; pass --confirmed only after the user confirms", file=sys.stderr)
        return 2
    if args.direct_template and args.picker_evidence is not None:
        print("ERROR: use either --direct-template or --picker-evidence, not both", file=sys.stderr)
        return 2
    if not args.direct_template and args.picker_evidence is None:
        print("ERROR: recommendation flow requires --picker-evidence from a visibly rendered picker", file=sys.stderr)
        return 2
    try:
        preset = load_preset(args.preset)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    picker = None
    selection_surface = "direct_user_specified_template"
    selection_method = "direct_user_specified_template"
    if args.picker_evidence is not None:
        try:
            picker = load_picker_evidence(args.picker_evidence)
        except ValueError as exc:
            print(f"ERROR: invalid picker evidence ({exc})", file=sys.stderr)
            return 2
        selection_surface = picker["surface"]
        selection_method = "picker_then_explicit_user_confirmation"

    choice = args.template.strip()
    if choice == "free":
        template_fields = {"template": "free", "template_kind": "free", "template_id": "free", "workspace": None, "summary": "Free Design"}
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
        template_fields = {
            "template": entry["key"], "template_kind": entry["template_kind"],
            "template_id": entry["template_id"], "workspace": entry["workspace"],
            "summary": entry.get("summary", ""),
        }

    result = {
        "gate_version": GATE_VERSION,
        "status": "selected",
        **template_fields,
        "purpose": args.purpose,
        "production_preset": preset,
        "selection_method": selection_method,
        "selection_surface": selection_surface,
        "picker_evidence": picker,
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
