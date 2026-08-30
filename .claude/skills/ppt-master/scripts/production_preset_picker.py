#!/usr/bin/env python3
"""Build a self-contained production-preset picker for the standard PPT workflow."""
from __future__ import annotations

import argparse
import html
import json
import re
import webbrowser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
PRESETS_PATH = REPO_ROOT / "docs" / "gpts" / "PRODUCTION_PRESETS.json"

BOOSTS = {
    "executive_brief": ("executive", "management", "decision", "strategy", "future", "leadership", "brief", "임원", "경영", "의사결정", "전략", "미래"),
    "storytelling_proposal": ("problem", "improve", "proposal", "change", "solution", "roadmap", "문제", "개선", "제안", "변화", "해결"),
    "data_insight": ("kpi", "data", "trend", "analysis", "performance", "voc", "quality", "데이터", "분석", "실적", "품질", "추이"),
    "training_guide": ("training", "manual", "guide", "education", "how-to", "교육", "매뉴얼", "가이드", "사용법"),
    "product_showcase": ("product", "service introduction", "brand", "launch", "showcase", "제품", "서비스소개", "브랜드", "행사"),
    "balanced_report": ("report", "status", "sharing", "project", "business", "보고", "현황", "공유", "프로젝트"),
}
def _load_presets() -> list[dict]:
    doc = json.loads(PRESETS_PATH.read_text(encoding="utf-8"))
    return [dict(x) for x in doc.get("presets", []) if isinstance(x, dict) and x.get("id")]


def _rank(presets: list[dict], purpose: str) -> list[dict]:
    text = re.sub(r"\s+", " ", purpose.lower()).strip()
    ranked = []
    for idx, preset in enumerate(presets):
        pid = str(preset["id"])
        score = 0
        for token in BOOSTS.get(pid, ()):
            if token in text:
                score += 8
        for phrase in preset.get("best_for", []):
            if str(phrase).lower() in text:
                score += 4
        if pid == "balanced_report":
            score += 1
        ranked.append((score, -idx, preset))
    ranked.sort(key=lambda x: (-x[0], -x[1]))
    return [p for _score, _idx, p in ranked]


def _esc(value: object) -> str:
    return html.escape(str(value or ""))
def build_html(purpose: str, limit: int = 5) -> str:
    presets = _rank(_load_presets(), purpose)[: max(3, min(limit, 5))]
    cards = []
    for rank, p in enumerate(presets, 1):
        best = ", ".join(str(x) for x in p.get("best_for", []))
        cards.append(
            f'''<button class="card" onclick="pick('{_esc(p['id'])}', '{_esc(p['display_name'])}')">
            <div class="rank">#{rank}</div><h2>{_esc(p['display_name'])}</h2>
            <p>{_esc(p.get('summary'))}</p>
            <div class="meta">{_esc(p.get('slide_range'))} slides · {_esc(p.get('content_density'))}</div>
            <small>{_esc(best)}</small></button>'''
        )
    cards_html = "\n".join(cards)
    return f'''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Slide Master Production Preset</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#f4f7fb;color:#172033;font-family:Pretendard,"Malgun Gothic",Arial,sans-serif}}
main{{max-width:1180px;margin:auto;padding:28px}}header{{background:linear-gradient(135deg,#111827,#3347a8);color:#fff;padding:28px;border-radius:24px}}
header h1{{margin:0 0 8px}}header p{{margin:0;color:#dbe4ff}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px;margin-top:22px}}
.card{{position:relative;text-align:left;border:1px solid #d8deea;background:#fff;border-radius:18px;padding:20px;cursor:pointer;box-shadow:0 8px 24px #1720330b}}
.card:hover{{transform:translateY(-3px);border-color:#6c80dd}}.rank{{font-size:12px;color:#4258bd;font-weight:800}}h2{{margin:8px 0}}p{{line-height:1.5;color:#4f5b70}}
.meta,small{{display:block;color:#68758d;margin-top:8px}}#selected{{display:none;margin-top:20px;padding:18px;border-radius:16px;background:#eaf8ef;border:1px solid #a7dfb7}}
code{{font-size:16px;font-weight:800}}@media(max-width:640px){{main{{padding:14px}}}}
</style></head><body><main><header><h1>Production Preset</h1>
<p>Purpose: {_esc(purpose)}</p></header><section class="grid">{cards_html}</section>
<div id="selected"></div></main><script>
function pick(id,name){{navigator.clipboard?.writeText(id).catch(()=>{{}});const b=document.getElementById('selected');b.style.display='block';b.innerHTML='<b>Selected:</b> '+name+'<br><b>Preset ID:</b> <code>'+id+'</code><br>Paste this preset ID back into ChatGPT.';window.scrollTo({{top:document.body.scrollHeight,behavior:'smooth'}})}}
</script></body></html>'''


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the production-preset picker HTML")
    parser.add_argument("--purpose", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--open", action="store_true")
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_html(args.purpose, args.limit), encoding="utf-8")
    print(f"PRODUCTION_PRESET_PICKER={args.output}")
    if args.open:
        webbrowser.open(args.output.resolve().as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
