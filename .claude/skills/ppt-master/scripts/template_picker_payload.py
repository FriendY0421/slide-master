#!/usr/bin/env python3
"""Emit a ChatGPT/MCP Apps template-picker payload with real registered previews."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import template_catalog as catalog_core
import template_gallery as legacy
import template_gallery_context as context
import template_gallery_inline_html as inline

REPO_ROOT = Path(__file__).resolve().parents[4]
PRESETS_PATH = REPO_ROOT / "docs" / "gpts" / "PRODUCTION_PRESETS.json"


def _reason(entry: dict, inferred: list[str], purpose: str) -> str:
    text = re.sub(r"\s+", "", str(purpose or "").lower())

    def hits(field: str) -> list[str]:
        out = []
        for value in entry.get(field, []) or []:
            norm = re.sub(r"\s+", "", str(value).lower())
            if len(norm) >= 2 and norm in text:
                out.append(str(value))
        return out

    brand = hits("brand_terms")
    intent = hits("document_types") + hits("purpose")
    audience = hits("audience")
    if brand:
        return f"요청의 조직/브랜드 표현 ‘{brand[0]}’과 직접 일치합니다."
    if intent:
        return f"요청 목적 ‘{intent[0]}’과 템플릿 활용 목적이 잘 맞습니다."
    if audience:
        return f"요청 대상 ‘{audience[0]}’에 맞춘 구성입니다."
    cats = [str(x) for x in entry.get("categories", [])]
    primary = str(entry.get("primary_category") or "general")
    matched = [x for x in inferred if x == primary or x in cats]
    if matched:
        return f"요청 목적의 {', '.join(matched[:2])} 성격과 잘 맞습니다."
    if entry.get("template_kind") == "deck":
        return "완성형 Deck이라 일관된 보고 흐름을 만들기 좋습니다."
    return "구조형 Layout이라 필요한 페이지 구성을 유연하게 조합하기 좋습니다."


def _rank_presets(presets: list[dict], purpose: str, limit: int = 5) -> list[dict]:
    compact = re.sub(r"\s+", "", str(purpose or "").lower())
    ranked: list[tuple[int, int, dict]] = []
    for index, preset in enumerate(presets):
        if not isinstance(preset, dict) or not preset.get("id"):
            continue
        searchable = " ".join([
            str(preset.get("id", "")), str(preset.get("display_name", "")),
            str(preset.get("summary", "")), " ".join(str(x) for x in preset.get("best_for", [])),
        ]).lower()
        score = 0
        for token in [x for x in re.split(r"[\s,/·→]+", searchable) if len(x) >= 2]:
            if re.sub(r"\s+", "", token) in compact:
                score += 2
        if any(word in compact for word in ("문제", "개선", "원인", "제안")) and preset.get("id") == "storytelling_proposal":
            score += 8
        if any(word in compact for word in ("실적", "kpi", "voc", "데이터", "추이", "분석")) and preset.get("id") == "data_insight":
            score += 8
        if any(word in compact for word in ("교육", "매뉴얼", "사용법", "가이드")) and preset.get("id") == "training_guide":
            score += 8
        if any(word in compact for word in ("임원", "경영진", "의사결정")) and preset.get("id") == "executive_brief":
            score += 8
        if any(word in compact for word in ("제품", "서비스소개", "브랜드")) and preset.get("id") == "product_showcase":
            score += 8
        ranked.append((score, -index, dict(preset)))
    ranked.sort(key=lambda item: (-item[0], -item[1]))
    selected = [preset for _score, _order, preset in ranked[: max(3, min(limit, 5))]]
    for idx, preset in enumerate(selected):
        preset["recommended_rank"] = idx + 1
    return selected


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
            "reason": _reason(entry, inferred, purpose),
        })
        return payload

    presets_doc = json.loads(PRESETS_PATH.read_text(encoding="utf-8"))
    all_presets = presets_doc.get("presets", presets_doc if isinstance(presets_doc, list) else [])
    presets = _rank_presets(all_presets, purpose, 5)
    return {
        "schema_version": "1.1",
        "surface": "mcp_apps_picker",
        "source": source_label,
        "purpose": purpose,
        "registered_total": len(full_catalog),
        "selectable_total": len(catalog),
        "recommended_keys": recommended,
        "shortlist": [card(entry) for entry in shortlist],
        "all_templates": [card(entry) for entry in ranked],
        "presets": presets,
        "all_presets": all_presets,
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
