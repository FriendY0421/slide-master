#!/usr/bin/env python3
"""Unified two-stage chat manifest for Slide Master template selection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import template_gallery as legacy
import template_gallery_context as context
import template_catalog as catalog_core


def _entry_payload(entry: dict, ref: str | None, recommended: set[str]) -> dict:
    previews = catalog_core.preview_items(entry, ref, limit=6)
    return {
        "key": entry["key"],
        "id": entry["template_id"],
        "template_kind": entry["template_kind"],
        "name": entry["display_name"],
        "summary": entry.get("summary", ""),
        "workspace": entry["workspace"],
        "canvas_format": entry.get("canvas_format", "ppt169"),
        "page_count": entry.get("page_count"),
        "primary_color": entry.get("primary_color", "#64748b"),
        "recommended": entry["key"] in recommended,
        "preview_path": previews[0][0] if previews else None,
        "preview_count": len(previews),
        "previews": [
            {"index": index, "label": label, "path": path}
            for index, (path, label) in enumerate(previews)
        ],
    }


def build_manifest(source: str, purpose: str, recommend: str = "", limit: int = 10) -> dict:
    ref, source_label = legacy._resolve_source(source)
    catalog = catalog_core.load_catalog(ref)
    inferred = context.infer_categories(purpose)
    shortlist_entries, auto_recommended = catalog_core.shortlist(catalog, purpose, inferred, limit)

    explicit: list[str] = []
    for raw in recommend.split(","):
        resolved = catalog_core.resolve_choice(raw.strip(), catalog)
        if resolved:
            explicit.append(resolved["key"])

    recommended: list[str] = []
    for key in auto_recommended + explicit:
        if key not in recommended:
            recommended.append(key)
        if len(recommended) >= 10:
            break
    recommended_set = set(recommended)

    all_payload = [_entry_payload(entry, ref, recommended_set) for entry in catalog.values()]
    by_key = {entry["key"]: entry for entry in all_payload}
    shortlist_payload = [by_key[entry["key"]] for entry in shortlist_entries if entry["key"] in by_key]

    return {
        "schema_version": "2.0",
        "surface": "conversation_inline_two_stage",
        "source": source_label,
        "purpose": purpose,
        "registered_template_count": len(all_payload),
        "shortlist_target": limit,
        "shortlist_count": len(shortlist_payload),
        "recommended": recommended,
        "shortlist": shortlist_payload,
        "all_templates": sorted(all_payload, key=lambda x: (x["template_kind"], x["key"])),
        "free_design": {
            "key": "free",
            "id": "free",
            "template_kind": "free",
            "display_name": "Free Design",
            "workspace": None,
            "requires_explicit_user_choice": True,
        },
        "selection_flow": {
            "stage_1": "Render up to 10 real registered previews and receive a tentative choice.",
            "stage_2": "Render up to 6 real layouts for that choice and receive final confirmation.",
            "stage_3": "Only then record template selection evidence and continue generation.",
        },
        "render_rule": (
            "Use exact registered SVG sources. If Korean font availability is not positively verified on a raster host, "
            "use English sample tokens inside the preview instead of producing broken Korean glyphs; keep Korean labels outside the image."
        ),
        "fallback_rule": "Use template_gallery_unified.py HTML/GUI only when reliable two-stage in-chat rendering is unavailable.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit scalable unified Slide Master chat gallery manifest")
    parser.add_argument("--source", choices=("auto", "github", "local"), default="auto")
    parser.add_argument("--purpose", nargs="+", default=[])
    parser.add_argument("--recommend", default="")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    purpose = " ".join(args.purpose).strip()
    try:
        manifest = build_manifest(args.source, purpose, args.recommend, max(1, args.limit))
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
