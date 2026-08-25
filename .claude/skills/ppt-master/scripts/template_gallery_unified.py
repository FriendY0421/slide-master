#!/usr/bin/env python3
"""Unified Deck+Layout HTML gallery with two-stage detail confirmation."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import tempfile
import threading
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import template_gallery as legacy
import template_gallery_context as context
import template_catalog as catalog_core


class State:
    def __init__(self, catalog: dict[str, dict], ref: str | None, lang: str, output: Path):
        self.catalog = catalog
        self.ref = ref
        self.lang = lang
        self.output = output
        self.previews = {key: catalog_core.preview_items(entry, ref, limit=6) for key, entry in catalog.items()}
        self.selection: dict | None = None
        self.server: ThreadingHTTPServer | None = None


class Handler(BaseHTTPRequestHandler):
    state: State
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
            key = urllib.parse.unquote(parsed.path.split("/", 2)[2])
            entry = self.state.catalog.get(key)
            items = self.state.previews.get(key, [])
            params = urllib.parse.parse_qs(parsed.query)
            try:
                index = int((params.get("index") or ["0"])[0])
            except (TypeError, ValueError):
                index = 0
            if not entry or index < 0 or index >= len(items):
                self._send(404, "text/plain; charset=utf-8", b"preview not found")
                return
            try:
                svg = catalog_core.preview_svg(entry, items[index][0], self.state.lang, self.state.ref)
                self._send(200, "image/svg+xml; charset=utf-8", svg.encode("utf-8"))
            except Exception as exc:
                self._send(500, "text/plain; charset=utf-8", str(exc).encode("utf-8"))
            return
        if parsed.path == "/asset":
            params = urllib.parse.parse_qs(parsed.query)
            repo_path = (params.get("path") or [""])[0]
            roots = tuple(prefix + "/" for _kind, prefix, _index in catalog_core.CATALOG_SOURCES)
            if not repo_path.startswith(roots) or ".." in Path(repo_path).parts:
                self._send(403, "text/plain; charset=utf-8", b"forbidden")
                return
            try:
                body = legacy._read_bytes(repo_path, self.state.ref)
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
            choice = str(data.get("template", "")).strip()
        except Exception:
            self._send(400, "application/json", b'{"ok":false}')
            return

        if choice == "free":
            result = {
                "gate_version": 1,
                "status": "selected",
                "template": "free",
                "template_kind": "free",
                "template_id": "free",
                "workspace": None,
                "summary": "Free Design",
                "selection_method": "html_detail_confirmation",
                "selected_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "source_ref": self.state.ref or "local",
            }
        else:
            entry = self.state.catalog.get(choice)
            if not entry:
                self._send(400, "application/json", b'{"ok":false}')
                return
            result = {
                "gate_version": 1,
                "status": "selected",
                "template": entry["key"],
                "template_kind": entry["template_kind"],
                "template_id": entry["template_id"],
                "workspace": entry["workspace"],
                "summary": entry.get("summary", ""),
                "selection_method": "html_detail_confirmation",
                "selected_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "source_ref": self.state.ref or "local",
            }

        self.state.output.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.state.output.with_suffix(self.state.output.suffix + ".tmp")
        tmp.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, self.state.output)
        self.state.selection = result
        self._send(200, "application/json; charset=utf-8", b'{"ok":true}')
        if self.state.server:
            threading.Thread(target=self.state.server.shutdown, daemon=True).start()


def _payload(entry: dict, state: State, recommended: set[str]) -> dict:
    previews = state.previews.get(entry["key"], [])
    return {
        "key": entry["key"],
        "name": entry["display_name"],
        "kind": entry["template_kind"],
        "summary": entry.get("summary", ""),
        "page_count": entry.get("page_count"),
        "primary_color": entry.get("primary_color", "#64748b"),
        "recommended": entry["key"] in recommended,
        "previews": [{"index": i, "label": label} for i, (_path, label) in enumerate(previews)],
    }


def _page(shortlist: list[dict], all_entries: list[dict], purpose: str, source: str) -> str:
    short_json = json.dumps(shortlist, ensure_ascii=False).replace("<", "\\u003c")
    all_json = json.dumps(all_entries, ensure_ascii=False).replace("<", "\\u003c")
    purpose_json = json.dumps(purpose, ensure_ascii=False)
    source_json = json.dumps(source, ensure_ascii=False)
    return f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Slide Master 템플릿 선택</title>
<style>*{{box-sizing:border-box}}body{{margin:0;background:#f3f6fa;color:#0f172a;font-family:Pretendard,"Malgun Gothic","Noto Sans CJK KR","Noto Sans KR",Arial,sans-serif}}main{{max-width:1500px;margin:auto;padding:28px}}.hero{{background:linear-gradient(135deg,#111827,#1e3a8a,#4338ca);color:white;padding:26px 28px;border-radius:22px}}h1{{margin:0 0 8px}}.muted{{color:#cbd5e1}}.bar{{display:flex;justify-content:space-between;gap:12px;align-items:center;margin:24px 0 14px}}button{{border:0;border-radius:11px;padding:11px 15px;font-weight:800;cursor:pointer}}.secondary{{background:#e2e8f0}}.primary{{background:#3157d5;color:white}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px}}.card{{position:relative;background:white;border:1px solid #dbe4ee;border-radius:18px;overflow:hidden;cursor:pointer;box-shadow:0 7px 20px #0f172a0c}}.card:hover{{transform:translateY(-3px)}}.preview{{aspect-ratio:16/9;background:#eef2f7}}.preview img{{width:100%;height:100%;object-fit:contain;background:white}}.body{{padding:15px}}.title{{font-size:17px;font-weight:850}}.desc{{font-size:12px;color:#64748b;line-height:1.5;min-height:38px;margin-top:6px}}.badge{{position:absolute;top:10px;left:10px;background:#111827;color:white;border-radius:999px;padding:6px 9px;font-size:11px;font-weight:800}}.tag{{display:inline-block;margin-top:9px;margin-right:5px;padding:4px 7px;border-radius:999px;background:#f1f5f9;color:#475569;font-size:11px}}dialog{{width:min(1200px,94vw);border:0;border-radius:20px;padding:0;box-shadow:0 30px 90px #0007}}dialog::backdrop{{background:#0f172ab0}}.dh{{padding:18px 20px;border-bottom:1px solid #e2e8f0;display:flex;justify-content:space-between;gap:14px}}.shots{{padding:18px;display:grid;grid-template-columns:repeat(3,1fr);gap:14px;background:#f8fafc}}.shot{{background:white;border:1px solid #e2e8f0;border-radius:13px;overflow:hidden}}.shot img{{width:100%;aspect-ratio:16/9;object-fit:contain}}.shot b{{display:block;padding:8px 10px;font-size:12px}}.actions{{display:flex;justify-content:flex-end;gap:9px;padding:14px 18px;border-top:1px solid #e2e8f0}}@media(max-width:800px){{main{{padding:14px}}.shots{{grid-template-columns:1fr}}}}</style></head>
<body><main><div class="hero"><h1>어떤 디자인으로 만들까요?</h1><div class="muted" id="purpose"></div><div class="muted" id="source" style="margin-top:6px;font-size:12px"></div></div><div class="bar"><div><b>추천/우선 후보 10개</b> · 카드를 누르면 최대 6개 상세 예제를 확인합니다.</div><button id="allBtn" class="secondary">전체 등록 템플릿 보기</button></div><div id="grid" class="grid"></div></main>
<dialog id="dlg"><div class="dh"><div><h2 id="dt" style="margin:0"></h2><div id="dd" style="color:#64748b;font-size:13px;margin-top:5px"></div></div><button onclick="dlg.close()">닫기</button></div><div id="shots" class="shots"></div><div class="actions"><button class="secondary" onclick="dlg.close()">다른 템플릿 보기</button><button id="use" class="primary">이 템플릿으로 확정 →</button></div></dialog>
<script>const shortlist={short_json},allEntries={all_json};let active=null;document.getElementById('purpose').textContent={purpose_json};document.getElementById('source').textContent='GitHub 기준본 · '+{source_json};const grid=document.getElementById('grid'),dlg=document.getElementById('dlg');
function card(e){{const a=document.createElement('article');a.className='card';if(e.recommended){{const b=document.createElement('div');b.className='badge';b.textContent='★ 추천';a.appendChild(b)}}const p=document.createElement('div');p.className='preview';p.innerHTML=`<img src="/preview/${{encodeURIComponent(e.key)}}?index=0">`;const b=document.createElement('div');b.className='body';b.innerHTML=`<div class="title">${{e.name}}</div><div class="desc">${{e.summary||''}}</div><span class="tag">${{e.kind==='deck'?'완성형 Deck':'구조형 Layout'}}</span>${{e.page_count?`<span class="tag">${{e.page_count}} layouts</span>`:''}}`;a.append(p,b);a.onclick=()=>detail(e);return a}}
function render(list){{grid.innerHTML='';list.forEach(e=>grid.appendChild(card(e)))}}function detail(e){{active=e;document.getElementById('dt').textContent=e.name;document.getElementById('dd').textContent=e.summary||'';const s=document.getElementById('shots');s.innerHTML='';e.previews.forEach(v=>{{const d=document.createElement('div');d.className='shot';d.innerHTML=`<img src="/preview/${{encodeURIComponent(e.key)}}?index=${{v.index}}"><b>${{v.label}}</b>`;s.appendChild(d)}});dlg.showModal()}}render(shortlist);document.getElementById('allBtn').onclick=()=>{{render(allEntries);document.getElementById('allBtn').style.display='none'}};document.getElementById('use').onclick=async()=>{{if(!active)return;const r=await fetch('/select',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{template:active.key}})}});if(r.ok)document.body.innerHTML='<main><div class="hero"><h1>템플릿 선택 완료</h1><div class="muted">선택한 디자인으로 PPT 제작을 계속합니다.</div></div></main>'}};</script></body></html>'''


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Open unified scalable Slide Master template gallery")
    parser.add_argument("--source", choices=("auto", "github", "local"), default="auto")
    parser.add_argument("--purpose", nargs="+", default=[])
    parser.add_argument("--lang", choices=("ko", "en"), default="ko")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--timeout", type=int, default=590)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    try:
        ref, source_label = legacy._resolve_source(args.source)
        catalog = catalog_core.load_catalog(ref)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 2
    purpose = " ".join(args.purpose).strip()
    inferred = context.infer_categories(purpose)
    shortlist_entries, recommended = catalog_core.shortlist(catalog, purpose, inferred, max(1, args.limit))
    state = State(catalog, ref, args.lang, args.output or Path(tempfile.gettempdir()) / f"slide-master-template-selection-v2-{os.getpid()}.json")
    rec = set(recommended)
    short_payload = [_payload(e, state, rec) for e in shortlist_entries]
    all_payload = [_payload(e, state, rec) for e in sorted(catalog.values(), key=lambda x: (x["template_kind"], x["key"]))]
    if args.list:
        print(json.dumps({"source": source_label, "registered": len(all_payload), "shortlist": short_payload, "all_templates": all_payload}, ensure_ascii=False, indent=2))
        return 0
    Handler.state = state
    Handler.page_html = _page(short_payload, all_payload, purpose, source_label)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    state.server = server
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    print(f"TEMPLATE_GALLERY_URL={url}", flush=True)
    print(f"TEMPLATE_RESULT_FILE={state.output}", flush=True)
    if not args.no_browser:
        threading.Timer(0.25, lambda: webbrowser.open(url)).start()
    timer = None
    if args.timeout > 0:
        timer = threading.Timer(args.timeout, server.shutdown)
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
