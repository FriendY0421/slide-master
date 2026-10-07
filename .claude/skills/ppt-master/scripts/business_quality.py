#!/usr/bin/env python3
"""
PPT Master - Opt-in Business Quality Evidence

Check a purpose-specific profile against authored SVG and exported PPTX. Bind
explicit agent visual review to the exact sources, profile, fonts, PPTX and PNGs.
This complements existing geometry/visual checks; it does not infer visual approval.
See docs/ppt-project/KOREAN_BUSINESS_QUALITY.md.

Usage:
    python3 scripts/business_quality.py SOURCE --profile PROFILE --pptx DECK
        [--render-manifest MANIFEST --record-review RECEIPT --reviewer NAME]
        [--review-record RECEIPT]

Dependencies:
    None beyond existing local text_fit helper (standard library).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import posixpath
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from console_encoding import configure_utf8_stdio
from text_fit import evaluate_stack, text_width

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "c": "http://schemas.openxmlformats.org/drawingml/2006/chart"}
SOURCE_SUFFIXES = {".svg", ".css", ".json", ".md"}


def sha256(path: Path) -> str:
    """Hash the file bytes, not its timestamp."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def source_state(source: Path, profile_path: Path, profile: dict) -> dict:
    """Include all source pages and shared design inputs, including bundled fonts."""
    inputs = {str(p.relative_to(source)): sha256(p) for p in sorted(source.rglob("*"))
              if p.is_file() and p.suffix in SOURCE_SUFFIXES}
    if not inputs:
        raise ValueError("No source inputs; supply the authored SVG source directory")
    fonts = {}
    shared = {}
    for raw in profile.get("shared_inputs", []):
        shared[raw] = sha256((profile_path.parent / raw).resolve())
    for name in ("spec_lock.md", "design_spec.md"):
        parent_input = source.parent / name
        if parent_input.is_file():
            shared[f"project/{name}"] = sha256(parent_input)
    for raw in profile["font_files"]:
        font = (profile_path.parent / raw).resolve()
        fonts[str(font)] = sha256(font)
    if not fonts:
        raise ValueError("Profile must declare the actual font files used for review")
    return {"inputs": inputs, "shared": shared,
            "profile_sha256": sha256(profile_path), "fonts": fonts}


def check_sources(source: Path, profile: dict) -> tuple[list[str], list[str]]:
    """Check this explicit role/zone contract with the existing conservative fit model."""
    pages = sorted(source.glob("*.svg"))
    errors, titles = [], []
    if len(pages) != profile["slide_count"]:
        errors.append(f"Expected {profile['slide_count']} SVG pages, found {len(pages)}")
    for page in pages:
        root = ET.parse(page).getroot()
        page_type = root.get("data-business-page-type")
        contract = profile["page_types"].get(page_type)
        if contract is None:
            errors.append(f"{page.name}: missing/unknown business page type")
            continue
        if any(e.get("transform") for e in root.iter()):
            errors.append(f"{page.name}: this opt-in profile requires explicit slide coordinates")
        vb = [float(v) for v in root.get("viewBox", "").split()]
        if vb != profile["view_box"]:
            errors.append(f"{page.name}: canvas differs from the declared profile")
        page_titles, body_count = [], 0
        texts = [e for e in root.iter() if e.tag.rsplit("}", 1)[-1] == "text"]
        for elem in texts:
            text = "".join(elem.itertext()).strip()
            role = elem.get("data-business-role")
            rule = profile["roles"].get(role)
            if rule is None:
                errors.append(f"{page.name}: text lacks a declared role: {text[:24]}")
                continue
            fs = float(elem.get("font-size", "0"))
            width = float(elem.get("data-business-width", "0"))
            x, y = float(elem.get("x", "0")), float(elem.get("y", "0"))
            if not all(math.isfinite(value) for value in (fs, width, x, y)) or fs <= 0:
                errors.append(f"{page.name}: {role} has invalid/non-finite text geometry")
                continue
            if fs < rule["min_px"]:
                errors.append(f"{page.name}: {role} is {fs:g}px, minimum {rule['min_px']}px")
            if profile["font_family"] != elem.get("font-family", "").split(",")[0].strip(" '\""):
                errors.append(f"{page.name}: {role} font differs from profile")
            if len(text) > rule["max_chars"]:
                errors.append(f"{page.name}: {role} exceeds {rule['max_chars']} characters; reflow/split")
            if "{{" in text or "}}" in text:
                errors.append(f"{page.name}: unresolved content token")
            if width <= 0 or text_width(text, fs) > width:
                errors.append(f"{page.name}: {role} exceeds/misses its declared text zone: {text[:24]}")
            fit = evaluate_stack(fs, x=x, y=y, lines=[text],
                                 anchor=elem.get("text-anchor", "start"),
                                 vb_width=profile["view_box"][2], vb_height=profile["view_box"][3])
            if fit["findings"]:
                errors.append(f"{page.name}: {role} crosses the canvas")
            if role == "title":
                page_titles.append(text)
            body_count += role == "body"
        if len(page_titles) != 1:
            errors.append(f"{page.name}: expected exactly one explicit title")
        titles.append(page_titles[0] if page_titles else "")
        if body_count > contract["max_body_lines"]:
            errors.append(f"{page.name}: exceeds {contract['max_body_lines']} body lines")
        disclosure = profile.get("required_disclosure")
        if disclosure and not any(disclosure in "".join(e.itertext()) for e in texts):
            errors.append(f"{page.name}: required disclosure missing")
    return errors, titles


def check_package(pptx: Path, profile: dict, titles: list[str], source: Path) -> tuple[list[str], dict]:
    """Require real chart/table owners and preserved text, not shape-count proxies."""
    errors, coverage = [], {"charts": [], "tables": [], "workbooks": 0}
    source_pages = sorted(source.glob("*.svg"))
    with zipfile.ZipFile(pptx) as package:
        names = package.namelist()
        slide_names = sorted((n for n in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
                             key=lambda n: int(re.search(r"slide(\d+)", n).group(1)))
        if len(slide_names) != profile["slide_count"]:
            errors.append("PPTX slide count differs from profile")
        coverage["workbooks"] = sum(n.startswith("ppt/embeddings/") and n.endswith(".xlsx")
                                    for n in names)
        for number, name in enumerate(slide_names, 1):
            root = ET.fromstring(package.read(name))
            text = "".join(root.itertext())
            if number <= len(titles) and titles[number - 1] not in text:
                errors.append(f"Slide {number}: authored title missing from PPTX")
            if profile.get("required_disclosure") and profile["required_disclosure"] not in text:
                errors.append(f"Slide {number}: disclosure missing from PPTX")
            if root.find(".//c:chart", NS) is not None:
                coverage["charts"].append(number)
            if root.find(".//a:tbl", NS) is not None:
                coverage["tables"].append(number)
            if number <= len(source_pages):
                source_root = ET.parse(source_pages[number - 1]).getroot()
                metadata = [e for e in source_root.iter()
                            if e.tag.rsplit("}", 1)[-1] == "metadata"
                            and e.get("data-pptx-native") in {"chart", "table"}]
                for marker in metadata:
                    payload = json.loads(marker.text)
                    if marker.get("data-pptx-native") == "table":
                        tables = root.findall(".//a:tbl", NS)
                        expected = ([payload["columns"]] if payload.get("columns") else []) + payload["rows"]
                        expected = [[str(cell.get("text", "")) if isinstance(cell, dict)
                                     else str(cell) for cell in row] for row in expected]
                        actual = [[["".join(cell.itertext()).strip() for cell in row.findall("a:tc/a:txBody", NS)]
                                   for row in table.findall("a:tr", NS)] for table in tables]
                        if expected not in actual:
                            errors.append(f"Slide {number}: native table cells differ from source metadata")
                    else:
                        rel_path = f"ppt/slides/_rels/slide{number}.xml.rels"
                        rels = {e.get("Id"): e.get("Target")
                                for e in ET.fromstring(package.read(rel_path))}
                        charts = root.findall(".//c:chart", NS)
                        expected = [[float(v) for v in series["values"]] for series in payload["series"]]
                        expected_categories = [str(v) for v in payload["categories"]]
                        matched = False
                        for chart in charts:
                            rid = chart.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
                            target = rels[rid]
                            chart_path = target.lstrip("/") if target.startswith("/") else posixpath.normpath(
                                posixpath.join("ppt/slides", target))
                            chart_root = ET.fromstring(package.read(chart_path))
                            actual_series, actual_categories = [], []
                            for series in chart_root.findall(".//c:ser", NS):
                                actual_series.append([float(v.text) for v in series.findall(
                                    "c:val/c:numRef/c:numCache/c:pt/c:v", NS)])
                                actual_categories.append([v.text for v in series.findall(
                                    "c:cat/c:strRef/c:strCache/c:pt/c:v", NS)])
                            matched |= actual_series == expected and all(
                                values == expected_categories for values in actual_categories)
                        if not matched:
                            errors.append(f"Slide {number}: native chart cache differs from source metadata")
            fonts = [e.get("typeface") for e in root.iter()
                     if e.tag in {f"{{{NS['a']}}}latin", f"{{{NS['a']}}}ea"}]
            if any(f != profile["font_family"] for f in fonts):
                errors.append(f"Slide {number}: exported text font differs from profile")
        for kind in ("charts", "tables"):
            missing = set(profile["required_native"][kind]) - set(coverage[kind])
            if missing:
                errors.append(f"Missing native {kind} on slides {sorted(missing)}")
        if coverage["charts"] and coverage["workbooks"] < len(coverage["charts"]):
            errors.append("Native chart coverage lacks embedded workbooks")
    return errors, coverage


def render_state(manifest_path: Path, pptx: Path, profile: dict, state: dict) -> dict:
    """Reject stale, partial or differently fonted renders before recording review."""
    manifest = read_json(manifest_path)
    if manifest["pptx_sha256"] != sha256(pptx):
        raise ValueError("Render manifest belongs to a different PPTX; render again")
    if manifest.get("registered_fonts") != state["fonts"]:
        raise ValueError("Renderer did not register the exact profile font assets")
    images = manifest["images"]
    if [e["slide"] for e in images] != list(range(1, profile["slide_count"] + 1)):
        raise ValueError("Expected exactly one ordered image per slide")
    if len({e["path"] for e in images}) != len(images):
        raise ValueError("Duplicate slide image paths")
    for entry in images:
        image = (manifest_path.parent / entry["path"]).resolve()
        if sha256(image) != entry["sha256"] or image.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"Slide {entry['slide']}: stale/invalid PNG; render again")
    return {"manifest_sha256": sha256(manifest_path), "images": images,
            "renderer": manifest["renderer"]}


def main(argv=None) -> int:
    configure_utf8_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--pptx", type=Path, required=True)
    parser.add_argument("--render-manifest", type=Path)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--record-review", type=Path)
    group.add_argument("--review-record", type=Path)
    parser.add_argument("--reviewer", help="Who actually inspected every rendered slide")
    args = parser.parse_args(argv)
    try:
        source, profile_path, pptx = args.source.resolve(), args.profile.resolve(), args.pptx.resolve()
        profile = read_json(profile_path)
        if profile.get("schema_version") != 1:
            raise ValueError("Unsupported business profile schema; use schema_version 1")
        state = source_state(source, profile_path, profile)
        errors, titles = check_sources(source, profile)
        package_errors, coverage = check_package(pptx, profile, titles, source)
        errors.extend(package_errors)
        evidence = {"schema_version": 1, "source": state, "pptx_sha256": sha256(pptx)}
        if args.record_review or args.review_record:
            if not args.render_manifest:
                raise ValueError("Visual review requires --render-manifest; render all slides first")
            evidence["render"] = render_state(args.render_manifest.resolve(), pptx, profile, state)
        if args.record_review:
            if not args.reviewer or not args.reviewer.strip():
                raise ValueError("Use --reviewer only after inspecting all rendered slides")
            if args.record_review.exists():
                raise ValueError("Review receipt already exists; use a new revision filename")
            if not errors:
                args.record_review.parent.mkdir(parents=True, exist_ok=True)
                args.record_review.write_text(json.dumps({"reviewer": args.reviewer,
                    "status": "explicit_visual_review", "evidence": evidence},
                    ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if args.review_record:
            recorded = read_json(args.review_record)
            if recorded.get("status") != "explicit_visual_review" or not recorded.get("reviewer"):
                errors.append("Review record lacks explicit review identity/status")
            if recorded.get("evidence") != evidence:
                errors.append("Visual review is stale: source/profile/font/PPTX/render changed; "
                              "review all slides again")
        print(json.dumps({"ok": not errors, "coverage": coverage, "errors": errors,
                          "visual_review": bool(args.review_record or (args.record_review and not errors)),
                          "geometry_basis": "existing conservative character-width model"},
                         ensure_ascii=False, indent=2))
        return 1 if errors else 0
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError, zipfile.BadZipFile) as exc:
        print(f"[business-quality] FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
