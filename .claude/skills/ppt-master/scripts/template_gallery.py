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
        fetched = _git(["fetch", "origin", "main", "--quiet"], timeout=10)
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


def _preview_file(deck_id: str, ref: str | None) -> str | None:
    prefix = f"{DECKS_PREFIX}/{deck_id}/templates"
    svgs = sorted(path for path in _list_repo_files(prefix, ref) if path.lower().endswith(".svg"))
    return svgs[0] if svgs else None


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
<title>Slide Master · 템플릿 선택</title>
<style>
:root{{--bg:#f4f6f8;--panel:#fff;--ink:#111827;--muted:#64748b;--line:#dbe2ea;--accent:#2563eb}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font-family:Pretendard,"Malgun Gothic",Arial,sans-serif}}
.wrap{{max-width:1420px;margin:auto;padding:34px 28px 48px}} h1{{font-size:30px;margin:0 0 8px}} .lead{{color:var(--muted);margin-bottom:8px}}
.meta{{font-size:12px;color:#94a3b8;margin-bottom:24px}} .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px}}
.card{{position:relative;background:var(--panel);border:2px solid transparent;border-radius:18px;overflow:hidden;box-shadow:0 6px 20px #0f172a0d;cursor:pointer;transition:.15s}}
.card:hover{{transform:translateY(-2px);box-shadow:0 10px 28px #0f172a18}} .card.selected{{border-color:var(--accent);box-shadow:0 0 0 3px #2563eb20}}
.preview{{aspect-ratio:16/9;background:#eef2f7;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:center;overflow:hidden}}
.preview img{{width:100%;height:100%;object-fit:contain;background:#fff}} .free{{width:100%;height:100%;display:grid;place-items:center;background:linear-gradient(135deg,#fff,#edf2f7);color:#475569;font-weight:700}}
.body{{padding:15px 16px 17px}} .title{{font-weight:800;font-size:18px;display:flex;align-items:center;gap:8px}} .desc{{font-size:13px;color:var(--muted);line-height:1.55;margin-top:7px;min-height:40px}}
.chip{{display:inline-block;width:12px;height:12px;border-radius:999px;border:1px solid #0002}} .badge{{position:absolute;top:12px;left:12px;background:#111827;color:#fff;padding:6px 9px;border-radius:999px;font-size:11px;font-weight:700;z-index:2}}
.footer{{position:sticky;bottom:0;margin-top:26px;padding:16px;background:#ffffffee;backdrop-filter:blur(8px);border:1px solid var(--line);border-radius:16px;display:flex;justify-content:space-between;gap:14px;align-items:center}}
.choice{{font-weight:700}} button{{border:0;border-radius:12px;padding:12px 20px;font-weight:800;font-size:14px;cursor:pointer}} #confirm{{background:var(--accent);color:white}} #confirm:disabled{{opacity:.4;cursor:not-allowed}}
@media(max-width:640px){{.wrap{{padding:22px 14px}} .grid{{grid-template-columns:1fr}} .footer{{align-items:stretch;flex-direction:column}}}}
</style></head><body><main class="wrap">
<h1>어떤 템플릿으로 만들까요?</h1><div class="lead">{purpose_html} · 원하는 디자인을 먼저 선택하면 그 템플릿으로만 제작합니다.</div>
<div class="meta">템플릿 기준본: {source_html} · 새로 등록된 템플릿도 자동 반영</div><section id="grid" class="grid"></section>
<div class="footer"><div><div style="font-size:12px;color:#64748b">현재 선택</div><div id="choice" class="choice">선택하지 않음</div></div><button id="confirm" disabled>이 템플릿 사용</button></div>
</main><script>
const entries={cards}, recommended=new Set({rec}); let selected=null;
function freePreview(){{return '<div class="free">FREE DESIGN<br><span style="font-size:12px;font-weight:500;margin-top:6px">템플릿 없이 자유 설계</span></div>'}}
const grid=document.getElementById('grid');
entries.forEach(e=>{{const card=document.createElement('article');card.className='card';card.dataset.id=e.id;
 if(recommended.has(e.id)){{const b=document.createElement('div');b.className='badge';b.textContent='★ 추천';card.appendChild(b)}}
 const p=document.createElement('div');p.className='preview';p.innerHTML=e.id==='free'?freePreview():`<img loading="lazy" src="/preview/${{encodeURIComponent(e.id)}}" alt="${{e.id}} 미리보기">`;
 const body=document.createElement('div');body.className='body';body.innerHTML=`<div class="title"><span class="chip" style="background:${{e.primary_color||'#e2e8f0'}}"></span>${{e.name}}</div><div class="desc">${{e.summary||''}}</div>`;
 card.append(p,body);card.onclick=()=>{{document.querySelectorAll('.card').forEach(x=>x.classList.remove('selected'));card.classList.add('selected');selected=e;document.getElementById('choice').textContent=e.name;document.getElementById('confirm').disabled=false}};grid.appendChild(card)}});
document.getElementById('confirm').onclick=async()=>{{if(!selected)return;const r=await fetch('/select',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{template:selected.id}})}});if(r.ok){{document.querySelector('.footer').innerHTML='<div class="choice">✓ '+selected.name+' 선택 완료 · 채팅으로 돌아가세요.</div>'}}}};
</script></body></html>"""


class GalleryState:
    def __init__(self, catalog: dict[str, dict], ref: str | None, lang: str, output: Path):
        self.catalog = catalog
        self.ref = ref
        self.lang = lang
        self.output = output
        self.previews = {deck_id: _preview_file(deck_id, ref) for deck_id in catalog}
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
            svg_path = self.state.previews.get(deck_id)
            if not SAFE_ID.fullmatch(deck_id) or not svg_path:
                self._send(404, "text/plain; charset=utf-8", b"preview not found")
                return
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
        if not _preview_file(deck_id, ref):
            continue
        out.append({
            "id": deck_id,
            "name": meta.get("display_name") or deck_id.replace("_", " ").title(),
            "summary": meta.get("summary", ""),
            "primary_color": meta.get("primary_color", "#e2e8f0"),
            "page_count": meta.get("page_count"),
        })
    out.append({"id": "free", "name": "Free Design", "summary": "등록 템플릿 없이 내용에 맞춰 자유롭게 설계", "primary_color": "#e2e8f0"})
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Open the Slide Master HTML template gallery")
    parser.add_argument("--source", choices=("auto", "github", "local"), default="auto")
    parser.add_argument("--recommend", default="", help="Comma-separated deck ids, max 3")
    parser.add_argument("--purpose", default="")
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
    page = _html_page(entries, set(recommend), source_label, args.purpose)

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
