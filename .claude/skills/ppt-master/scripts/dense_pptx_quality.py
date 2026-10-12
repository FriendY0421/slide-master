#!/usr/bin/env python3
"""PPT Master - Task-scoped dense native PPTX geometry check.

Measure final DrawingML text/cells against actual supplied font files. Report
mechanical failures separately from design preferences; never resize a font.

Usage: python3 scripts/dense_pptx_quality.py DECK --contract CONTRACT [--output REPORT]
Examples: see docs/ppt-project/DENSE_PPTX_QUALITY.md.
Dependencies: standard library and existing Pillow.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from console_encoding import configure_utf8_stdio

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main"}
EMU_PT = 12700.0
SCALE = 8


def _number(value: object, name: str, *, positive: bool = False) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be numeric")
    result = float(value)
    if not math.isfinite(result) or result < 0 or (positive and result == 0):
        raise ValueError(f"{name} must be finite and {'positive' if positive else 'nonnegative'}")
    return result


def _color(element: ET.Element | None, fallback: str | None = None) -> str | None:
    node = element.find("a:solidFill/a:srgbClr", NS) if element is not None else None
    return node.get("val") if node is not None else fallback


def _contrast(foreground: str, background: str) -> float:
    def luminance(color):
        channels = [int(color[i:i+2], 16) / 255 for i in (0, 2, 4)]
        linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
        return sum(c * w for c, w in zip(linear, (0.2126, 0.7152, 0.0722)))
    light, dark = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


class DenseInspector:
    def __init__(self, contract: dict, base: Path) -> None:
        self.contract, self.base = contract, base
        self.errors, self.warnings, self.measurements, self.fonts = [], [], [], {}
        self.font_files = {}
        self.tolerance = _number(contract.get("tolerance_pt", 0.2), "tolerance")

    def issue(self, kind: str, target: str, detail: str, *, preference: bool = False) -> None:
        (self.warnings if preference else self.errors).append(
            {"kind": kind, "target": target, "detail": detail,
             "category": "design_preference" if preference else "mechanical"})

    def font(self, family: str, bold: bool, size: float):
        from PIL import ImageFont

        face = "bold" if bold else "regular"
        identity = (family, face, size)
        if identity not in self.fonts:
            spec = self.contract["font_files"].get(family, {}).get(face)
            if not spec:
                raise ValueError(f"Actual {family} {face} font file is required; fallback is not verification")
            path = (self.base / spec["path"]).resolve(strict=True)
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if spec.get("sha256") and digest != spec["sha256"]:
                raise ValueError(f"{family} {face} font bytes differ from the task's verified font")
            font = ImageFont.truetype(str(path), max(1, round(size * SCALE)), index=int(spec.get("index", 0)))
            if font.getname()[0] != family:
                raise ValueError(f"Font file identifies as {font.getname()[0]}, not required {family}")
            self.font_files[str(path)] = digest
            self.fonts[identity] = font
        return self.fonts[identity]

    def box(self, shape: ET.Element) -> tuple[float, float, float, float]:
        xfrm = shape.find("p:xfrm", NS)
        if xfrm is None:
            xfrm = shape.find("p:spPr/a:xfrm", NS)
        if xfrm is None or xfrm.get("rot", "0") != "0":
            raise ValueError("Dense check requires explicit unrotated native geometry")
        off, extent = xfrm.find("a:off", NS), xfrm.find("a:ext", NS)
        return tuple(float(node.get(attr)) / EMU_PT for node, attr in
                     ((off, "x"), (off, "y"), (extent, "cx"), (extent, "cy")))

    def text(self, body: ET.Element, width: float, height: float, target: str,
             expected: dict, fill: str | None) -> None:
        if width <= 0 or height <= 0:
            self.issue("NO_CONTENT_AREA", target, "Padding leaves no usable text/cell area")
            return
        props = body.find("a:bodyPr", NS)
        if props is not None and props.find("a:normAutofit", NS) is not None:
            self.issue("AUTO_SHRINK", target, "Font auto-shrink cannot satisfy the fixed-size contract")
        wrap = props is None or props.get("wrap", "square") != "none"
        required_height, max_width, line_count = 0.0, 0.0, 0
        for paragraph in body.findall("a:p", NS):
            paragraph_props = paragraph.find("a:pPr", NS)
            align = paragraph_props.get("algn", "l") if paragraph_props is not None else "l"
            if align not in {"l", "ctr", "r"}:
                self.issue("ALIGNMENT", target, f"Unsupported paragraph alignment {align}")
            if expected.get("align") and align != expected["align"]:
                self.issue("ALIGNMENT", target, f"{align} differs from requested {expected['align']}")
            tokens, natural_height = [], 0.0
            for child in paragraph:
                local = child.tag.rsplit("}", 1)[-1]
                if local == "br":
                    tokens.append(("\n", 0.0))
                    continue
                if local not in {"r", "fld"}:
                    continue
                text = child.findtext("a:t", "", NS)
                if not text:
                    continue
                run = child.find("a:rPr", NS)
                if run is None or not run.get("sz"):
                    raise ValueError(f"{target}: explicit final run point size required; inherited text is unverified")
                size = _number(run.get("sz"), "run size", positive=True) / 100
                typeface = run.find("a:ea", NS)
                if typeface is None:
                    typeface = run.find("a:latin", NS)
                family = typeface.get("typeface") if typeface is not None else None
                if family != self.contract["font_family"]:
                    raise ValueError(
                        f"{target}: final font {family} differs from requested {self.contract['font_family']}"
                    )
                if "font_pt" in expected and abs(size - expected["font_pt"]) > 0.01:
                    self.issue("FONT_SIZE", target, f"{size:g}pt != required {expected['font_pt']:g}pt")
                if "max_font_pt" in expected and size > expected["max_font_pt"] + 0.01:
                    self.issue("FONT_SIZE", target, f"{size:g}pt exceeds {expected['max_font_pt']:g}pt")
                font = self.font(family, run.get("b") == "1", size)
                ascent, descent = font.getmetrics()
                natural_height = max(natural_height, (ascent + descent) / SCALE)
                color = _color(run)
                if expected.get("color") and color != expected["color"]:
                    self.issue("COLOR", target, f"{color} differs from required {expected['color']}")
                if color and fill:
                    ratio = _contrast(color, fill)
                    if ratio < self.contract.get("contrast_preference", 4.5):
                        self.issue("CONTRAST", target, f"Small-text contrast {ratio:.2f}; review requested colors",
                                   preference=True)
                else:
                    self.issue("COLOR_UNVERIFIED", target, "Inherited/theme color requires rendered review",
                               preference=True)
                # Use word boundaries for Latin and per-glyph opportunities for CJK.
                tracking = float(run.get("spc", "0")) / 100
                token_pattern = (r"\n|[\u1100-\u11ff\u2e80-\ua4cf\uac00-\ud7af]|"
                                 r"[^\s\u1100-\u11ff\u2e80-\ua4cf\uac00-\ud7af]+|[^\S\n]+")
                for token in re.findall(token_pattern, text):
                    tokens.append((token, font.getlength(token) / SCALE + len(token) * tracking))
            if not tokens:
                continue
            lines, current = 1, 0.0
            for token, measured in tokens:
                if token == "\n":
                    max_width = max(max_width, current); lines += 1; current = 0.0
                elif measured > width + self.tolerance:
                    self.issue("UNBREAKABLE_TEXT_WIDTH", target,
                               f"Token needs {measured:.2f}pt; available {width:.2f}pt")
                    current += measured
                elif wrap and current + measured > width + self.tolerance:
                    max_width = max(max_width, current); lines += 1; current = measured if token.strip() else 0.0
                else:
                    current += measured
            max_width = max(max_width, current)
            if not wrap and current > width + self.tolerance:
                self.issue("TEXT_WIDTH", target, f"Unwrapped line needs {current:.2f}pt; available {width:.2f}pt")
            spacing = paragraph.find("a:pPr/a:lnSpc/a:spcPts", NS)
            percent_spacing = paragraph.find("a:pPr/a:lnSpc/a:spcPct", NS)
            line_height = float(spacing.get("val")) / 100 if spacing is not None else natural_height
            if percent_spacing is not None:
                line_height = natural_height * float(percent_spacing.get("val")) / 100000
            if spacing is None and percent_spacing is None:
                self.issue("LINE_SPACING_UNVERIFIED", target,
                           "No explicit point line spacing; font-metric estimate used",
                           preference=True)
            if lines > 1 and line_height + self.tolerance < natural_height:
                self.issue("LINE_HEIGHT", target,
                           f"{line_height:.2f}pt line spacing < font line metrics {natural_height:.2f}pt")
            before = paragraph.find("a:pPr/a:spcBef/a:spcPts", NS)
            after = paragraph.find("a:pPr/a:spcAft/a:spcPts", NS)
            required_height += (natural_height + (lines - 1) * line_height
                                + sum(float(n.get("val")) / 100 for n in (before, after) if n is not None))
            line_count += lines
        self.measurements.append({"target": target, "available_pt": [width, height],
                                  "measured_width_pt": max_width, "required_height_pt": required_height,
                                  "wrapped_lines": line_count})
        if required_height > height + self.tolerance:
            self.issue("TEXT_HEIGHT", target,
                       f"{line_count} lines need {required_height:.2f}pt; available {height:.2f}pt")

    def table(self, shape: ET.Element, target: str, expected: dict) -> None:
        table = shape.find("a:graphic/a:graphicData/a:tbl", NS)
        if table is None:
            raise ValueError(f"{target}: required editable native table is missing")
        cols = [float(c.get("w")) / EMU_PT for c in table.findall("a:tblGrid/a:gridCol", NS)]
        rows = table.findall("a:tr", NS)
        heights = [float(r.get("h")) / EMU_PT for r in rows]
        _, _, width, height = self.box(shape)
        if abs(sum(cols) - width) > self.tolerance or abs(sum(heights) - height) > self.tolerance:
            self.issue("TABLE_EXTENT", target, "Grid widths/row heights disagree with actual frame")
        for field, actual in (("column_widths_pt", cols), ("row_heights_pt", heights)):
            wanted = expected.get(field)
            if wanted is not None and (len(wanted) != len(actual) or any(
                    abs(a - b) > self.tolerance for a, b in zip(actual, wanted))):
                self.issue("TABLE_GEOMETRY", target, f"{field} differs from requested {wanted}")
        covered = set()
        for r, row in enumerate(rows):
            cells = row.findall("a:tc", NS)
            if len(cells) != len(cols):
                raise ValueError(f"{target}: inconsistent native table grid")
            for col, cell in enumerate(cells):
                identity = (r, col)
                continuation = cell.get("hMerge") == "1" or cell.get("vMerge") == "1"
                body = cell.find("a:txBody", NS)
                if identity in covered:
                    if not continuation or "".join(body.itertext()).strip():
                        self.issue("MERGE_CONTINUATION", target,
                                   f"R{r+1}C{col+1}: covered cell must be blank and marked merged")
                    continue
                if continuation:
                    self.issue("ORPHAN_MERGE", target, f"R{r+1}C{col+1}: continuation has no preceding anchor")
                    continue
                rs, cs = int(cell.get("rowSpan", "1")), int(cell.get("gridSpan", "1"))
                if min(rs, cs) < 1 or r + rs > len(rows) or col + cs > len(cols):
                    raise ValueError(f"{target}: merged cell span exceeds grid")
                region = {(rr, cc) for rr in range(r, r+rs) for cc in range(col, col+cs)}
                if region & covered:
                    self.issue("MERGE_OVERLAP", target, f"R{r+1}C{col+1}: merge overlaps another anchor")
                covered.update(region - {identity})
                props = cell.find("a:tcPr", NS)
                if props is None or any(props.get(a) is None for a in ("marL", "marR", "marT", "marB")):
                    raise ValueError(f"{target}: explicit final cell padding is required")
                pads = [float(props.get(a)) / EMU_PT for a in ("marL", "marR", "marT", "marB")]
                if any(p < 0 for p in pads):
                    self.issue("CELL_PADDING", target, "Negative cell padding")
                if props.get("anchor", "t") not in {"t", "ctr", "b"}:
                    self.issue("VERTICAL_ALIGNMENT", target, "Unsupported cell anchor")
                borders = [line for side in ("lnL", "lnR", "lnT", "lnB")
                           for line in props.findall(f"a:{side}", NS)]
                for line in borders:
                    if line.find("a:noFill", NS) is None:
                        weight = float(line.get("w", "0")) / EMU_PT
                        low, high = self.contract.get("line_weight_preference_pt", [0.25, 0.75])
                        if not low <= weight <= high:
                            self.issue("LINE_WEIGHT", target, f"{weight:g}pt line outside requested thin-line range",
                                       preference=True)
                is_header = r < expected.get("header_rows", 1)
                cell_expected = {"max_font_pt": expected.get("max_font_pt", expected["header_max_pt"])}
                if is_header:
                    cell_expected["max_font_pt"] = expected["header_max_pt"]
                    if "header_pt" in expected:
                        cell_expected["font_pt"] = expected["header_pt"]
                else:
                    cell_expected["font_pt"] = expected["body_pt"]
                color_key = "header_color" if is_header else "body_color"
                if color_key in expected:
                    cell_expected["color"] = expected[color_key]
                if "padding_pt" in expected and any(
                        abs(a - b) > self.tolerance for a, b in zip(pads, expected["padding_pt"])):
                    self.issue("CELL_PADDING", target, "Padding differs from requested values")
                self.text(body, sum(cols[col:col+cs]) - pads[0] - pads[1],
                          sum(heights[r:r+rs]) - pads[2] - pads[3],
                          f"{target}:R{r+1}C{col+1}", cell_expected, _color(props))


def inspect_pptx(path: Path, contract: dict, base: Path) -> dict:
    if not contract.get("slides") or any(not page.get("objects") for page in contract["slides"]):
        raise ValueError("Dense contract requires nonempty slides and explicit target objects")
    inspector = DenseInspector(contract, base)
    with zipfile.ZipFile(path) as package:
        pres = ET.fromstring(package.read("ppt/presentation.xml"))
        size = pres.find("p:sldSz", NS)
        actual = [float(size.get(a)) / EMU_PT for a in ("cx", "cy")]
        if actual != contract["slide_size_pt"]:
            inspector.issue("SLIDE_SIZE", "deck", f"Actual {actual} differs from requested dimensions")
        for page in contract["slides"]:
            number = int(page["slide"])
            root = ET.fromstring(package.read(f"ppt/slides/slide{number}.xml"))
            shapes = root.findall("p:cSld/p:spTree/*", NS)
            found = {}
            for shape in shapes:
                identity = shape.find(".//p:cNvPr", NS)
                if identity is not None:
                    found.setdefault(identity.get("name"), []).append(shape)
            boxes = []
            for name, expected in page["objects"].items():
                target = f"P{number}:{name}"
                matches = found.get(name, [])
                shape = matches[0] if len(matches) == 1 else None
                if shape is None and expected.get("text_equals"):
                    matches = [s for s in shapes if "".join(t.text or "" for t in s.findall(".//a:t", NS))
                               == expected["text_equals"]]
                    shape = matches[0] if len(matches) == 1 else None
                if shape is None:
                    inspector.issue("MISSING_EDITABLE_OBJECT", target, "Required unique native object missing")
                    continue
                if "text_equals" in expected:
                    actual_text = "".join(t.text or "" for t in shape.findall(".//a:t", NS))
                    if actual_text != expected["text_equals"]:
                        inspector.issue("TEXT_CONTENT", target, "Final text differs from the required source")
                try:
                    box = inspector.box(shape)
                    x, y, w, h = box
                    rx, ry, rw, rh = page["region_pt"]
                    if (w <= 0 or h <= 0 or x < rx or y < ry
                            or x+w > rx+rw+inspector.tolerance or y+h > ry+rh+inspector.tolerance):
                        inspector.issue("REGION_BOUNDS", target,
                                        "Object violates requested page margin/left-half region")
                    boxes.append((target, box))
                    if expected["kind"] == "table":
                        inspector.table(shape, target, expected)
                    else:
                        body = shape.find("p:txBody", NS)
                        if body is None:
                            raise ValueError("Required editable native text/diagram label missing")
                        props = body.find("a:bodyPr", NS)
                        pads = [float(props.get(a, str(default))) / EMU_PT for a, default in
                                (("lIns", 91440), ("rIns", 91440), ("tIns", 45720), ("bIns", 45720))]
                        inspector.text(body, w-pads[0]-pads[1], h-pads[2]-pads[3], target, expected,
                                       _color(shape.find("p:spPr", NS), page.get("background", "FFFFFF")))
                except (OSError, ValueError, KeyError, TypeError) as exc:
                    inspector.issue("UNVERIFIED", target, str(exc))
            for i, (name, (x,y,w,h)) in enumerate(boxes):
                for other, (xx,yy,ww,hh) in boxes[i+1:]:
                    if (min(x+w,xx+ww)-max(x,xx) > inspector.tolerance
                            and min(y+h,yy+hh)-max(y,yy) > inspector.tolerance):
                        inspector.issue("OBJECT_OVERLAP", name, f"Overlaps required region {other}")
            for label in page.get("required_diagram_labels", []):
                native_labels = [s for s in root.findall(".//p:sp", NS)
                                 if "".join(t.text or "" for t in s.findall("p:txBody//a:t", NS)) == label]
                if len(native_labels) != 1:
                    inspector.issue("DIAGRAM_EDITABILITY", f"P{number}:{label}",
                                    "Required unique native diagram label missing")
            arrow_count = sum(end.get("type", "none") != "none" for end in
                              root.findall(".//a:headEnd", NS) + root.findall(".//a:tailEnd", NS))
            if arrow_count < page.get("minimum_arrow_ends", 0):
                inspector.issue("DIAGRAM_CONNECTORS", f"P{number}", "Required editable arrow connectors are missing")
    return {"schema_version": 1, "deck_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "contract_sha256": hashlib.sha256(json.dumps(contract, sort_keys=True).encode()).hexdigest(),
            "errors": inspector.errors, "design_warnings": inspector.warnings,
            "measurements": inspector.measurements, "font_files_sha256": inspector.font_files,
            "rendered_review_completed": False, "powerpoint_review_completed": False,
            "font_metric_check": "actual supplied font files; rendered review still required"}


def main(argv: list[str] | None = None) -> int:
    configure_utf8_stdio()
    parser = argparse.ArgumentParser(
        description="Measure task-scoped dense native PPTX cells/text without font shrinking")
    parser.add_argument("deck", type=Path)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        report = inspect_pptx(args.deck, json.loads(args.contract.read_text(encoding="utf-8")), args.contract.parent)
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError, zipfile.BadZipFile) as exc:
        print(f"[dense-quality] FAIL: {exc}", file=sys.stderr)
        return 2
    if args.output:
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"errors": len(report["errors"]), "design_warnings": len(report["design_warnings"]),
                      "measured_regions": len(report["measurements"])}, ensure_ascii=False))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
