#!/usr/bin/env python3
"""Lightweight composition/readability heuristics for generated Slide Master SVGs.

This gate complements svg_quality_checker.py. It focuses on failure patterns that
look technically valid but visually weak: cramped line spacing, excessive card
grids, tiny/decorative imagery, unused-center compositions, and repeated layouts.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

NUM_RE = re.compile(r"[-+]?\d+(?:\.\d+)?")
SECTION_RE = re.compile(r"^##\s+([A-Za-z_]+)\s*$")
RHYTHMS = {"anchor", "dense", "breathing"}


def _num(value, default=0.0):
    if value is None:
        return default
    m = NUM_RE.search(str(value))
    return float(m.group(0)) if m else default


def _tag(elem):
    return elem.tag.rsplit("}", 1)[-1]


def _text(elem):
    return "".join(elem.itertext()).strip()


def _estimate_text_width(text: str, fs: float) -> float:
    width = 0.0
    for ch in text:
        if ch.isspace():
            width += 0.25 * fs
        elif ord(ch) > 0x2FF:
            width += 1.0 * fs
        else:
            width += 0.55 * fs
    return width


def _parse_spec_lock(project: Path):
    path = project / "spec_lock.md"
    body = None
    rhythms: dict[str, str] = {}
    if not path.exists():
        return body, rhythms
    current = None
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip().lstrip("\ufeff")
        m = SECTION_RE.match(line)
        if m:
            current = m.group(1)
            continue
        kv = re.match(r"^-\s+([^:]+):\s*(.+)$", line)
        if not kv:
            continue
        key, value = kv.group(1).strip(), kv.group(2).strip()
        if current == "typography" and key == "body":
            body = _num(value, None)
        elif current == "page_rhythm" and key.startswith("P") and value in RHYTHMS:
            rhythms[key] = value
    return body, rhythms


def _bbox_for_element(elem, w: float, h: float):
    tag = _tag(elem)
    if tag in {"rect", "image", "foreignObject"}:
        x, y = _num(elem.get("x")), _num(elem.get("y"))
        ew, eh = _num(elem.get("width")), _num(elem.get("height"))
        if ew > 0 and eh > 0:
            return (x, y, x + ew, y + eh)
    if tag == "circle":
        cx, cy, r = _num(elem.get("cx")), _num(elem.get("cy")), _num(elem.get("r"))
        if r > 0:
            return (cx - r, cy - r, cx + r, cy + r)
    if tag == "text":
        fs = _num(elem.get("font-size"), 24.0)
        x, y = _num(elem.get("x")), _num(elem.get("y"))
        text = _text(elem)
        lines = max(1, 1 + sum(1 for t in elem if _tag(t) == "tspan" and _num(t.get("dy")) > 0))
        width = min(w, max(fs, _estimate_text_width(text, fs) / lines))
        height = min(h, max(fs * 1.2, fs * 1.4 * lines))
        return (x, max(0.0, y - fs), min(w, x + width), min(h, y - fs + height))
    return None


def _union(boxes):
    if not boxes:
        return None
    return (
        min(b[0] for b in boxes), min(b[1] for b in boxes),
        max(b[2] for b in boxes), max(b[3] for b in boxes),
    )


def _page_index(path: Path, fallback: int):
    m = re.match(r"(\d+)", path.stem)
    return int(m.group(1)) if m else fallback


def inspect_page(path: Path, rhythm: str | None, body_px: float | None):
    errors: list[str] = []
    warnings: list[str] = []
    try:
        root = ET.parse(path).getroot()
    except Exception as exc:
        return [f"{path.name}: cannot parse SVG ({exc})"], [], None
    vb = [_num(x) for x in str(root.get("viewBox") or "0 0 1280 720").split()]
    if len(vb) != 4:
        vb = [0.0, 0.0, 1280.0, 720.0]
    _, _, w, h = vb
    canvas_area = max(1.0, w * h)

    boxes = []
    cards = []
    image_areas = []
    text_boxes = []
    text_count = 0
    for elem in root.iter():
        tag = _tag(elem)
        box = _bbox_for_element(elem, w, h)
        if box:
            area = max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])
            if area < 0.85 * canvas_area and box[1] < 0.94 * h:
                boxes.append(box)
        if tag == "rect":
            rw, rh = _num(elem.get("width")), _num(elem.get("height"))
            area = rw * rh
            rx = max(_num(elem.get("rx")), _num(elem.get("ry")))
            if rx >= 6 and 0.025 * canvas_area <= area <= 0.45 * canvas_area and box:
                cards.append((elem, area, box))
        elif tag == "image":
            image_areas.append(_num(elem.get("width")) * _num(elem.get("height")))
        elif tag == "text":
            text_count += 1
            fs = _num(elem.get("font-size"), body_px or 24.0)
            if box:
                text_boxes.append((box, fs, _text(elem)))
            positive_dy = [_num(t.get("dy")) for t in elem if _tag(t) == "tspan" and _num(t.get("dy")) > 0]
            if positive_dy and fs >= (body_px or fs) * 0.72:
                ratio = min(positive_dy) / max(fs, 1.0)
                if ratio < 1.20:
                    errors.append(f"{path.name}: cramped multiline spacing {ratio:.2f}x on {fs:g}px text; target >=1.35x body rhythm")
                elif ratio < 1.30:
                    warnings.append(f"{path.name}: tight multiline spacing {ratio:.2f}x; prefer 1.35-1.50x for body copy")

    for tbox, fs, text in text_boxes:
        for _elem, _area, cbox in sorted(cards, key=lambda item: item[1]):
            if cbox[0] <= tbox[0] <= cbox[2] and cbox[1] <= tbox[1] <= cbox[3]:
                left_pad = tbox[0] - cbox[0]
                top_pad = tbox[1] - cbox[1]
                if fs >= (body_px or fs) * 0.72 and left_pad < 20:
                    warnings.append(f"{path.name}: text starts only {left_pad:.0f}px from a card edge; prefer ~28-36px horizontal padding")
                if fs >= (body_px or fs) * 0.72 and top_pad < 12:
                    warnings.append(f"{path.name}: text sits only {top_pad:.0f}px from a card top; increase vertical breathing room")
                break

    card_count = len(cards)
    if card_count >= 6:
        errors.append(f"{path.name}: {card_count} large rounded cards create a dense card wall; regroup/split the slide")
    elif card_count >= 5:
        warnings.append(f"{path.name}: {card_count} peer cards; prefer <=3 primary regions unless the comparison requires it")
    if rhythm == "breathing" and card_count >= 3:
        errors.append(f"{path.name}: breathing page uses {card_count} large cards; use a hero/naked-text/visual composition instead")

    if image_areas:
        max_img = max(image_areas) / canvas_area
        total_img = sum(image_areas) / canvas_area
        if max_img < 0.08 and total_img < 0.14:
            warnings.append(f"{path.name}: imagery is visually minor ({max_img:.0%} max canvas area); enlarge a meaningful visual or remove decoration")

    u = _union(boxes)
    if u and rhythm not in {"anchor", "breathing"}:
        bw, bh = u[2] - u[0], u[3] - u[1]
        if bw < 0.58 * w and bh < 0.58 * h:
            warnings.append(f"{path.name}: content footprint is small ({bw/w:.0%}w × {bh/h:.0%}h); avoid a dense center island with unused outer space")

    signature = (
        min(card_count, 5),
        min(len(image_areas), 3),
        min(text_count // 4, 5),
        rhythm or "unknown",
    )
    return errors, warnings, signature


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check Slide Master composition/readability heuristics")
    parser.add_argument("project")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = parser.parse_args(argv)
    project = Path(args.project)
    pages = sorted((project / "svg_output").glob("*.svg"))
    if not pages:
        print("[design-quality] FAIL: no svg_output pages", file=sys.stderr)
        return 1
    body_px, rhythms = _parse_spec_lock(project)
    errors: list[str] = []
    warnings: list[str] = []
    signatures = []

    for fallback, page in enumerate(pages, 1):
        idx = _page_index(page, fallback)
        rhythm = rhythms.get(f"P{idx:02d}")
        e, w, sig = inspect_page(page, rhythm, body_px)
        errors.extend(e)
        warnings.extend(w)
        signatures.append((page.name, sig))

    for i in range(2, len(signatures)):
        a, b, c = signatures[i - 2:i + 1]
        if a[1] and a[1] == b[1] == c[1] and a[1][3] == "dense":
            warnings.append(
                f"{a[0]}, {b[0]}, {c[0]}: three consecutive dense pages share the same layout signature; vary hierarchy/composition if content allows"
            )

    for msg in warnings:
        print(f"[design-quality] WARN: {msg}", file=sys.stderr)
    for msg in errors:
        print(f"[design-quality] ERROR: {msg}", file=sys.stderr)

    report = {
        "body_px": body_px,
        "pages": len(pages),
        "errors": len(errors),
        "warnings": len(warnings),
    }
    print("DESIGN_QUALITY=" + json.dumps(report, ensure_ascii=False))
    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
