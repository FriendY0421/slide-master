#!/usr/bin/env python3
"""Emit a live, chat-renderable template gallery manifest without opening a browser.

This is the canonical helper for conversational hosts such as ChatGPT. It uses
the same catalog, context ranking, and representative SVG selection as the HTML
picker, but returns exact registered workspace/preview paths so the host can
render the real templates inside the current conversation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import template_gallery as legacy
import template_gallery_context as context


def build_manifest(source: str, purpose: str, recommend: str = "") -> dict:
    ref, source_label = legacy._resolve_source(source)
    catalog = legacy._catalog(ref)
    entries, auto_rec, inferred = context.build_entries(catalog, ref, purpose)

    explicit = [
        item.strip()
        for item in recommend.split(",")
        if item.strip() and item.strip() in catalog
    ]
    recommended: list[str] = []
    for deck_id in auto_rec + explicit:
        if deck_id not in recommended:
            recommended.append(deck_id)
        if len(recommended) >= 10:
            break

    manifest_entries: list[dict] = []
    for entry in entries:
        deck_id = entry["id"]
        preview_items = legacy._preview_items(deck_id, ref)
        manifest_entries.append(
            {
                **entry,
                "workspace": f"{legacy.DECKS_PREFIX}/{deck_id}",
                "recommended": deck_id in recommended,
                "preview_path": preview_items[0][0] if preview_items else None,
                "previews": [
                    {"index": index, "label": label, "path": path}
                    for index, (path, label) in enumerate(preview_items)
                ],
            }
        )

    return {
        "schema_version": "1.0",
        "surface": "conversation_inline_first",
        "source": source_label,
        "purpose": purpose,
        "inferred_categories": inferred,
        "recommended": recommended,
        "templates": manifest_entries,
        "free_design": {
            "id": "free",
            "display_name": "Free Design",
            "workspace": None,
            "requires_explicit_user_choice": True,
        },
        "selection_rule": (
            "Render the real registered preview SVGs in the current conversation, "
            "wait for an explicit user choice, then record it with "
            "record_template_choice.py. Do not auto-select."
        ),
        "fallback_rule": (
            "Use template_gallery_context.py HTML/GUI only when the current host "
            "cannot render the gallery inside the conversation."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Emit Slide Master template manifest for in-conversation gallery rendering"
    )
    parser.add_argument("--source", choices=("auto", "github", "local"), default="auto")
    parser.add_argument("--purpose", nargs="+", default=[])
    parser.add_argument("--recommend", default="")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    purpose = " ".join(args.purpose).strip()
    try:
        manifest = build_manifest(args.source, purpose, args.recommend)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 2

    payload = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
        print(f"CHAT_TEMPLATE_MANIFEST={args.output}")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
