#!/usr/bin/env python3
"""Context-aware categorized HTML template gallery for new Slide Master decks."""

from __future__ import annotations

import argparse
import html
import json
import tempfile
from pathlib import Path

import template_gallery as legacy

CATEGORY_LABELS = {
    "report": "보고용",
    "education": "학습 · 교육용",
    "notice": "공지 · 안내용",
    "presentation": "발표용",
    "proposal": "제안 · 기획용",
    "data": "데이터 · 실적용",
    "brand_story": "브랜드 · 스토리용",
    "product": "제품 · 서비스 소개용",
    "general": "일반 · 기타",
}
CATEGORY_ORDER = [
    "report", "education", "notice", "presentation", "proposal",
    "data", "brand_story", "product", "general",
]
CATEGORY_KEYWORDS = {
    "report": ("보고", "보고서", "현황", "결과", "분석", "개선", "문제", "의견", "바라는점", "요구사항", "경영", "임원"),
    "education": ("교육", "학습", "강의", "교안", "워크숍", "튜토리얼", "가이드", "설명", "훈련", "신입"),
    "notice": ("공지", "안내", "알림", "주의", "캠페인", "준수", "안전", "업무연락", "전파"),
    "presentation": ("발표", "프레젠테이션", "브리핑", "설명회", "세미나", "회의"),
    "proposal": ("제안", "기획", "전략", "계획", "로드맵", "아이디어", "개선안"),
    "data": ("실적", "성과", "지표", "kpi", "매출", "재무", "분기", "통계", "데이터", "목표"),
    "brand_story": ("브랜드", "스토리", "비전", "미션", "문화", "가치"),
    "product": ("제품", "서비스 소개", "기능", "출시", "상품", "솔루션"),
}


def _norm(value: object) -> str:
    return str(value or "").strip().lower().replace(" ", "")


def infer_categories(purpose: str) -> list[str]:
    text = _norm(purpose)
    scored: list[tuple[int, int, str]] = []
    for order, category in enumerate(CATEGORY_ORDER):
        hits = sum(1 for keyword in CATEGORY_KEYWORDS.get(category, ()) if _norm(keyword) in text)
        if hits:
            scored.append((hits, -order, category))
    scored.sort(reverse=True)
    return [category for _hits, _order, category in scored]


def template_score(deck_id: str, meta: dict, purpose: str, inferred: list[str]) -> int:
    text = _norm(purpose)
    score = 0
    primary = str(meta.get("primary_category") or "general")
    categories = [str(x) for x in meta.get("categories", []) if str(x).strip()]
    keywords = [str(x) for x in meta.get("keywords", []) if str(x).strip()]
    if inferred:
        if primary == inferred[0]:
            score += 10
        for idx, category in enumerate(inferred):
            if category in categories:
                score += max(2, 7 - idx)
    for keyword in keywords:
        if _norm(keyword) and _norm(keyword) in text:
            score += 3
    summary = _norm(meta.get("summary"))
    for token in [t for t in purpose.replace("/", " ").replace(",", " ").split() if len(t) >= 2]:
        if _norm(token) in summary:
            score += 1
    return score


def build_entries(catalog: dict[str, dict], ref: str | None, purpose: str) -> tuple[list[dict], list[str], list[str]]:
    inferred = infer_categories(purpose)
    entries: list[dict] = []
    ranked: list[tuple[int, str]] = []
    for deck_id, meta in catalog.items():
        previews = legacy._preview_items(deck_id, ref)
        if not previews:
            continue
        primary = str(meta.get("primary_category") or "general")
        categories = [str(x) for x in meta.get("categories", []) if str(x).strip()] or [primary]
        score = template_score(deck_id, meta, purpose, inferred)
        entry = {
            "id": deck_id,
            "name": meta.get("display_name") or deck_id.replace("_", " ").title(),
            "summary": meta.get("summary", ""),
            "primary_color": meta.get("primary_color", "#e2e8f0"),
            "page_count": meta.get("page_count"),
            "primary_category": primary,
            "categories": categories,
            "category_label": CATEGORY_LABELS.get(primary, primary),
            "score": score,
            "previews": [{"index": i, "label": label} for i, (_path, label) in enumerate(previews)],
        }
        entries.append(entry)
        if score > 0:
            ranked.append((score, deck_id))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    if ranked:
        top_score = ranked[0][0]
        cutoff = max(3, int(top_score * 0.30 + 0.999))
        recommended = [deck_id for score, deck_id in ranked if score >= cutoff][:10]
    else:
        recommended = []
    return entries, recommended, inferred


def _html_page(entries: list[dict], recommended: list[str], inferred: list[str], source_label: str, purpose: str) -> str:
    payload = json.dumps(entries, ensure_ascii=False).replace("<", "\\u003c")
    rec = json.dumps(recommended, ensure_ascii=False)
    inferred_labels = " · ".join(CATEGORY_LABELS.get(x, x) for x in inferred[:3]) or "문맥 자동 분석"
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Slide Master · Context Template Gallery</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#f3f6fa;color:#0f172a;font-family:Pretendard,'Malgun Gothic',Arial,sans-serif}}main{{max-width:1500px;margin:auto;padding:32px}}.hero{{background:linear-gradient(135deg,#111827,#1e3a8a,#4338ca);color:#fff;padding:28px 30px;border-radius:24px;box-shadow:0 18px 45px #0f172a25}}h1{{margin:0 0 10px;font-size:34px}}.hero p{{margin:4px 0;color:#dbeafe;line-height:1.6}}.meta{{font-size:12px;color:#64748b;margin-top:10px}}section{{margin-top:30px}}h2{{font-size:22px;margin:0 0 14px}}.sub{{color:#64748b;font-size:13px;margin:-6px 0 14px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:18px}}.card{{position:relative;background:#fff;border:1px solid #dbe4ee;border-radius:20px;overflow:hidden;box-shadow:0 8px 24px #0f172a0b;cursor:pointer;transition:.18s}}.card:hover{{transform:translateY(-4px);box-shadow:0 16px 35px #0f172a18}}.preview{{aspect-ratio:16/9;background:#e9eef5;display:flex;align-items:center;justify-content:center;overflow:hidden}}.preview img{{width:100%;height:100%;object-fit:contain;background:#fff}}.body{{padding:16px 17px 18px}}.title{{font-weight:850;font-size:18px;display:flex;gap:8px;align-items:center}}.dot{{width:11px;height:11px;border-radius:50%}}.desc{{color:#64748b;font-size:13px;line-height:1.55;margin-top:7px;min-height:40px}}.chips{{display:flex;gap:6px;flex-wrap:wrap;margin-top:11px}}.chip{{font-size:11px;padding:4px 7px;border-radius:999px;background:#f1f5f9;color:#475569}}.badge{{position:absolute;top:12px;left:12px;z-index:2;background:#111827;color:#fff;border-radius:999px;padding:6px 9px;font-size:11px;font-weight:800}}.empty{{background:#fff;border:1px dashed #cbd5e1;border-radius:16px;padding:18px;color:#64748b}}.free{{background:#fff;border:1px solid #dbe4ee;border-radius:18px;padding:20px;cursor:pointer}}dialog{{width:min(1220px,94vw);border:0;border-radius:22px;padding:0;box-shadow:0 30px 90px #0007}}dialog::backdrop{{background:#0f172ab0}}.dh{{padding:20px 22px;border-bottom:1px solid #e2e8f0;display:flex;justify-content:space-between;gap:15px}}.dh h3{{margin:0 0 5px;font-size:25px}}.detail{{padding:18px 20px;display:grid;grid-template-columns:repeat(3,1fr);gap:14px;background:#f8fafc}}.shot{{border:1px solid #e2e8f0;border-radius:14px;overflow:hidden;background:#fff}}.shot img{{width:100%;aspect-ratio:16/9;object-fit:contain;background:#fff}}.shot b{{display:block;padding:9px 11px;font-size:12px}}.actions{{padding:16px 20px;display:flex;justify-content:flex-end;gap:10px}}button{{border:0;border-radius:12px;padding:12px 18px;font-weight:800;cursor:pointer}}.primary{{background:#3157d5;color:#fff}}@media(max-width:800px){{main{{padding:16px}}.detail{{grid-template-columns:1fr}}h1{{font-size:28px}}}}
</style></head><body><main><div class="hero"><h1>어떤 디자인으로 만들까요?</h1><p>{html.escape(purpose or '새 프레젠테이션')}</p><p><b>문맥 판단:</b> {html.escape(inferred_labels)} · 적합한 템플릿만 최대 10개 추천</p><div class="meta">GitHub 기준본 · {html.escape(source_label)}</div></div><div id="root"></div></main>
<dialog id="dlg"><div class="dh"><div><h3 id="dt"></h3><div id="dd" class="sub"></div></div><button onclick="dlg.close()">닫기</button></div><div id="shots" class="detail"></div><div class="actions"><button onclick="dlg.close()">다른 템플릿 보기</button><button id="use" class="primary">이 템플릿으로 계속 →</button></div></dialog>
<script>const entries={payload},recommended={rec};let active=null;const byId=Object.fromEntries(entries.map(x=>[x.id,x]));const root=document.getElementById('root'),dlg=document.getElementById('dlg');
function card(e,rec=false){{const a=document.createElement('article');a.className='card';if(rec){{const b=document.createElement('div');b.className='badge';b.textContent='★ 이 자료에 추천';a.appendChild(b)}}a.innerHTML+=`<div class="preview"><img loading="lazy" src="/preview/${{encodeURIComponent(e.id)}}?index=0"></div><div class="body"><div class="title"><span class="dot" style="background:${{e.primary_color||'#ddd'}}"></span>${{e.name}}</div><div class="desc">${{e.summary||''}}</div><div class="chips"><span class="chip">${{e.category_label}}</span>${{e.page_count?`<span class="chip">레이아웃 ${{e.page_count}}개</span>`:''}}</div></div>`;a.onclick=()=>openDetail(e);return a}}
function openDetail(e){{active=e;document.getElementById('dt').textContent=e.name;document.getElementById('dd').textContent=e.summary||'';const s=document.getElementById('shots');s.innerHTML='';e.previews.forEach(v=>{{const d=document.createElement('div');d.className='shot';d.innerHTML=`<img src="/preview/${{encodeURIComponent(e.id)}}?index=${{v.index}}"><b>${{v.label}}</b>`;s.appendChild(d)}});dlg.showModal()}}
function section(title,items,sub=''){{const sec=document.createElement('section');sec.innerHTML=`<h2>${{title}}</h2>${{sub?`<div class="sub">${{sub}}</div>`:''}}`;if(!items.length){{const e=document.createElement('div');e.className='empty';e.textContent='현재 이 용도에 등록된 템플릿이 없습니다.';sec.appendChild(e)}}else{{const g=document.createElement('div');g.className='grid';items.forEach(x=>g.appendChild(card(x,recommended.includes(x.id))));sec.appendChild(g)}}root.appendChild(sec)}}
section('이 내용에 가장 잘 맞는 추천 템플릿',recommended.map(id=>byId[id]).filter(Boolean),'추천 개수를 채우지 않고 실제 문맥 적합도가 있는 템플릿만 표시합니다.');
const order={json.dumps(CATEGORY_ORDER, ensure_ascii=False)},labels={json.dumps(CATEGORY_LABELS, ensure_ascii=False)};order.forEach(cat=>section(labels[cat]||cat,entries.filter(e=>(e.primary_category||'general')===cat)));
const fs=document.createElement('section');fs.innerHTML='<h2>자유 설계</h2><div class="free"><b>Free Design</b><div class="sub" style="margin-top:7px">등록 템플릿을 사용하지 않고 내용에 맞춰 새 디자인을 만듭니다.</div></div>';fs.querySelector('.free').onclick=()=>selectTemplate('free');root.appendChild(fs);
async function selectTemplate(id){{const r=await fetch('/select',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{template:id}})}});if(r.ok){{document.body.innerHTML='<main><div class="hero"><h1>템플릿 선택 완료</h1><p>선택한 디자인으로 PPT 제작을 계속합니다.</p></div></main>'}}}}document.getElementById('use').onclick=()=>{{if(active)selectTemplate(active.id)}};
</script></body></html>"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Open context-aware categorized Slide Master template gallery")
    parser.add_argument("--source", choices=("auto", "github", "local"), default="auto")
    parser.add_argument("--purpose", nargs="+", default=[])
    parser.add_argument("--purpose-file", type=Path, default=None, help="UTF-8 text file for purpose/context; preferred on Windows for non-ASCII text")
    parser.add_argument("--recommend", default="", help="Optional additional registered ids; total recommendations remain max 10")
    parser.add_argument("--lang", choices=("ko", "en"), default="ko")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--timeout", type=int, default=590)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)
    try:
        ref, source_label = legacy._resolve_source(args.source)
        catalog = legacy._catalog(ref)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 2
    purpose = args.purpose_file.read_text(encoding="utf-8").strip() if args.purpose_file else " ".join(args.purpose).strip()
    entries, auto_rec, inferred = build_entries(catalog, ref, purpose)
    explicit = [x.strip() for x in args.recommend.split(",") if x.strip() and x.strip() in catalog]
    recommended = []
    for deck_id in auto_rec + explicit:
        if deck_id not in recommended:
            recommended.append(deck_id)
        if len(recommended) >= 10:
            break
    if args.list:
        print(json.dumps({"source": source_label, "purpose": purpose, "inferred_categories": inferred, "recommended": recommended, "templates": entries}, ensure_ascii=False, indent=2))
        return 0
    output = args.output or Path(tempfile.gettempdir()) / "slide-master-template-selection-context.json"
    state = legacy.GalleryState(catalog, ref, args.lang, output)
    legacy.GalleryHandler.state = state
    legacy.GalleryHandler.page_html = _html_page(entries, recommended, inferred, source_label, purpose)
    server = legacy.ThreadingHTTPServer(("127.0.0.1", args.port), legacy.GalleryHandler)
    state.server = server
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    print(f"TEMPLATE_GALLERY_URL={url}", flush=True)
    print(f"TEMPLATE_RESULT_FILE={output}", flush=True)
    print(f"TEMPLATE_SOURCE={source_label}", flush=True)
    if not args.no_browser:
        legacy.threading.Timer(0.25, lambda: legacy.webbrowser.open(url)).start()
    timer = None
    if args.timeout > 0:
        timer = legacy.threading.Timer(args.timeout, server.shutdown)
        timer.daemon = True
        timer.start()
    try:
        server.serve_forever(poll_interval=0.2)
    finally:
        server.server_close()
        if timer:
            timer.cancel()
    if state.selection:
        print("TEMPLATE_SELECTED=" + json.dumps(state.selection, ensure_ascii=False), flush=True)
        return 0
    print("TEMPLATE_SELECTION_TIMEOUT")
    return 124


if __name__ == "__main__":
    raise SystemExit(main())
