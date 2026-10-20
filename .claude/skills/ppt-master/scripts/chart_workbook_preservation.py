#!/usr/bin/env python3
"""PPT Master - Read-only chart/workbook preservation gate.

Compare exact pre-edit and post-edit packages. A failed candidate is never made
safe by declaring a rebuild source; regeneration must create a separate file.

Usage:
    python3 chart_workbook_preservation.py SOURCE CANDIDATE --source-sha256 SHA
        --candidate-sha256 SHA [--mode edit|regenerate] [--authoring-manifest JSON]
Examples:
    See docs/ppt-project/CLOUD_REVIEW_FONT_ORDER_20261020.md.
Dependencies:
    Standard library; no renderer, network, installer or package mutation.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import posixpath
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

from console_encoding import configure_utf8_stdio

NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"
MAX_BYTES = 100 * 1024 * 1024


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def checked_bytes(path: Path, expected: str) -> bytes:
    """Require exact, bounded existing bytes without changing the file."""
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError("Missing or oversized source/candidate")
    data = path.read_bytes()
    if digest(data) != expected:
        raise ValueError("Source/candidate SHA256 differs from the bound file")
    return data


def check_zip(package: ZipFile) -> None:
    names = package.namelist()
    if len(names) > 20000 or len(names) != len(set(names)) or sum(
        info.file_size for info in package.infolist()
    ) > MAX_BYTES:
        raise ValueError("Duplicate or excessive package content")


def relationships(package: ZipFile, owner: str) -> dict:
    parent, base = posixpath.split(owner)
    part = posixpath.join(parent, "_rels", base + ".rels")
    if part not in package.namelist():
        return {}
    found = {}
    for rel in ET.fromstring(package.read(part)).findall(REL + "Relationship"):
        key = rel.get("Id")
        if not key or key in found:
            raise ValueError("Duplicate/missing relationship ID")
        target = rel.get("Target", "")
        resolved = posixpath.normpath(target.lstrip("/") if target.startswith("/")
                                     else posixpath.join(parent, target))
        if resolved.startswith("../"):
            raise ValueError("Relationship escapes package root")
        found[key] = {"part": resolved, "type": rel.get("Type", ""),
                      "external": rel.get("TargetMode", "Internal") != "Internal"}
    return found


def related_part(package: ZipFile, rels: dict, rid: str, suffix: str) -> str:
    rel = rels.get(rid)
    if not rel or rel["external"] or not rel["type"].endswith(suffix):
        raise ValueError("Required internal chart/workbook relationship missing or external")
    if rel["part"] not in package.namelist():
        raise ValueError("Chart/workbook relationship target is absent")
    return rel["part"]


def workbook_metadata(data: bytes) -> dict:
    with ZipFile(io.BytesIO(data)) as book:
        check_zip(book)
        if "xl/workbook.xml" not in book.namelist():
            raise ValueError("Referenced package is not an XLSX workbook")
        formulas = []
        for name in sorted(book.namelist()):
            if name.startswith("xl/worksheets/") and name.endswith(".xml"):
                root = ET.fromstring(book.read(name))
                for cell in root.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c"):
                    formula = cell.find("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}f")
                    if formula is not None:
                        formulas.append([name, cell.get("r"), formula.attrib, formula.text])
        return {"sha256": digest(data), "formula_count": len(formulas),
                "formula_sha256": digest(json.dumps(formulas, sort_keys=True).encode()),
                "external_links": sum(n.startswith("xl/externalLinks/") and n.endswith(".xml")
                                      for n in book.namelist())}


def chart_inventory(data: bytes) -> dict:
    """Resolve logical slide -> native chart -> externalData -> embedded XLSX."""
    result = {}
    with ZipFile(io.BytesIO(data)) as package:
        check_zip(package)
        pres = ET.fromstring(package.read("ppt/presentation.xml"))
        rels = relationships(package, "ppt/presentation.xml")
        seen = set()
        slides = pres.findall("p:sldIdLst/p:sldId", NS)
        if not slides:
            raise ValueError("Missing logical slide inventory")
        for number, slide in enumerate(slides, 1):
            part = related_part(package, rels, slide.get("{" + NS["r"] + "}id"), "/slide")
            if part in seen:
                raise ValueError("Duplicate logical slide part")
            seen.add(part)
            root = ET.fromstring(package.read(part))
            slide_rels = relationships(package, part)
            for index, node in enumerate(root.findall(".//c:chart", NS), 1):
                chart_part = related_part(package, slide_rels, node.get("{" + NS["r"] + "}id"), "/chart")
                chart = ET.fromstring(package.read(chart_part))
                books = []
                chart_rels = relationships(package, chart_part)
                for external in chart.findall("c:externalData", NS):
                    book = related_part(package, chart_rels, external.get("{" + NS["r"] + "}id"), "/package")
                    books.append(workbook_metadata(package.read(book)))
                kind = [n.tag.rsplit("}", 1)[-1] for n in chart.findall("c:chart/c:plotArea/*", NS)
                        if n.tag.rsplit("}", 1)[-1].endswith("Chart")]
                result[f"P{number}:chart{index}"] = {
                    "workbooks": books, "types": kind,
                    "series_count": len(chart.findall(".//c:ser", NS)),
                    "formula_refs": [node.text for node in chart.findall(".//c:f", NS)],
                }
    return result


def verify_authoring_manifest(path: Path | None, source_sha: str) -> dict:
    """Verify retained local authoring files; never execute a manifest command."""
    if path is None:
        return {"verified": False, "reason": "No retained authoring manifest supplied"}
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("source_pptx_sha256") != source_sha or not manifest.get("files"):
        raise ValueError("Authoring manifest must bind source PPTX and retained files")
    if not {"authoring_code", "source_data"}.issubset(
        {entry.get("role") for entry in manifest["files"]}
    ):
        raise ValueError("Retained authoring code and source data are both required")
    base = path.parent.resolve()
    for entry in manifest["files"]:
        raw = Path(entry["path"])
        file = (base / raw).resolve(strict=True)
        if raw.is_absolute() or not file.is_relative_to(base):
            raise ValueError("Authoring files must remain inside the manifest directory")
        checked_bytes(file, entry["sha256"])
    return {"verified": True, "manifest_sha256": digest(path.read_bytes()),
            "verified_file_count": len(manifest["files"]),
            "boundary": "File identity only; not permission, provenance or generator execution proof"}


def preservation_gate(source: Path, candidate: Path, source_sha: str, candidate_sha: str,
                      *, mode: str = "edit", authoring_manifest: Path | None = None) -> dict:
    """Block lost charts/workbooks and formula loss; no automatic repair or release."""
    if mode not in {"edit", "regenerate"}:
        raise ValueError("Expected edit or regenerate mode")
    source_data = checked_bytes(source, source_sha)
    candidate_data = checked_bytes(candidate, candidate_sha)
    authoring = verify_authoring_manifest(authoring_manifest, source_sha)
    before = chart_inventory(source_data)
    issues = []
    try:
        after = chart_inventory(candidate_data)
        if set(before) != set(after):
            issues.append("Logical chart owners/counts changed; explicit remapping unsupported")
        for owner, old in before.items():
            new = after.get(owner)
            if new is None:
                continue
            if (old["types"] != new["types"] or old["series_count"] != new["series_count"]
                    or old["formula_refs"] != new["formula_refs"]
                    or len(old["workbooks"]) != len(new["workbooks"])):
                issues.append(owner + ": native chart type/series/range/workbook linkage changed")
                continue
            for original, edited in zip(old["workbooks"], new["workbooks"]):
                if original["formula_count"] and original["formula_sha256"] != edited["formula_sha256"]:
                    issues.append(owner + ": source workbook formulas changed or were lost")
                if edited["external_links"] > original["external_links"]:
                    issues.append(owner + ": new external workbook links unsupported")
    except (ValueError, KeyError, ET.ParseError, BadZipFile):
        issues.append("Candidate native chart/workbook package is broken or missing")
    if mode == "regenerate" and not authoring["verified"]:
        issues.append("Regeneration requires verified retained authoring files")
    unchanged = digest(source.read_bytes()) == source_sha and digest(candidate.read_bytes()) == candidate_sha
    if not unchanged:
        issues.append("Source or candidate bytes changed during inspection")
    passed = not issues
    return {"schema_version": 1, "operation": mode, "passed": passed,
            "candidate_deliverable": False, "delivery_blocked": not passed, "source_sha256": source_sha,
            "candidate_sha256": candidate_sha, "source_unchanged": unchanged,
            "source_chart_count": len(before), "issues": issues,
            "retained_authoring_source": authoring,
            "regeneration_eligible": authoring["verified"],
            "automatic_regeneration_executed": False, "engine_defect_fixed": False,
            "scope": "Relationship/formula preservation only; data/render/owner QA still required"}


def main(argv: list[str] | None = None) -> int:
    configure_utf8_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--candidate-sha256", required=True)
    parser.add_argument("--mode", choices=["edit", "regenerate"], default="edit")
    parser.add_argument("--authoring-manifest", type=Path)
    args = parser.parse_args(argv)
    try:
        report = preservation_gate(args.source, args.candidate, args.source_sha256,
                                   args.candidate_sha256, mode=args.mode,
                                   authoring_manifest=args.authoring_manifest)
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError, BadZipFile):
        report = {"passed": False, "candidate_deliverable": False,
                  "error": "Invalid or unverified preservation inputs", "engine_defect_fixed": False}
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
