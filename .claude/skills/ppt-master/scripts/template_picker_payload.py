#!/usr/bin/env python3
"""Emit a ChatGPT/MCP Apps template-picker payload with real registered previews."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import template_catalog as catalog_core
import template_gallery as legacy
import template_gallery_context as context
import template_gallery_inline_html as inline

REPO_ROOT = Path(__file__).resolve().parents[4]
PRESETS_PATH = REPO_ROOT / "docs" / "gpts" / "PRODUCTION_PRESETS.json"


def _reason(entry: dict, inferred: list[str]) -> str:
    cats = [str(x) for x in entry.get("categories", [])]
    primary = str(entry.get("primary_category") or "general")
    matched = [x for x in inferred if x == primary or x in cats]
    if matched:
        return f"요청 목적의 {', '.join(matched[:2])} 성격과 잘 맞습니다."
    if entry.get("template_kind") == "deck":
        return "완성형 Deck이라 일관된 보고 흐름을 만들기 좋습니다."
    return "구조형 Layout이라 필요한 페이지 구성을 유연하게 조합하기 좋습니다."


def build_payload(source: str, purpose: str, limit: int = 10, lang: str = "ko") -> dict:
    ref, source_label = legacy._resolve_source(source)
    full_catalog = catalog_core.load_catalog(ref)
    catalog = catalog_core.selectable_catalog(full_catalog)
    inferred = context.infer_categories(purpose)
    ranked, recommended = catalog_core.shortlist(catalog, purpose, inferred, max(len(catalog), 1))
    recommended_set = set(recommended)
    shortlist = ranked[: max(1, min(limit, 10))]

    def card(entry: dict) -> dict:
        payload = inline._payload(entry, ref, recommended_set, lang)
        payload.update({
            "key": entry["key"],
            "status": entry.get("status", "ACTIVE"),
            "version": entry.get("version", "1.0"),
            "visibility": entry.get("visibility", "public"),
            "reason": _reason(entry, inferred),
        })
        return payload

    presets_doc = json.loads(PRESETS_PATH.read_text(encoding="utf-8"))
    presets = presets_doc.get("presets", presets_doc if isinstance(presets_doc, list) else [])
    return {
        "schema_version": "1.0",
        "surface": "mcp_apps_picker",
        "source": source_label,
        "purpose": purpose,
        "registered_total": len(full_catalog),
        "selectable_total": len(catalog),
        "recommended_keys": recommended,
        "shortlist": [card(entry) for entry in shortlist],
        "all_templates": [card(entry) for entry in ranked],
        "presets": presets,
        "free_design": {"id": "free", "display_name": "Free Design"},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit Slide Master MCP Apps picker payload")
    parser.add_argument("--source", choices=("auto", "github", "local"), default="github")
    parser.add_argument("--purpose", required=True)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--lang", default="ko")
    args = parser.parse_args()
    try:
        payload = build_payload(args.source, args.purpose, args.limit, args.lang)
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
