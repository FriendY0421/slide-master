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
import io
import json
import math
import posixpath
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from console_encoding import configure_utf8_stdio

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
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
        self.structure_only = contract.get("text_metrics", "actual_font") == "structure_only"
        if contract.get("text_metrics", "actual_font") not in {"actual_font", "structure_only"}:
            raise ValueError("text_metrics must be actual_font or structure_only")

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
        if off is None or extent is None:
            raise ValueError("Explicit object offset and extent required")
        box = tuple(float(node.get(attr)) / EMU_PT for node, attr in
                    ((off, "x"), (off, "y"), (extent, "cx"), (extent, "cy")))
        if any(not math.isfinite(value) for value in box):
            raise ValueError("Object geometry must be finite")
        return box

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
            self.paragraph_style(paragraph, target, expected)
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
                font = None
                if not self.structure_only:
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
                if self.structure_only:
                    continue
                # Use word boundaries for Latin and per-glyph opportunities for CJK.
                tracking = float(run.get("spc", "0")) / 100
                token_pattern = (r"\n|[\u1100-\u11ff\u2e80-\ua4cf\uac00-\ud7af]|"
                                 r"[^\s\u1100-\u11ff\u2e80-\ua4cf\uac00-\ud7af]+|[^\S\n]+")
                for token in re.findall(token_pattern, text):
                    tokens.append((token, font.getlength(token) / SCALE + len(token) * tracking))
            if not tokens:
                continue
            lines, current, paragraph_width = 1, 0.0, 0.0
            for token, measured in tokens:
                if token == "\n":
                    paragraph_width = max(paragraph_width, current); lines += 1; current = 0.0
                elif measured > width + self.tolerance:
                    self.issue("UNBREAKABLE_TEXT_WIDTH", target,
                               f"Token needs {measured:.2f}pt; available {width:.2f}pt")
                    current += measured
                elif wrap and current + measured > width + self.tolerance:
                    paragraph_width = max(paragraph_width, current); lines += 1; current = measured if token.strip() else 0.0
                else:
                    current += measured
            paragraph_width = max(paragraph_width, current)
            max_width = max(max_width, paragraph_width)
            if not wrap and paragraph_width > width + self.tolerance:
                self.issue("TEXT_WIDTH", target, f"Unwrapped line needs {paragraph_width:.2f}pt; available {width:.2f}pt")
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
        if self.structure_only:
            self.measurements.append({"target": target, "available_pt": [width, height],
                                      "kind": "text_structure", "text_metrics_verified": False})
            return
        self.measurements.append({"target": target, "available_pt": [width, height],
                                  "measured_width_pt": max_width, "required_height_pt": required_height,
                                  "wrapped_lines": line_count})
        if required_height > height + self.tolerance:
            self.issue("TEXT_HEIGHT", target,
                       f"{line_count} lines need {required_height:.2f}pt; available {height:.2f}pt")

    def paragraph_style(self, paragraph: ET.Element, target: str, expected: dict) -> None:
        fields = {"line_spacing_pt": "lnSpc/spcPts", "line_spacing_multiple": "lnSpc/spcPct",
                  "paragraph_before_pt": "spcBef/spcPts", "paragraph_after_pt": "spcAft/spcPts"}
        if "line_spacing_pt" in expected and "line_spacing_multiple" in expected:
            raise ValueError("Specify exact or multiple line spacing, not both")
        for field, path in fields.items():
            if field not in expected:
                continue
            wanted = _number(expected[field], field, positive=field.startswith("line_"))
            node = paragraph.find("a:pPr/" + "/".join("a:"+part for part in path.split("/")), NS)
            scale = 100000 if field == "line_spacing_multiple" else 100
            actual = float(node.get("val"))/scale if node is not None else None
            if actual is None or not math.isfinite(actual) or abs(actual-wanted) > 0.01:
                self.issue("PARAGRAPH_SPACING", target, f"{field}: {actual} differs from required {wanted}")

    def image(self, shape: ET.Element, target: str, expected: dict, package, slide_part: str) -> None:
        from PIL import Image

        if shape.tag != f"{{{NS['p']}}}pic":
            raise ValueError("Required editable picture object missing")
        blip = shape.find("p:blipFill/a:blip", NS)
        if blip is None or blip.get(f"{{{NS['r']}}}link"):
            raise ValueError("Picture must embed its source, not depend on an external link")
        rid = blip.get(f"{{{NS['r']}}}embed")
        rel_part = posixpath.join(posixpath.dirname(slide_part), "_rels", posixpath.basename(slide_part)+".rels")
        rels = ET.fromstring(package.read(rel_part))
        rel = next((node for node in rels if node.get("Id") == rid), None)
        if rel is None or rel.get("TargetMode") == "External":
            raise ValueError("Embedded image relationship missing or external")
        media_target = rel.get("Target", "")
        media_part = posixpath.normpath(media_target.lstrip("/") if media_target.startswith("/")
                                       else posixpath.join(posixpath.dirname(slide_part), media_target))
        if not media_part.startswith("ppt/media/"):
            raise ValueError("Picture relationship must target package media")
        with Image.open(io.BytesIO(package.read(media_part))) as image:
            pixels = image.size
        crop_node = shape.find("p:blipFill/a:srcRect", NS)
        crop = [float(crop_node.get(side, "0"))/100000 if crop_node is not None else 0
                for side in ("l", "t", "r", "b")]
        if any(not math.isfinite(value) or value < 0 or value >= 1 for value in crop):
            raise ValueError("Negative/outside image crops require separate rendered review")
        left, top, right, bottom = crop
        if left+right >= 1 or top+bottom >= 1:
            raise ValueError("Image crop leaves no visible pixels")
        _, _, width, height = self.box(shape)
        if width <= 0 or height <= 0:
            raise ValueError("Image frame must have positive width and height")
        visible = [pixels[0]*(1-left-right), pixels[1]*(1-top-bottom)]
        ratio_error = abs((width/height)/(visible[0]/visible[1])-1)
        if ratio_error > _number(expected.get("aspect_tolerance", 0.02), "aspect tolerance"):
            self.issue("IMAGE_DISTORTION", target, "Picture frame stretches the visible source aspect ratio")
        if expected.get("allow_crop") is False and any(crop):
            self.issue("IMAGE_CROP", target, "Cropping is forbidden for this source")
        if "protected_source_rect" in expected:
            px, py, pw, ph = [_number(value, "protected source rectangle")
                              for value in expected["protected_source_rect"]]
            if pw <= 0 or ph <= 0 or px+pw > 1 or py+ph > 1:
                raise ValueError("protected_source_rect uses normalized source coordinates within [0,1]")
            if px < left or py < top or px+pw > 1-right or py+ph > 1-bottom:
                self.issue("IMAGE_PROTECTED_CROP", target, "Cropping removes part of the declared important source region")
        dpi = [visible[0]*72/width, visible[1]*72/height]
        if "min_dpi" in expected and min(dpi) < _number(expected["min_dpi"], "minimum image DPI", positive=True):
            self.issue("IMAGE_RESOLUTION", target, f"Effective {min(dpi):.1f} DPI below the requested minimum")
        self.measurements.append({"target": target, "kind": "image", "source_pixels": pixels,
                                  "crop_ltrb": crop, "effective_dpi": dpi,
                                  "aspect_ratio_error": ratio_error})

    def layout(self, boxes: dict, page: dict, target: str) -> None:
        anchors = {"left": lambda b:b[0], "right": lambda b:b[0]+b[2],
                   "top": lambda b:b[1], "bottom": lambda b:b[1]+b[3],
                   "center_x": lambda b:b[0]+b[2]/2, "center_y": lambda b:b[1]+b[3]/2}
        for rule in page.get("alignment", []):
            names, axis = rule["objects"], rule["axis"]
            if len(names) < 2 or axis not in anchors:
                raise ValueError("Alignment needs at least two objects and a supported anchor")
            values = [anchors[axis](boxes[name]) for name in names]
            tolerance = _number(rule.get("tolerance_pt", self.tolerance), "alignment tolerance")
            if max(values)-min(values) > tolerance:
                self.issue("LAYOUT_ALIGNMENT", target, f"{names} do not share requested {axis} alignment")
        for rule in page.get("spacing", []):
            first, second = rule["objects"]
            axis = rule["axis"]
            if axis not in {"x", "y"}:
                raise ValueError("Spacing axis must be x or y; objects are ordered left/right or top/bottom")
            index = 0 if axis == "x" else 1
            a, b = boxes[first], boxes[second]
            gap = b[index]-(a[index]+a[index+2])
            low = _number(rule["min_gap_pt"], "minimum gap")
            high = _number(rule["max_gap_pt"], "maximum gap") if "max_gap_pt" in rule else math.inf
            if high < low:
                raise ValueError("Maximum gap must not be below minimum gap")
            if gap < low-self.tolerance or gap > high+self.tolerance:
                self.issue("LAYOUT_SPACING", target, f"{first} to {second}: {gap:.2f}pt outside [{low},{high}]")

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
                table_max = _number(expected.get("max_font_pt", expected["header_max_pt"]),
                                    "table maximum font size", positive=True)
                cell_expected = {"max_font_pt": table_max}
                if is_header:
                    cell_expected["max_font_pt"] = min(table_max, _number(
                        expected["header_max_pt"], "header maximum font size", positive=True))
                    if "header_pt" in expected:
                        cell_expected["font_pt"] = expected["header_pt"]
                else:
                    cell_expected["font_pt"] = expected["body_pt"]
                color_key = "header_color" if is_header else "body_color"
                if color_key in expected:
                    cell_expected["color"] = expected[color_key]
                prefix = "header_" if is_header else "body_"
                for field in ("line_spacing_pt", "line_spacing_multiple", "paragraph_before_pt", "paragraph_after_pt", "align"):
                    if prefix+field in expected:
                        cell_expected[field] = expected[prefix+field]
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
                    if "box_pt" in expected and (len(expected["box_pt"]) != 4 or any(
                            abs(a-b) > inspector.tolerance for a,b in zip(box, expected["box_pt"]))):
                        inspector.issue("OBJECT_GEOMETRY", target, "Object differs from the requested position/size")
                    if expected["kind"] == "table":
                        inspector.table(shape, target, expected)
                    elif expected["kind"] == "image":
                        inspector.image(shape, target, expected, package, f"ppt/slides/slide{number}.xml")
                    elif expected["kind"] == "shape":
                        if shape.tag != f"{{{NS['p']}}}sp":
                            raise ValueError("Required native box/shape missing")
                    elif expected["kind"] == "text":
                        body = shape.find("p:txBody", NS)
                        if body is None:
                            raise ValueError("Required editable native text/diagram label missing")
                        props = body.find("a:bodyPr", NS)
                        pads = [float(props.get(a, str(default))) / EMU_PT for a, default in
                                (("lIns", 91440), ("rIns", 91440), ("tIns", 45720), ("bIns", 45720))]
                        inspector.text(body, w-pads[0]-pads[1], h-pads[2]-pads[3], target, expected,
                                       _color(shape.find("p:spPr", NS), page.get("background", "FFFFFF")))
                    else:
                        raise ValueError("Object kind must be text, table, image or shape")
                except (OSError, ValueError, KeyError, TypeError) as exc:
                    inspector.issue("UNVERIFIED", target, str(exc))
            try:
                inspector.layout({name.split(":",1)[1]:box for name,box in boxes}, page, f"P{number}")
            except (ValueError, KeyError, TypeError) as exc:
                inspector.issue("UNVERIFIED_LAYOUT", f"P{number}", str(exc))
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
            "text_metrics_mode": "structure_only" if inspector.structure_only else "actual_font",
            "rendered_review_completed": False, "powerpoint_review_completed": False,
            "font_metric_check": ("not performed; structure-only metadata checks, wrapping/clipping unverified"
                                  if inspector.structure_only else "actual supplied font files; rendered review still required")}


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
