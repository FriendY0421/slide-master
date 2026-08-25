#!/usr/bin/env python3
"""Build the self-contained interactive template gallery intended to render inline in ChatGPT.

The output is one HTML file with no localhost/server dependency. Registered SVG previews and
package-local assets are embedded as data URIs so the conversation attachment can render cards,
open a modal with up to six real examples, and show the final selected template id.
"""
from __future__ import annotations

import argparse
import base64
import html
import json
import mimetypes
import re
import urllib.parse
from pathlib import Path

import template_gallery as legacy
import template_gallery_context as context
import template_catalog as catalog_core

ASSET_URL_RE = re.compile(r'(["\'])/asset\?path=([^"\']+)\1')


def _data_uri(data: bytes, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(data).decode("ascii")


def _self_contained_svg(entry: dict, svg_path: str, lang: str, ref: str | None) -> str:
    svg = catalog_core.preview_svg(entry, svg_path, lang, ref)

    def repl(match: re.Match) -> str:
        repo_path = urllib.parse.unquote(match.group(2))
        try:
            data = legacy._read_bytes(repo_path, ref)
        except FileNotFoundError:
            return match.group(0)
        mime = mimetypes.guess_type(repo_path)[0] or "application/octet-stream"
        return match.group(1) + _data_uri(data, mime) + match.group(1)

    return ASSET_URL_RE.sub(repl, svg)


def _preview_data_uri(entry: dict, svg_path: str, lang: str, ref: str | None) -> str:
    svg = _self_contained_svg(entry, svg_path, lang, ref)
    return _data_uri(svg.encode("utf-8"), "image/svg+xml")


def _payload(entry: dict, ref: str | None, recommended: set[str], lang: str) -> dict:
    previews = []
    for path, label in catalog_core.preview_items(entry, ref, limit=6):
        previews.append({"label": label, "src": _preview_data_uri(entry, path, lang, ref)})
    return {
        "id": entry["key"],
        "name": entry["display_name"],
        "cat": "완성형 Deck" if entry["template_kind"] == "deck" else "구조형 Layout",
        "color": entry.get("primary_color", "#64748b"),
        "summary": entry.get("summary", ""),
        "rec": entry["key"] in recommended,
        "previews": previews,
    }


def build_html(source: str, purpose: str, lang: str = "ko", limit: int = 10) -> str:
    ref, source_label = legacy._resolve_source(source)
    catalog = catalog_core.load_catalog(ref)
    inferred = context.infer_categories(purpose)
    shortlist, recommended = catalog_core.shortlist(catalog, purpose, inferred, max(1, limit))
    cards = [_payload(entry, ref, set(recommended), lang) for entry in shortlist]
    cards_json = json.dumps(cards, ensure_ascii=False).replace("</", "<\\/")
    purpose_html = html.escape(purpose or "새 프레젠테이션")
    source_html = html.escape(source_label)

    return f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Slide Master Template Gallery</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#f3f6fa;color:#0f172a;font-family:Pretendard,'Malgun Gothic','Noto Sans CJK KR','Noto Sans KR',Arial,sans-serif}}
main{{max-width:1480px;margin:auto;padding:30px}}.hero{{background:linear-gradient(135deg,#111827,#1e3a8a,#4338ca);color:white;padding:30px;border-radius:26px;box-shadow:0 20px 45px #0f172a25}}
h1{{margin:0 0 12px;font-size:36px}}.hero p{{margin:6px 0;color:#dbeafe;line-height:1.55}}.notice{{background:#fff7ed;color:#9a3412;border:1px solid #fed7aa;border-radius:16px;padding:14px 16px;margin-top:16px;font-weight:700}}
section{{margin-top:30px}}h2{{font-size:24px;margin:0 0 12px}}.sub{{color:#64748b;font-size:14px;margin-bottom:16px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:18px}}
.card{{position:relative;background:#fff;border:1px solid #dbe4ee;border-radius:22px;overflow:hidden;box-shadow:0 8px 24px #0f172a0b;cursor:pointer;transition:.18s}}.card:hover{{transform:translateY(-4px);box-shadow:0 18px 36px #0f172a20}}
.thumb{{aspect-ratio:16/9;background:#e9eef5}}.thumb img{{width:100%;height:100%;object-fit:contain;background:#fff}}.body{{padding:16px 17px 18px}}.title{{font-weight:900;font-size:19px;display:flex;gap:8px;align-items:center}}.dot{{width:12px;height:12px;border-radius:50%}}
.desc{{color:#64748b;font-size:13px;line-height:1.55;margin-top:8px;min-height:42px}}.chips{{display:flex;gap:6px;flex-wrap:wrap;margin-top:12px}}.chip{{font-size:11px;padding:5px 8px;border-radius:999px;background:#f1f5f9;color:#475569}}.badge{{position:absolute;top:12px;left:12px;background:#111827;color:white;border-radius:999px;padding:6px 10px;font-size:11px;font-weight:900}}
dialog{{width:min(1220px,94vw);border:0;border-radius:24px;padding:0;box-shadow:0 30px 90px #0008}}dialog::backdrop{{background:#0f172ab0}}.dh{{padding:20px 22px;border-bottom:1px solid #e2e8f0;display:flex;justify-content:space-between;gap:15px}}.dh h3{{margin:0 0 6px;font-size:27px}}
.detail{{padding:18px 20px;display:grid;grid-template-columns:repeat(3,1fr);gap:14px;background:#f8fafc}}.shot{{border:1px solid #e2e8f0;border-radius:15px;overflow:hidden;background:#fff}}.shot img{{width:100%;aspect-ratio:16/9;object-fit:contain;background:#fff}}.shot b{{display:block;padding:9px 11px;font-size:12px}}
.actions{{padding:16px 20px;display:flex;justify-content:flex-end;gap:10px;align-items:center;flex-wrap:wrap}}button{{border:0;border-radius:13px;padding:12px 18px;font-weight:900;cursor:pointer}}.primary{{background:#3157d5;color:white}}.secondary{{background:#e2e8f0;color:#0f172a}}
.result{{display:none;margin-top:18px;background:#ecfdf5;border:1px solid #bbf7d0;color:#065f46;border-radius:18px;padding:18px;font-size:16px;line-height:1.7}}code{{background:#e2e8f0;padding:3px 6px;border-radius:6px}}@media(max-width:800px){{main{{padding:16px}}.detail{{grid-template-columns:1fr}}h1{{font-size:28px}}}}
</style></head>
<body><main>
<div class="hero"><h1>{purpose_html} · 템플릿 선택</h1>
<p>FAH → GitHub 최신 규칙 → 등록 템플릿 → 실제 미리보기 확인 → 최종 선택 → 선택 템플릿으로 PPT 제작을 시작합니다.</p>
<p>GitHub 기준본 · {source_html}</p>
<div class="notice">선택 전에는 PPTX 생성을 진행하지 않습니다. 카드 클릭 → 상세 예제 확인 → “이 템플릿 선택”을 눌러주세요.</div></div>
<div id="selected" class="result"></div>
<section><h2>추천 템플릿</h2><div class="sub">이번 자료 목적과 맞는 템플릿입니다. 추천은 자동 선택이 아닙니다.</div><div id="recommended" class="grid"></div></section>
<section><h2>1차 선택 후보 {len(cards)}개</h2><div class="sub">각 템플릿은 대표 레이아웃 예제를 최대 6개까지 확인할 수 있습니다.</div><div id="all" class="grid"></div></section>
<section><h2>Free Design</h2><div class="sub">등록 템플릿을 쓰지 않고 새 디자인으로 제작합니다.</div><button class="secondary" onclick="selectTemplate({{id:'free',name:'Free Design'}})">Free Design 선택</button></section>
</main>
<dialog id="dlg"><div class="dh"><div><h3 id="dt"></h3><div id="dd" class="sub"></div></div><button onclick="dlg.close()">닫기</button></div><div id="shots" class="detail"></div><div class="actions"><button class="secondary" onclick="dlg.close()">다른 템플릿 보기</button><button id="use" class="primary">이 템플릿 선택</button></div></dialog>
<script>
const templates={cards_json};let active=null;const dlg=document.getElementById('dlg');
function card(t){{const a=document.createElement('article');a.className='card';if(t.rec){{const b=document.createElement('div');b.className='badge';b.textContent='★ 추천';a.appendChild(b)}}a.innerHTML+=`<div class="thumb"><img src="${{t.previews[0]?.src||''}}"></div><div class="body"><div class="title"><span class="dot" style="background:${{t.color}}"></span>${{t.name}}</div><div class="desc">${{t.summary}}</div><div class="chips"><span class="chip">${{t.cat}}</span><span class="chip">예제 ${{t.previews.length}}개</span><span class="chip">${{t.id}}</span></div></div>`;a.onclick=()=>openDetail(t);return a}}
function openDetail(t){{active=t;document.getElementById('dt').textContent=t.name;document.getElementById('dd').textContent=t.summary+' · 선택 ID: '+t.id;const s=document.getElementById('shots');s.innerHTML='';t.previews.forEach(p=>{{const d=document.createElement('div');d.className='shot';d.innerHTML=`<img src="${{p.src}}"><b>${{p.label}}</b>`;s.appendChild(d)}});dlg.showModal()}}
function selectTemplate(t){{dlg.close();const box=document.getElementById('selected');box.style.display='block';box.innerHTML=`<b>선택 완료:</b> ${{t.name}}<br><b>선택 ID:</b> <code>${{t.id}}</code><br>채팅창에 <b>${{t.id}}</b> 라고 보내주시면 이 템플릿으로 PPT 제작을 이어갑니다.`;navigator.clipboard?.writeText(t.id).catch(()=>{{}});window.scrollTo({{top:0,behavior:'smooth'}})}}
document.getElementById('use').onclick=()=>{{if(active)selectTemplate(active)}};templates.filter(t=>t.rec).forEach(t=>document.getElementById('recommended').appendChild(card(t)));templates.forEach(t=>document.getElementById('all').appendChild(card(t)));
</script></body></html>'''


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build self-contained inline Slide Master template gallery")
    parser.add_argument("--source", choices=("auto", "github", "local"), default="auto")
    parser.add_argument("--purpose", nargs="+", default=[])
    parser.add_argument("--lang", choices=("ko", "en"), default="ko")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    purpose = " ".join(args.purpose).strip()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_html(args.source, purpose, args.lang, max(1, args.limit)), encoding="utf-8")
    print(f"INLINE_TEMPLATE_GALLERY={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
