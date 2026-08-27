#!/usr/bin/env python3
"""Build the self-contained interactive template gallery intended to render inline in ChatGPT.

The output is one HTML file with no localhost/server dependency. Every build refreshes the
registered Slide Master catalog from the requested source, embeds the current registered SVG previews
and package-local assets as data URIs, and produces an interactive card gallery with search, filters,
pagination, modal detail previews, Free Design, and final selected-template display.

Production callers should use ``--source github`` so a new PPT request fails closed rather than silently
showing a stale local template catalog when GitHub cannot be refreshed.
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
DEFAULT_PAGE_SIZE = 12
DEFAULT_RECOMMENDED_LIMIT = 6


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
        "template_kind": entry["template_kind"],
        "name": entry["display_name"],
        "cat": "완성형 Deck" if entry["template_kind"] == "deck" else "구조형 Layout",
        "color": entry.get("primary_color", "#64748b"),
        "summary": entry.get("summary", ""),
        "rec": entry["key"] in recommended,
        "previews": previews,
    }


def _source_commit(ref: str | None) -> str:
    if not ref:
        return "local"
    try:
        proc = legacy._git(["rev-parse", ref])
        if proc.returncode == 0:
            return proc.stdout.strip()[:12]
    except Exception:
        pass
    return str(ref)


def build_html(
    source: str,
    purpose: str,
    lang: str = "ko",
    recommendation_limit: int = DEFAULT_RECOMMENDED_LIMIT,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> str:
    ref, source_label = legacy._resolve_source(source)
    catalog = catalog_core.load_catalog(ref)
    selectable = catalog_core.selectable_catalog(catalog)
    inferred = context.infer_categories(purpose)

    # Recommendation is context-ranked, but the selectable library is always the complete live catalog.
    ranked, recommended = catalog_core.shortlist(
        selectable,
        purpose,
        inferred,
        max(len(selectable), 1),
    )
    recommended_keys = recommended[: max(1, recommendation_limit)]
    recommended_set = set(recommended_keys)

    by_key = {entry["key"]: entry for entry in ranked}
    ordered_entries = [by_key[key] for key in recommended_keys if key in by_key]
    ordered_entries.extend(
        entry for entry in ranked
        if entry["key"] not in recommended_set
    )
    cards = [_payload(entry, ref, recommended_set, lang) for entry in ordered_entries]
    cards_json = json.dumps(cards, ensure_ascii=False).replace("</", "<\\/")
    purpose_html = html.escape(purpose or "새 프레젠테이션")
    source_html = html.escape(source_label)
    source_commit = html.escape(_source_commit(ref))
    registered_count = len(cards)
    page_size = max(4, min(int(page_size), 30))

    return f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Slide Master Template Gallery</title>
<style>
:root{{--ink:#0f172a;--muted:#64748b;--line:#dbe4ee;--panel:#fff;--soft:#f3f6fa;--blue:#3157d5}}
*{{box-sizing:border-box}}body{{margin:0;background:linear-gradient(180deg,#f7f9fc,#eef3f9);color:var(--ink);font-family:Pretendard,'Malgun Gothic','Noto Sans CJK KR','Noto Sans KR',Arial,sans-serif}}
main{{max-width:1480px;margin:auto;padding:30px}}.hero{{background:radial-gradient(circle at 92% 10%,#6366f155,transparent 28%),linear-gradient(135deg,#111827,#1e3a8a,#4338ca);color:white;padding:30px;border-radius:26px;box-shadow:0 20px 45px #0f172a25}}
h1{{margin:0 0 12px;font-size:36px}}.hero p{{margin:6px 0;color:#dbeafe;line-height:1.55}}.meta{{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}}.meta span{{font-size:12px;background:#ffffff17;border:1px solid #ffffff24;border-radius:999px;padding:6px 9px}}
.notice{{background:#fff7ed;color:#9a3412;border:1px solid #fed7aa;border-radius:16px;padding:14px 16px;margin-top:16px;font-weight:700}}
section{{margin-top:30px}}h2{{font-size:24px;margin:0 0 12px}}.sub{{color:var(--muted);font-size:14px;margin-bottom:16px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:18px}}
.card{{position:relative;background:var(--panel);border:1px solid var(--line);border-radius:22px;overflow:hidden;box-shadow:0 8px 24px #0f172a0b;cursor:pointer;transition:.18s}}.card:hover{{transform:translateY(-4px);box-shadow:0 18px 36px #0f172a20;border-color:#aebee8}}
.thumb{{aspect-ratio:16/9;background:#e9eef5}}.thumb img{{width:100%;height:100%;object-fit:contain;background:#fff}}.body{{padding:16px 17px 18px}}.title{{font-weight:900;font-size:19px;display:flex;gap:8px;align-items:center}}.dot{{width:12px;height:12px;border-radius:50%;flex:0 0 auto}}
.desc{{color:var(--muted);font-size:13px;line-height:1.55;margin-top:8px;min-height:42px}}.chips{{display:flex;gap:6px;flex-wrap:wrap;margin-top:12px}}.chip{{font-size:11px;padding:5px 8px;border-radius:999px;background:#f1f5f9;color:#475569}}.badge{{position:absolute;top:12px;left:12px;background:#111827;color:white;border-radius:999px;padding:6px 10px;font-size:11px;font-weight:900;z-index:2}}
.toolbar{{display:grid;grid-template-columns:minmax(220px,1fr) auto;gap:12px;align-items:center;margin:12px 0 18px}}.search{{width:100%;border:1px solid var(--line);border-radius:14px;background:#fff;padding:12px 14px;font-size:14px;outline:none}}.search:focus{{border-color:#8da4ea;box-shadow:0 0 0 3px #3157d518}}
.filters{{display:flex;gap:7px;flex-wrap:wrap;justify-content:flex-end}}button{{border:0;border-radius:13px;padding:11px 15px;font-weight:850;cursor:pointer}}.filter{{background:#e8edf5;color:#334155}}.filter.active{{background:#111827;color:#fff}}.primary{{background:var(--blue);color:white}}.secondary{{background:#e2e8f0;color:#0f172a}}
.pager{{display:flex;align-items:center;justify-content:center;gap:9px;margin:22px 0 4px}}.pageinfo{{min-width:120px;text-align:center;color:#475569;font-size:13px;font-weight:700}}.empty{{display:none;background:#fff;border:1px dashed #cbd5e1;border-radius:18px;padding:28px;text-align:center;color:#64748b}}
dialog{{width:min(1220px,94vw);border:0;border-radius:24px;padding:0;box-shadow:0 30px 90px #0008}}dialog::backdrop{{background:#0f172ab0}}.dh{{padding:20px 22px;border-bottom:1px solid #e2e8f0;display:flex;justify-content:space-between;gap:15px}}.dh h3{{margin:0 0 6px;font-size:27px}}
.detail{{padding:18px 20px;display:grid;grid-template-columns:repeat(3,1fr);gap:14px;background:#f8fafc}}.shot{{border:1px solid #e2e8f0;border-radius:15px;overflow:hidden;background:#fff}}.shot img{{width:100%;aspect-ratio:16/9;object-fit:contain;background:#fff}}.shot b{{display:block;padding:9px 11px;font-size:12px}}
.actions{{padding:16px 20px;display:flex;justify-content:flex-end;gap:10px;align-items:center;flex-wrap:wrap}}.result{{display:none;margin-top:18px;background:#ecfdf5;border:1px solid #bbf7d0;color:#065f46;border-radius:18px;padding:18px;font-size:16px;line-height:1.7}}code{{background:#e2e8f0;padding:3px 6px;border-radius:6px}}
@media(max-width:900px){{.toolbar{{grid-template-columns:1fr}}.filters{{justify-content:flex-start}}}}@media(max-width:800px){{main{{padding:16px}}.detail{{grid-template-columns:1fr}}h1{{font-size:28px}}}}
</style></head>
<body><main>
<div class="hero"><h1>{purpose_html} · 템플릿 선택</h1>
<p>FAH → GitHub 최신 Slide Master → 실제 등록 템플릿 → 상세 예제 확인 → 최종 선택 → 그 이후에만 PPT 제작을 시작합니다.</p>
<div class="meta"><span>등록 템플릿 {registered_count}개</span><span>GitHub {source_commit}</span><span>페이지당 {page_size}개</span></div>
<p>GitHub 기준본 · {source_html}</p>
<div class="notice">선택 전에는 PPTX 생성을 진행하지 않습니다. 카드 클릭 → 상세 예제 확인 → “이 템플릿 선택”을 눌러주세요.</div></div>
<div id="selected" class="result"></div>
<section id="recommendedSection"><h2>추천 템플릿</h2><div class="sub">이번 자료 목적과 맞는 상위 후보입니다. 추천은 자동 선택이 아닙니다.</div><div id="recommended" class="grid"></div></section>
<section><h2>전체 등록 템플릿 <span id="countLabel">{registered_count}</span>개</h2><div class="sub">GitHub Slide Master의 현재 등록 템플릿 전체입니다. 검색·필터·페이지 이동이 가능합니다.</div>
<div class="toolbar"><input id="search" class="search" type="search" placeholder="템플릿 이름·설명·ID 검색"><div class="filters"><button class="filter active" data-kind="all">전체</button><button class="filter" data-kind="deck">Deck</button><button class="filter" data-kind="layout">Layout</button></div></div>
<div id="all" class="grid"></div><div id="empty" class="empty">조건에 맞는 템플릿이 없습니다.</div><div class="pager"><button id="prev" class="secondary">← 이전</button><div id="pageInfo" class="pageinfo"></div><button id="next" class="secondary">다음 →</button></div></section>
<section><h2>Free Design</h2><div class="sub">등록 템플릿을 쓰지 않고 새 디자인으로 제작합니다.</div><button class="secondary" onclick="selectTemplate({{id:'free',name:'Free Design'}})">Free Design 선택</button></section>
</main>
<dialog id="dlg"><div class="dh"><div><h3 id="dt"></h3><div id="dd" class="sub"></div></div><button onclick="dlg.close()">닫기</button></div><div id="shots" class="detail"></div><div class="actions"><button class="secondary" onclick="dlg.close()">다른 템플릿 보기</button><button id="use" class="primary">이 템플릿 선택</button></div></dialog>
<script>
const templates={cards_json};const PAGE_SIZE={page_size};let active=null,currentPage=1,currentKind='all',query='';const dlg=document.getElementById('dlg');
function card(t){{const a=document.createElement('article');a.className='card';if(t.rec){{const b=document.createElement('div');b.className='badge';b.textContent='★ 추천';a.appendChild(b)}}a.innerHTML+=`<div class="thumb"><img loading="lazy" src="${{t.previews[0]?.src||''}}"></div><div class="body"><div class="title"><span class="dot" style="background:${{t.color}}"></span>${{t.name}}</div><div class="desc">${{t.summary}}</div><div class="chips"><span class="chip">${{t.cat}}</span><span class="chip">예제 ${{t.previews.length}}개</span><span class="chip">${{t.id}}</span></div></div>`;a.onclick=()=>openDetail(t);return a}}
function openDetail(t){{active=t;document.getElementById('dt').textContent=t.name;document.getElementById('dd').textContent=t.summary+' · 선택 ID: '+t.id;const s=document.getElementById('shots');s.innerHTML='';t.previews.forEach(p=>{{const d=document.createElement('div');d.className='shot';d.innerHTML=`<img loading="lazy" src="${{p.src}}"><b>${{p.label}}</b>`;s.appendChild(d)}});dlg.showModal()}}
function selectTemplate(t){{dlg.close();const box=document.getElementById('selected');box.style.display='block';box.innerHTML=`<b>선택 완료:</b> ${{t.name}}<br><b>선택 ID:</b> <code>${{t.id}}</code><br>채팅창에 <b>${{t.id}}</b> 라고 보내주시면 이 템플릿으로 PPT 제작을 이어갑니다.`;navigator.clipboard?.writeText(t.id).catch(()=>{{}});window.scrollTo({{top:0,behavior:'smooth'}})}}
function filtered(){{const q=query.trim().toLowerCase();return templates.filter(t=>{{if(currentKind!=='all'&&t.template_kind!==currentKind)return false;if(!q)return true;return [t.name,t.summary,t.id,t.cat].join(' ').toLowerCase().includes(q)}})}}
function renderAll(){{const list=filtered();const pages=Math.max(1,Math.ceil(list.length/PAGE_SIZE));currentPage=Math.min(currentPage,pages);const start=(currentPage-1)*PAGE_SIZE;const page=list.slice(start,start+PAGE_SIZE);const host=document.getElementById('all');host.innerHTML='';page.forEach(t=>host.appendChild(card(t)));document.getElementById('empty').style.display=list.length?'none':'block';document.getElementById('countLabel').textContent=list.length;document.getElementById('pageInfo').textContent=`${{currentPage}} / ${{pages}} 페이지`;document.getElementById('prev').disabled=currentPage<=1;document.getElementById('next').disabled=currentPage>=pages}}
function renderRecommended(){{const list=templates.filter(t=>t.rec).slice(0,{max(1, recommendation_limit)});const host=document.getElementById('recommended');host.innerHTML='';list.forEach(t=>host.appendChild(card(t)));document.getElementById('recommendedSection').style.display=list.length?'block':'none'}}
document.getElementById('use').onclick=()=>{{if(active)selectTemplate(active)}};document.getElementById('search').oninput=e=>{{query=e.target.value;currentPage=1;renderAll()}};document.querySelectorAll('.filter').forEach(b=>b.onclick=()=>{{document.querySelectorAll('.filter').forEach(x=>x.classList.remove('active'));b.classList.add('active');currentKind=b.dataset.kind;currentPage=1;renderAll()}});document.getElementById('prev').onclick=()=>{{if(currentPage>1){{currentPage--;renderAll();window.scrollTo({{top:document.getElementById('all').offsetTop-120,behavior:'smooth'}})}}}};document.getElementById('next').onclick=()=>{{const pages=Math.max(1,Math.ceil(filtered().length/PAGE_SIZE));if(currentPage<pages){{currentPage++;renderAll();window.scrollTo({{top:document.getElementById('all').offsetTop-120,behavior:'smooth'}})}}}};renderRecommended();renderAll();
</script></body></html>'''


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build self-contained inline Slide Master template gallery")
    parser.add_argument("--source", choices=("auto", "github", "local"), default="github")
    parser.add_argument("--purpose", nargs="+", default=[])
    parser.add_argument("--lang", choices=("ko", "en"), default="ko")
    parser.add_argument("--recommendation-limit", type=int, default=DEFAULT_RECOMMENDED_LIMIT)
    parser.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    purpose = " ".join(args.purpose).strip()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        build_html(
            args.source,
            purpose,
            args.lang,
            max(1, args.recommendation_limit),
            max(4, args.page_size),
        ),
        encoding="utf-8",
    )
    print(f"INLINE_TEMPLATE_GALLERY={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
