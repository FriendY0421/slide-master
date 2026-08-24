#!/usr/bin/env python3
"""Record an explicit user template choice without reopening the HTML gallery."""

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

configure_utf8_stdio()

SKILL_DIR = SCRIPTS_DIR.parent
INDEX_PATH = SKILL_DIR / "templates" / "decks" / "decks_index.json"
DECKS_PREFIX = ".claude/skills/ppt-master/templates/decks"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Record a user-confirmed registered template id.")
    parser.add_argument("template", help="registered deck id, or 'free' only when user explicitly chose Free Design")
    parser.add_argument("--purpose", default="")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        catalog = json.loads(INDEX_PATH.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read deck catalog ({exc})", file=sys.stderr)
        return 2

    choice = args.template.strip()
    if choice != "free" and choice not in catalog:
        print(f"ERROR: unregistered template id: {choice}", file=sys.stderr)
        return 2

    entry = catalog.get(choice, {})
    result = {
        "gate_version": 1,
        "status": "selected",
        "template": choice,
        "workspace": None if choice == "free" else f"{DECKS_PREFIX}/{choice}",
        "summary": "Free Design" if choice == "free" else entry.get("summary", ""),
        "purpose": args.purpose,
        "selection_method": "explicit_user_choice",
        "selected_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "source_ref": "registered-local-catalog",
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
