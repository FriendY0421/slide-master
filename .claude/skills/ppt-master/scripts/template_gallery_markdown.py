#!/usr/bin/env python3
"""Generate or validate a stable GitHub-rendered visual template catalog."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import template_catalog as catalog_core
import template_gallery as legacy

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "template-gallery" / "README.md"


def _image_link(output_path: Path, repo_path: str) -> str:
    target = REPO_ROOT / Path(repo_path)
    return Path(os.path.relpath(target, output_path.parent)).as_posix()


def _template_block(entry: dict, output_path: Path, ref: str | None) -> list[str]:
    previews = catalog_core.preview_items(entry, ref, limit=6)
    lines = [
        f"## {entry['display_name']}",
        "",
        f"- 선택 ID: `{entry['key']}`",
        f"- 종류: `{entry['template_kind']}`",
        f"- 요약: {entry.get('summary') or '등록된 템플릿'}",
        "",
    ]
    if previews:
        representative, _ = previews[0]
        lines += [
            f"![{entry['display_name']} 대표 미리보기]({_image_link(output_path, representative)})",
            "",
            "<details>",
            f"<summary>{entry['display_name']} 상세 레이아웃 보기</summary>",
            "",
        ]
        for path, label in previews:
            lines += [
                f"**{label}**",
                "",
                f"![{entry['display_name']} - {label}]({_image_link(output_path, path)})",
                "",
            ]
        lines += ["</details>", ""]
    else:
        lines += [
            "> 등록된 SVG 미리보기가 없습니다. 선택 전에 템플릿 패키지를 점검하세요.",
            "",
        ]
    lines += ["---", ""]
    return lines


def build_markdown(source: str, output_path: Path) -> str:
    ref, source_label = legacy._resolve_source(source)
    catalog = catalog_core.load_catalog(ref)
    decks = sorted(
        (e for e in catalog.values() if e["template_kind"] == "deck"),
        key=lambda e: e["display_name"].lower(),
    )
    layouts = sorted(
        (e for e in catalog.values() if e["template_kind"] == "layout"),
        key=lambda e: e["display_name"].lower(),
    )
    lines = [
        "# Slide Master — Stable Visual Template Gallery",
        "",
        "> ChatGPT의 HTML/JavaScript 렌더링 여부와 무관하게 GitHub에서 확인하는 안정형 템플릿 선택 화면입니다.",
        "> 모든 미리보기는 저장소에 실제 등록된 SVG 원본을 직접 참조하며 임의 재디자인 이미지를 사용하지 않습니다.",
        "",
        "## 선택 방법",
        "",
        "1. 아래 실제 미리보기와 상세 레이아웃을 확인합니다.",
        "2. 원하는 템플릿의 `선택 ID`를 복사합니다.",
        "3. ChatGPT 대화창에 예: `deck:mckinsey 선택`이라고 보냅니다.",
        "4. 사용자의 명시적 선택 전에는 새 PPT 생성이 시작되지 않습니다.",
        "",
        f"- 카탈로그 소스: `{source_label}`",
        f"- 현재 등록 템플릿: **{len(catalog)}개** + Free Design",
        "",
        "# Deck Templates",
        "",
    ]
    for entry in decks:
        lines.extend(_template_block(entry, output_path, ref))
    lines += ["# Layout Templates", ""]
    for entry in layouts:
        lines.extend(_template_block(entry, output_path, ref))
    lines += [
        "# Free Design",
        "",
        "- 선택 ID: `free`",
        "- 설명: 등록 템플릿을 사용하지 않고 주제에 맞춰 새 디자인을 설계합니다.",
        "- 자동 선택되지 않습니다. 사용자가 명시적으로 `free`를 선택해야 합니다.",
        "",
        "---",
        "",
        "## 운영 규칙",
        "",
        "- 이 문서는 `decks_index.json`과 `layouts_index.json`에서 자동 생성합니다.",
        "- 템플릿을 추가·수정·삭제한 뒤 반드시 이 갤러리를 다시 생성하고 `--check`로 최신 상태를 검증합니다.",
        "- ChatGPT가 실제로 표시하지 못한 화면을 '열었다'거나 '표시했다'고 안내해서는 안 됩니다.",
        "- `deck:<id>`, `layout:<id>`, `free` 중 사용자가 최종 선택을 반환하기 전에는 PPT를 생성하지 않습니다.",
        "",
    ]
    return "\n".join(lines)


def check_gallery(source: str, output_path: Path) -> list[str]:
    if not output_path.is_file():
        return [f"stable gallery is missing: {output_path}"]
    ref, _ = legacy._resolve_source(source)
    catalog = catalog_core.load_catalog(ref)
    text = output_path.read_text(encoding="utf-8")
    errors: list[str] = []
    for entry in catalog.values():
        if f"`{entry['key']}`" not in text:
            errors.append(f"missing selection id: {entry['key']}")
        previews = catalog_core.preview_items(entry, ref, limit=6)
        if not previews:
            errors.append(f"missing registered preview: {entry['key']}")
            continue
        for preview_path, _ in previews:
            link = _image_link(output_path, preview_path)
            if link not in text:
                errors.append(f"missing registered preview link: {entry['key']} -> {link}")
    if "`free`" not in text:
        errors.append("missing Free Design selection id")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the stable Slide Master visual gallery")
    parser.add_argument("--source", choices=("auto", "github", "local"), default="local")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    output_path = args.output
    if not output_path.is_absolute():
        output_path = (REPO_ROOT / output_path).resolve()

    if args.check:
        errors = check_gallery(args.source, output_path)
        if errors:
            for error in errors:
                print(f"ERROR: {error}")
            return 2
        print(f"TEMPLATE_GALLERY_OK={output_path}")
        return 0

    payload = build_markdown(args.source, output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(payload, encoding="utf-8")
    print(f"TEMPLATE_GALLERY_WRITTEN={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
