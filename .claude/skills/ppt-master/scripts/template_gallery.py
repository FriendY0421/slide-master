#!/usr/bin/env python3
"""Fast HTML template picker for Slide Master new-deck generation.

The gallery reads the registered deck catalog from the latest ``origin/main``
without changing the user's working tree. If GitHub is unreachable it falls
back to the local checkout. It uses only Python's standard library.
"""

from __future__ import annotations

import argparse
import html
import json
import mimetypes
import os
import posixpath
import re
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

REPO_ROOT = Path(__file__).resolve().parents[4]
DECKS_PREFIX = ".claude/skills/ppt-master/templates/decks"
INDEX_PATH = f"{DECKS_PREFIX}/decks_index.json"
SAFE_ID = re.compile(r"^[A-Za-z0-9_.-]+$")
TOKEN_RE = re.compile(r"\{\{([A-Za-z0-9_]+)\}\}")
HREF_RE = re.compile(r"(\b(?:href|xlink:href)=)([\"'])([^\"']+)\2")

SAMPLE_TEXT = {
    "ko": {
        "title": "프레젠테이션 제목",
        "subtitle": "핵심 메시지를 한 줄로 설명합니다",
        "date": "2026. 08",
        "name": "발표자",
        "organization": "회사명",
        "kicker": "EXECUTIVE BRIEF",
        "generic": "샘플 텍스트",
    },
    "en": {
        "title": "Presentation Title",
        "subtitle": "A concise line that explains the key message",
        "date": "2026. 08",
        "name": "Presenter",
        "organization": "Organization",
        "kicker": "EXECUTIVE BRIEF",
        "generic": "Sample text",
    },
}


def _git(args: list[str], *, binary: bool = False, timeout: int = 12):
    kwargs = {
        "cwd": REPO_ROOT,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "timeout": timeout,
        "check": False,
    }
    if not binary:
        kwargs.update({"text": True, "encoding": "utf-8", "errors": "replace"})
    return subprocess.run(["git", *args], **kwargs)


def _resolve_source(mode: str) -> tuple[str | None, str]:
    if mode == "local":
        return None, "local checkout"
    try:
        fetched = _git(["fetch", "origin", "main:refs/remotes/origin/main", "--quiet"], timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        fetched = None
    if fetched is not None and fetched.returncode == 0:
        return "origin/main", "GitHub origin/main"
    if mode == "github":
        raise RuntimeError("Could not refresh origin/main from GitHub")
    return None, "local checkout (GitHub unavailable)"


def _read_text(repo_path: str, ref: str | None) -> str:
    if ref:
        proc = _git(["show", f"{ref}:{repo_path}"])
        if proc.returncode != 0:
            raise FileNotFoundError(repo_path)
        return proc.stdout
    return (REPO_ROOT / Path(repo_path)).read_text(encoding="utf-8-sig")


def _read_bytes(repo_path: str, ref: str | None) -> bytes:
    if ref:
        proc = _git(["show", f"{ref}:{repo_path}"], binary=True)
        if proc.returncode != 0:
            raise FileNotFoundError(repo_path)
        return proc.stdout
    return (REPO_ROOT / Path(repo_path)).read_bytes()


def _list_repo_files(prefix: str, ref: str | None) -> list[str]:
    if ref:
        proc = _git(["ls-tree", "-r", "--name-only", ref, "--", prefix])
        if proc.returncode != 0:
            return []
        return [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    root = REPO_ROOT / Path(prefix)
    if not root.exists():
        return []
    return [p.relative_to(REPO_ROOT).as_posix() for p in root.rglob("*") if p.is_file()]


def _catalog(ref: str | None) -> dict[str, dict]:
    raw = json.loads(_read_text(INDEX_PATH, ref))
    if not isinstance(raw, dict):
        raise ValueError("decks_index.json must contain an object")
    return {k: v for k, v in raw.items() if SAFE_ID.fullmatch(k) and isinstance(v, dict)}


_PREVIEW_GROUPS = (
    ("표지", ("cover", "title")),
    ("목차 · 섹션", ("agenda", "toc", "chapter", "section", "notice")),
    ("본문", ("content", "split", "feature", "keyword", "thesis")),
    ("데이터 · KPI", ("stat", "trend", "chart", "table", "evidence", "segment", "donut", "bar", "line")),
    ("비교 · 비주얼", ("comparison", "image", "exhibit", "quote")),
    ("마무리", ("ending", "closing")),
)


def _all_preview_files(deck_id: str, ref: str | None) -> list[str]:
    prefix = f"{DECKS_PREFIX}/{deck_id}/templates"
    return sorted(path for path in _list_repo_files(prefix, ref) if path.lower().endswith(".svg"))


def _preview_label(path: str) -> str:
    stem = Path(path).stem.lower()
    specific = (("표지",("cover","title")),("목차",("agenda","toc")),("챕터 · 섹션",("chapter","section")),("안내",("notice",)),("키워드 스택",("keyword",)),("논리 체인",("thesis",)),("근거 매트릭스",("evidence",)),("트렌드",("trend",)),("핵심 Exhibit",("exhibit",)),("KPI · 지표",("stat",)),("막대 차트",("bar_chart",)),("라인 차트",("line_chart",)),("도넛 차트",("donut_chart",)),("비교",("comparison",)),("이미지",("image",)),("테이블",("table",)),("세그먼트",("segment",)),("차트",("chart",)),("분할 본문",("split",)),("특징 그리드",("feature",)),("인용",("quote",)),("마무리",("ending","closing")),("본문",("content",)))
    for label,words in specific:
        if any(word in stem for word in words): return label
    clean=re.sub(r"^\d+[a-z]?[_-]*","",Path(path).stem).replace("_"," ").replace("-"," ")
    return clean.strip().title() or "레이아웃"


def _preview_items(deck_id: str, ref: str | None, limit: int = 6) -> list[tuple[str, str]]:
    svgs = _all_preview_files(deck_id, ref)
    chosen: list[tuple[str, str]] = []
    used: set[str] = set()
    for label, words in _PREVIEW_GROUPS:
        match = next((path for path in svgs if path not in used and any(word in Path(path).stem.lower() for word in words)), None)
        if match:
            chosen.append((match, _preview_label(match)))
            used.add(match)
        if len(chosen) >= limit:
            return chosen[:limit]
    for path in svgs:
        if path in used:
            continue
        chosen.append((path, _preview_label(path)))
        if len(chosen) >= limit:
            break
    return chosen


def _preview_file(deck_id: str, ref: str | None) -> str | None:
    items = _preview_items(deck_id, ref, limit=1)
    return items[0][0] if items else None


def _token_value(token: str, lang: str) -> str:
    t = token.upper()
    s = SAMPLE_TEXT.get(lang, SAMPLE_TEXT["en"])
    if "SUBTITLE" in t:
        return s["subtitle"]
    if "TITLE" in t:
        return s["title"]
    if "DATE" in t or "PAGE_LABEL" in t:
        return s["date"]
    if "PRESENTER" in t or "AUTHOR" in t:
        return s["name"]
    if "ORGANIZATION" in t or "BRAND_MARK" in t:
        return s["organization"]
    if "KICKER" in t or "EYEBROW" in t or "CONFIDENTIALITY" in t:
        return s["kicker"]
    return s["generic"]


def _preview_svg(deck_id: str, svg_path: str, lang: str, ref: str | None) -> str:
    raw = _read_text(svg_path, ref)
    raw = TOKEN_RE.sub(lambda m: html.escape(_token_value(m.group(1), lang)), raw)
    workspace = f"{DECKS_PREFIX}/{deck_id}/"
    base = posixpath.dirname(svg_path)

    def rewrite(match: re.Match) -> str:
        value = match.group(3)
        if value.startswith(("data:", "http://", "https://", "#")):
            return match.group(0)
        resolved = posixpath.normpath(posixpath.join(base, value))
        if not resolved.startswith(workspace):
            return match.group(0)
        url = "/asset?path=" + urllib.parse.quote(resolved, safe="")
        return f"{match.group(1)}{match.group(2)}{url}{match.group(2)}"

    return HREF_RE.sub(rewrite, raw)


def _html_page(entries: list[dict], recommended: set[str], source_label: str, purpose: str) -> str:
    cards = json.dumps(entries, ensure_ascii=False).replace("<", "\\u003c")
    rec = json.dumps(sorted(recommended), ensure_ascii=False)
    purpose_html = html.escape(purpose or "새 프레젠테이션")
    source_html = html.escape(source_label)
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Slide Master · 템플릿 갤러리</title>
<style>
:root{{--bg:#eef2f7;--panel:#fff;--ink:#0f172a;--muted:#64748b;--line:#dbe4ee;--accent:#3157d5;--accent2:#7c3aed;--soft:#f8fafc}}
*{{box-sizing:border-box}} body{{margin:0;background:radial-gradient(circle at 8% 0%,#dfe7ff 0,transparent 34%),radial-gradient(circle at 100% 12%,#eee7ff 0,transparent 30%),linear-gradient(180deg,#f7f9fc 0,#edf2f7 100%);color:var(--ink);font-family:Pretendard,"Malgun Gothic",Arial,sans-serif;min-height:100vh}}
body.modal-open{{overflow:hidden}} .wrap{{max-width:1480px;margin:auto;padding:36px 34px 58px}}
.hero{{display:flex;justify-content:space-between;gap:24px;align-items:flex-end;padding:26px 28px;margin-bottom:24px;border:1px solid #ffffffaa;border-radius:24px;background:linear-gradient(135deg,#0f172a 0,#172554 52%,#312e81 100%);color:#fff;box-shadow:0 18px 50px #1e293b24}}
.brand{{font-size:12px;font-weight:800;letter-spacing:1.7px;color:#c7d2fe;margin-bottom:10px}} h1{{font-size:34px;line-height:1.15;margin:0 0 10px;letter-spacing:-1.1px}} .lead{{color:#dbeafe;margin:0;line-height:1.6}} .steps{{white-space:nowrap;font-size:12px;color:#cbd5e1;background:#ffffff12;border:1px solid #ffffff20;border-radius:999px;padding:9px 13px}}
.meta{{display:flex;align-items:center;gap:8px;font-size:12px;color:#64748b;margin:0 4px 18px}} .meta:before{{content:'LIVE';font-size:9px;letter-spacing:.8px;font-weight:900;color:#166534;background:#dcfce7;border-radius:999px;padding:4px 7px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:20px}}
.card{{position:relative;background:linear-gradient(180deg,#fff 0,#fbfdff 100%);border:1px solid #dbe4ee;border-radius:22px;overflow:hidden;box-shadow:0 8px 26px #0f172a0c;cursor:pointer;transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease}}
.card:hover{{transform:translateY(-5px);border-color:#a9b9e8;box-shadow:0 18px 42px #0f172a1c}} .preview{{aspect-ratio:16/9;background:#eef2f7;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:center;overflow:hidden;position:relative}}
.preview img{{width:100%;height:100%;object-fit:contain;background:#fff;transition:transform .25s ease}} .card:hover .preview img{{transform:scale(1.025)}} .free{{width:100%;height:100%;display:grid;place-items:center;background:linear-gradient(135deg,#fff,#edf2f7);color:#475569;font-weight:700;text-align:center}}
.body{{padding:17px 18px 19px}} .title{{font-weight:850;font-size:18px;display:flex;align-items:center;gap:9px;letter-spacing:-.3px}} .desc{{font-size:13px;color:var(--muted);line-height:1.58;margin-top:8px;min-height:42px}} .facts{{display:flex;gap:7px;flex-wrap:wrap;margin-top:13px}} .fact{{font-size:11px;color:#475569;background:#f1f5f9;border:1px solid #e2e8f0;border-radius:999px;padding:5px 8px}} .detail-cta{{margin-top:13px;font-size:12px;font-weight:800;color:#3157d5}}
.chip{{display:inline-block;width:12px;height:12px;border-radius:999px;border:1px solid #0002;box-shadow:0 0 0 3px #00000008}} .badge{{position:absolute;top:14px;left:14px;background:linear-gradient(135deg,#111827,#312e81);color:#fff;padding:7px 10px;border-radius:999px;font-size:11px;font-weight:800;z-index:2;box-shadow:0 7px 18px #0f172a30}}
.guide{{margin:26px 0 0;padding:15px 18px;border:1px solid #dbe4ee;border-radius:16px;background:#ffffffb8;color:#475569;font-size:13px;box-shadow:0 8px 24px #0f172a0b}}
.modal{{position:fixed;inset:0;z-index:100;display:none;align-items:center;justify-content:center;padding:28px}} .modal.open{{display:flex}} .modal-bg{{position:absolute;inset:0;background:#0f172ab8;backdrop-filter:blur(7px)}} .modal-panel{{position:relative;width:min(1320px,96vw);max-height:92vh;overflow:auto;border-radius:24px;background:#f8fafc;box-shadow:0 28px 90px #02061770;border:1px solid #ffffff80}}
.modal-head{{position:sticky;top:0;z-index:4;display:flex;align-items:flex-start;justify-content:space-between;gap:20px;padding:22px 24px 18px;background:#ffffffed;backdrop-filter:blur(14px);border-bottom:1px solid #e2e8f0}} .modal-title{{margin:3px 0 5px;font-size:25px;letter-spacing:-.6px}} .modal-desc{{margin:0;color:#64748b;font-size:13px;line-height:1.55}} .close{{display:grid;place-items:center;width:38px;height:38px;padding:0;border:1px solid #dbe4ee;border-radius:12px;background:#fff;color:#334155;font-size:22px;cursor:pointer}}
.modal-body{{padding:20px 22px 6px}} .modal-facts{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:17px}} .detail-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}} .detail-card{{overflow:hidden;border:1px solid #dbe4ee;border-radius:16px;background:#fff;box-shadow:0 6px 20px #0f172a0c}} .detail-shot{{aspect-ratio:16/9;background:#edf2f7;display:flex;align-items:center;justify-content:center;overflow:hidden}} .detail-shot img{{width:100%;height:100%;object-fit:contain;background:#fff}} .detail-label{{padding:10px 12px;font-size:12px;font-weight:800;color:#475569;border-top:1px solid #eef2f7}}
.modal-actions{{position:sticky;bottom:0;z-index:4;display:flex;justify-content:flex-end;gap:10px;padding:16px 22px 20px;background:#ffffffed;backdrop-filter:blur(14px);border-top:1px solid #e2e8f0}} button{{border:0;border-radius:13px;padding:13px 20px;font-weight:850;font-size:14px;cursor:pointer}} .btn-secondary{{background:#eef2f7;color:#334155}} .btn-primary{{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;box-shadow:0 8px 20px #3157d540}}
@media(max-width:980px){{.detail-grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}}} @media(max-width:760px){{.wrap{{padding:18px 12px 34px}} .hero{{padding:22px 20px;align-items:flex-start;flex-direction:column}} h1{{font-size:28px}} .steps{{white-space:normal}} .grid{{grid-template-columns:1fr}} .modal{{padding:8px}} .modal-panel{{width:100%;max-height:96vh;border-radius:18px}} .detail-grid{{grid-template-columns:1fr}} .modal-actions{{flex-direction:column-reverse}} .modal-actions button{{width:100%}}}}
</style></head><body><main class="wrap">
<section class="hero"><div><div class="brand">SLIDE MASTER · TEMPLATE GALLERY</div><h1>어떤 디자인으로 만들까요?</h1><p class="lead">{purpose_html}<br>카드를 클릭하면 표지뿐 아니라 여러 실제 레이아웃을 비교할 수 있습니다.</p></div><div class="steps">1 디자인 비교&nbsp;&nbsp;→&nbsp;&nbsp;2 템플릿 확정&nbsp;&nbsp;→&nbsp;&nbsp;3 PPT 생성</div></section>
<div class="meta">GitHub 기준본 · {source_html} · 새 템플릿도 대표 레이아웃 자동 반영</div><section id="grid" class="grid"></section>
<div class="guide">템플릿 카드를 클릭하면 <b>표지 · 목차/섹션 · 본문 · 데이터/KPI · 비교/비주얼 · 마무리</b> 등 대표 레이아웃을 큰 화면으로 확인할 수 있습니다.</div>
</main>
<div id="modal" class="modal" aria-hidden="true"><div class="modal-bg" id="modalBg"></div><section class="modal-panel" role="dialog" aria-modal="true"><div class="modal-head"><div><div class="brand" style="color:#6366f1">TEMPLATE DETAIL</div><h2 id="modalTitle" class="modal-title"></h2><p id="modalDesc" class="modal-desc"></p></div><button id="closeModal" class="close" aria-label="닫기">×</button></div><div class="modal-body"><div id="modalFacts" class="modal-facts"></div><div id="detailGrid" class="detail-grid"></div></div><div class="modal-actions"><button id="backBtn" class="btn-secondary">다른 템플릿 보기</button><button id="useBtn" class="btn-primary">이 템플릿으로 계속 →</button></div></section></div>
<script>
const entries={cards}, recommended=new Set({rec}); let active=null;
function freePreview(){{return '<div class="free">FREE DESIGN<br><span style="font-size:12px;font-weight:500;margin-top:6px">템플릿 없이 자유 설계</span></div>'}}
function addFact(host,text){{const f=document.createElement('span');f.className='fact';f.textContent=text;host.appendChild(f)}}
function closeModal(){{document.getElementById('modal').classList.remove('open');document.getElementById('modal').setAttribute('aria-hidden','true');document.body.classList.remove('modal-open')}}
function openModal(e){{active=e;document.getElementById('modalTitle').textContent=e.name;document.getElementById('modalDesc').textContent=e.summary||'';const facts=document.getElementById('modalFacts');facts.innerHTML='';if(e.page_count)addFact(facts,'전체 '+e.page_count+' layouts');addFact(facts,e.id==='free'?'Custom design':'대표 미리보기 '+(e.preview_count||0)+'종');if(recommended.has(e.id))addFact(facts,'★ 이 자료에 추천');const host=document.getElementById('detailGrid');host.innerHTML='';if(e.id==='free'){{const c=document.createElement('div');c.className='detail-card';const shot=document.createElement('div');shot.className='detail-shot';shot.innerHTML=freePreview();const lab=document.createElement('div');lab.className='detail-label';lab.textContent='내용에 맞춰 자유 설계';c.append(shot,lab);host.appendChild(c)}}else{{(e.previews||[]).forEach(v=>{{const c=document.createElement('div');c.className='detail-card';const shot=document.createElement('div');shot.className='detail-shot';const img=document.createElement('img');img.loading='lazy';img.alt=e.name+' '+v.label;img.src='/preview/'+encodeURIComponent(e.id)+'?index='+v.index;shot.appendChild(img);const lab=document.createElement('div');lab.className='detail-label';lab.textContent=v.label;c.append(shot,lab);host.appendChild(c)}})}}document.getElementById('modal').classList.add('open');document.getElementById('modal').setAttribute('aria-hidden','false');document.body.classList.add('modal-open')}}
const grid=document.getElementById('grid');
entries.forEach(e=>{{const card=document.createElement('article');card.className='card';card.dataset.id=e.id;if(recommended.has(e.id)){{const b=document.createElement('div');b.className='badge';b.textContent='★ 추천';card.appendChild(b)}}const p=document.createElement('div');p.className='preview';p.innerHTML=e.id==='free'?freePreview():`<img loading="lazy" src="/preview/${{encodeURIComponent(e.id)}}?index=0" alt="${{e.id}} 미리보기">`;const body=document.createElement('div');body.className='body';const title=document.createElement('div');title.className='title';const chip=document.createElement('span');chip.className='chip';chip.style.background=e.primary_color||'#e2e8f0';title.append(chip,document.createTextNode(e.name));const desc=document.createElement('div');desc.className='desc';desc.textContent=e.summary||'';const facts=document.createElement('div');facts.className='facts';if(e.page_count)addFact(facts,e.page_count+' layouts');if(e.id!=='free')addFact(facts,'대표 '+(e.preview_count||0)+'종');const cta=document.createElement('div');cta.className='detail-cta';cta.textContent=e.id==='free'?'자유 디자인 선택 보기 →':'여러 레이아웃 미리보기 →';body.append(title,desc,facts,cta);card.append(p,body);card.onclick=()=>openModal(e);grid.appendChild(card)}});
document.getElementById('closeModal').onclick=closeModal;document.getElementById('modalBg').onclick=closeModal;document.getElementById('backBtn').onclick=closeModal;document.addEventListener('keydown',e=>{{if(e.key==='Escape')closeModal()}});
const initial=new URLSearchParams(location.search).get('template');if(initial){{const found=entries.find(x=>x.id===initial);if(found)openModal(found)}};
document.getElementById('useBtn').onclick=async()=>{{if(!active)return;const btn=document.getElementById('useBtn');btn.disabled=true;btn.textContent='선택 저장 중…';const r=await fetch('/select',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{template:active.id}})}});if(r.ok){{document.querySelector('.modal-panel').innerHTML='<div style="padding:70px 30px;text-align:center"><div style="font-size:44px;margin-bottom:12px">✓</div><h2>'+active.name+' 선택 완료</h2><p style="color:#64748b">이 창을 닫고 채팅으로 돌아가세요. 선택한 템플릿으로 PPT 제작을 이어갑니다.</p></div>'}}else{{btn.disabled=false;btn.textContent='이 템플릿으로 계속 →'}}}};
</script></body></html>"""


class GalleryState:
    def __init__(self, catalog: dict[str, dict], ref: str | None, lang: str, output: Path):
        self.catalog = catalog
        self.ref = ref
        self.lang = lang
        self.output = output
        self.previews = {deck_id: _preview_items(deck_id, ref) for deck_id in catalog}
        self.selection: dict | None = None
        self.server: ThreadingHTTPServer | None = None


class GalleryHandler(BaseHTTPRequestHandler):
    state: GalleryState
    page_html: str

    def log_message(self, _format, *args):
        return

    def _send(self, status: int, content_type: str, body: bytes):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/":
            self._send(200, "text/html; charset=utf-8", self.page_html.encode("utf-8"))
            return
        if parsed.path.startswith("/preview/"):
            deck_id = urllib.parse.unquote(parsed.path.split("/", 2)[2])
            items = self.state.previews.get(deck_id, [])
            params = urllib.parse.parse_qs(parsed.query)
            try:
                index = int((params.get("index") or ["0"])[0])
            except (TypeError, ValueError):
                index = 0
            if not SAFE_ID.fullmatch(deck_id) or index < 0 or index >= len(items):
                self._send(404, "text/plain; charset=utf-8", b"preview not found")
                return
            svg_path = items[index][0]
            try:
                svg = _preview_svg(deck_id, svg_path, self.state.lang, self.state.ref)
                self._send(200, "image/svg+xml; charset=utf-8", svg.encode("utf-8"))
            except Exception as exc:
                self._send(500, "text/plain; charset=utf-8", str(exc).encode("utf-8"))
            return
        if parsed.path == "/asset":
            params = urllib.parse.parse_qs(parsed.query)
            repo_path = (params.get("path") or [""])[0]
            if not repo_path.startswith(DECKS_PREFIX + "/") or ".." in Path(repo_path).parts:
                self._send(403, "text/plain; charset=utf-8", b"forbidden")
                return
            try:
                body = _read_bytes(repo_path, self.state.ref)
                mime = mimetypes.guess_type(repo_path)[0] or "application/octet-stream"
                self._send(200, mime, body)
            except FileNotFoundError:
                self._send(404, "text/plain; charset=utf-8", b"asset not found")
            return
        self._send(404, "text/plain; charset=utf-8", b"not found")

    def do_POST(self):
        if self.path != "/select":
            self._send(404, "application/json", b"{}")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            choice = str(data.get("template", ""))
        except Exception:
            self._send(400, "application/json", b'{"ok":false}')
            return
        if choice != "free" and choice not in self.state.catalog:
            self._send(400, "application/json", b'{"ok":false}')
            return
        entry = self.state.catalog.get(choice, {})
        result = {
            "template": choice,
            "workspace": None if choice == "free" else f"{DECKS_PREFIX}/{choice}",
            "summary": "Free Design" if choice == "free" else entry.get("summary", ""),
            "selected_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "source_ref": self.state.ref or "local",
        }
        self.state.output.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.state.output.with_suffix(self.state.output.suffix + ".tmp")
        tmp.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, self.state.output)
        self.state.selection = result
        self._send(200, "application/json; charset=utf-8", b'{"ok":true}')
        if self.state.server:
            threading.Thread(target=self.state.server.shutdown, daemon=True).start()


def _entries(catalog: dict[str, dict], ref: str | None) -> list[dict]:
    out = []
    for deck_id, meta in catalog.items():
        items = _preview_items(deck_id, ref)
        if not items:
            continue
        out.append({
            "id": deck_id,
            "name": meta.get("display_name") or deck_id.replace("_", " ").title(),
            "summary": meta.get("summary", ""),
            "primary_color": meta.get("primary_color", "#e2e8f0"),
            "page_count": meta.get("page_count"),
            "preview_count": len(items),
            "previews": [{"index": i, "label": label} for i, (_path, label) in enumerate(items)],
        })
    out.append({"id": "free", "name": "Free Design", "summary": "등록 템플릿 없이 내용에 맞춰 자유롭게 설계", "primary_color": "#e2e8f0", "preview_count": 1, "previews": [{"index": 0, "label": "자유 설계"}]})
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Open the Slide Master HTML template gallery")
    parser.add_argument("--source", choices=("auto", "github", "local"), default="auto")
    parser.add_argument("--recommend", default="", help="Comma-separated deck ids, max 3")
    parser.add_argument("--purpose", nargs="+", default=[])
    parser.add_argument("--lang", choices=("ko", "en"), default="ko")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--timeout", type=int, default=590)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--list", action="store_true", help="Validate/list catalog and exit")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    try:
        ref, source_label = _resolve_source(args.source)
        catalog = _catalog(ref)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    entries = _entries(catalog, ref)
    if args.list:
        print(json.dumps({"source": source_label, "templates": entries}, ensure_ascii=False, indent=2))
        return 0

    recommend = [x.strip() for x in args.recommend.split(",") if x.strip()]
    recommend = [x for x in recommend if x in catalog][:3]
    output = args.output or Path(tempfile.gettempdir()) / f"slide-master-template-selection-{os.getpid()}.json"
    state = GalleryState(catalog, ref, args.lang, output)
    purpose = " ".join(args.purpose).strip() if isinstance(args.purpose, list) else str(args.purpose or "")
    page = _html_page(entries, set(recommend), source_label, purpose)

    GalleryHandler.state = state
    GalleryHandler.page_html = page
    server = ThreadingHTTPServer(("127.0.0.1", args.port), GalleryHandler)
    state.server = server
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    print(f"TEMPLATE_GALLERY_URL={url}", flush=True)
    print(f"TEMPLATE_RESULT_FILE={output}", flush=True)
    print(f"TEMPLATE_SOURCE={source_label}", flush=True)
    if not args.no_browser:
        threading.Timer(0.25, lambda: webbrowser.open(url)).start()
    timer = None
    if args.timeout > 0:
        timer = threading.Timer(args.timeout, server.shutdown)
        timer.daemon = True
        timer.start()
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        if timer:
            timer.cancel()
    if state.selection:
        print("TEMPLATE_SELECTED=" + json.dumps(state.selection, ensure_ascii=False), flush=True)
        return 0
    print("TEMPLATE_SELECTION_TIMEOUT", file=sys.stderr)
    return 124


if __name__ == "__main__":
    raise SystemExit(main())
