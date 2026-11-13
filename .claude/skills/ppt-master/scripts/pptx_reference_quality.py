#!/usr/bin/env python3
"""PPT Master - Reference preservation and repair evidence.

Compare native text including grouped shapes/table cells and explicitly protected
XML/package parts. Never change input decks or treat unsupported objects as passed.

Usage: imported by dense_pptx_quality when a task declares reference_comparison.
Examples: see docs/ppt-project/REFERENCE_QUALITY.md.
Dependencies: None (standard library only).
"""
from __future__ import annotations

import collections
import hashlib
import json
import posixpath
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
KINDS = {"sp": "shape", "pic": "picture", "cxnSp": "connector", "grpSp": "group",
         "graphicFrame": "graphic_frame"}


def _digest(data):
    return hashlib.sha256(data).hexdigest()


def _tree(node):
    # Expanded names ignore namespace prefix spelling, but retain visible text.
    return [node.tag, sorted(node.attrib.items()), node.text if node.text and
            (node.tag == f"{{{NS['a']}}}t" or node.text.strip()) else None,
            [_tree(child) for child in node]]


def _paragraphs(node):
    return ["".join("\n" if c.tag == f"{{{NS['a']}}}br" else
                    c.findtext("a:t", "", NS) for c in p
                    if c.tag.rsplit("}", 1)[-1] in {"r", "fld", "br"})
            for p in node.findall(".//a:p", NS)]


def _relationships(package, part):
    relpath = posixpath.join(posixpath.dirname(part), "_rels", posixpath.basename(part)+".rels")
    if relpath not in package.namelist():
        return {}
    return {n.get("Id"): n for n in ET.fromstring(package.read(relpath))}


def _dependencies(package, part, element=None, seen=None):
    """Hash reachable package bytes too: unchanged rIds alone cannot protect assets."""
    seen = set() if seen is None else seen
    found = {}
    rels = _relationships(package, part)
    ids = ({v for n in element.iter() for k, v in n.attrib.items()
            if k.startswith("{"+NS["r"]+"}")} if element is not None else set(rels))
    for rid in sorted(ids):
        rel = rels.get(rid)
        if rel is None:
            raise ValueError(f"Missing relationship in protected object: {part}")
        target = rel.get("Target", "")
        if rel.get("TargetMode") == "External":
            raise ValueError("External protected dependency cannot be byte-verified")
        dest = posixpath.normpath(target.lstrip("/") if target.startswith("/") else
                                 posixpath.join(posixpath.dirname(part), target))
        # Preserve graph edges, not just the reachable set: two layouts can
        # reach the same master/all-layout graph while looking very different.
        found[f"{part}#{rid}"] = _digest(json.dumps(
            [rel.get("Type"), dest], sort_keys=True).encode())
        if dest in seen:
            continue
        seen.add(dest)
        found[dest] = _digest(package.read(dest))
        found.update(_dependencies(package, dest, seen=seen))
    return found


def _inventory(package):
    parts = sorted((n for n in package.namelist() if
                    re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
                   key=lambda n: int(re.search(r"slide(\d+)", n).group(1)))
    objects, text, tables, unverified, counts = {}, {}, {}, [], collections.Counter()

    def walk(parent, slide, prefix, part, ancestors=()):
        names = set()
        for index, node in enumerate(parent):
            tag = node.tag.rsplit("}", 1)[-1]
            if tag not in KINDS:
                if tag not in {"nvGrpSpPr", "grpSpPr", "extLst"}:
                    unverified.append({"target": prefix, "kind": tag})
                continue
            identity = node.find(".//p:cNvPr", NS)
            name = identity.get("name", "") if identity is not None else ""
            if not name or name in names:
                raise ValueError(f"Reference comparison requires unique object names in {prefix}")
            names.add(name)
            key = prefix + "/" + name
            if key in objects:
                raise ValueError("Ambiguous reference object path; use distinct native names")
            objects[key] = (part, node, ancestors, index)
            counts[KINDS[tag]] += 1
            if tag == "grpSp":
                props = node.find("p:grpSpPr", NS)
                context = (json.dumps(_tree(props), sort_keys=True),) if props is not None else ()
                walk(node, slide, key, part, ancestors + context)
                continue
            table = node.find(".//a:tbl", NS)
            if table is not None:
                counts["native_table"] += 1
                tables[key] = [[{k: cell.get(k, "1" if k in {"rowSpan", "gridSpan"} else "0")
                                 for k in ("rowSpan", "gridSpan", "hMerge", "vMerge")}
                                for cell in row.findall("a:tc", NS)]
                               for row in table.findall("a:tr", NS)]
                for ri, row in enumerate(table.findall("a:tr", NS)):
                    for ci, cell in enumerate(row.findall("a:tc", NS)):
                        text[f"{key}/R{ri}C{ci}"] = _paragraphs(cell)
                        counts["table_cell"] += 1
            else:
                text[key] = _paragraphs(node)
            if tag == "graphicFrame" and table is None:
                unverified.append({"target": key, "kind": "chart/diagram/other graphic frame",
                                   "reason": "native text/data/rendering needs dedicated checks"})

    for part in parts:
        root = ET.fromstring(package.read(part))
        walk(root.find("p:cSld/p:spTree", NS), part, part, part)
    return objects, text, tables, unverified, dict(counts), parts


def _slide_context(package, part):
    root = ET.fromstring(package.read(part))
    context = [sorted(root.attrib.items())]
    for child in root:
        if child.tag == f"{{{NS['p']}}}cSld":
            context.append([sorted(child.attrib.items()), [_tree(n) for n in child
                            if n.tag != f"{{{NS['p']}}}spTree"]])
        else:
            context.append(_tree(child))
    # Preserve inherited layout/master/theme as well as an object's local XML.
    dummy = ET.Element("context")
    for rid, rel in _relationships(package, part).items():
        if rel.get("Type", "").endswith("/slideLayout"):
            ET.SubElement(dummy, "layout", {f"{{{NS['r']}}}id": rid})
    return context, _dependencies(package, part, dummy)


def _photo_region_text(tree, name):
    # Resolve only the named region. Unrelated pictures may share export names.
    if tree is None:
        return None
    segments = name.split("/")
    node = tree
    for segment in segments:
        matches = [child for child in node if any(
            identity.get("name") == segment
            for identity in child.findall("./*/p:cNvPr", NS))]
        if not matches and node.tag == f"{{{NS['p']}}}graphicFrame":
            coordinates = re.fullmatch(r"R(\d+)C(\d+)", segment)
            if coordinates:
                row, col = map(int, coordinates.groups())
                matches = node.findall(f".//a:tbl/a:tr[{row + 1}]/a:tc[{col + 1}]", NS)
        if len(matches) != 1:
            return None
        node = matches[0]
    if node.tag == f"{{{NS['p']}}}sp":
        node = node.find("p:txBody", NS)
    if node is None or node.tag not in {f"{{{NS['p']}}}txBody", f"{{{NS['a']}}}tc"}:
        return None
    return _paragraphs(node)


def check_photo_text(candidate: Path, spec: dict, base: Path) -> dict:
    """Check approved photo transcription against named editable PPTX text."""
    source_hash = spec["sha256"]
    if _digest((base / spec["path"]).read_bytes()) != source_hash:
        raise ValueError("Photo source bytes differ from the approved source")
    regions = spec["regions"]
    if not isinstance(regions, list) or not regions:
        raise ValueError("Photo text contract requires reviewed regions")
    with zipfile.ZipFile(candidate) as package:
        presentation = "ppt/presentation.xml"
        relationships = _relationships(package, presentation)
        root = ET.fromstring(package.read(presentation))
        slide_parts = []
        for node in root.findall("p:sldIdLst/p:sldId", NS):
            rel = relationships[node.attrib[f"{{{NS['r']}}}id"]]
            target = rel.attrib["Target"]
            if rel.get("TargetMode") == "External" or not rel.get("Type", "").endswith("/slide"):
                raise ValueError("Photo text contract requires internal slide relationships")
            slide_parts.append(posixpath.normpath(target.lstrip("/") if target.startswith("/")
                                                  else posixpath.join("ppt", target)))
        trees = {
            page: ET.fromstring(package.read(part)).find("p:cSld/p:spTree", NS)
            for page, part in enumerate(slide_parts, start=1)
        }
    checks, errors, seen = [], [], set()
    for region in regions:
        page, name, status = region["slide"], region["object"], region["status"]
        if type(page) is not int or not 1 <= page <= len(slide_parts):
            raise ValueError("Photo text contract slide is outside the presentation")
        if (not isinstance(name, str) or any(not segment.strip() for segment in name.split("/"))
                or (page, name) in seen):
            raise ValueError("Photo text contract requires unique named regions per slide")
        seen.add((page, name))
        target = f"P{page}:{name}"
        actual = _photo_region_text(trees[page], name)
        expected = region.get("text")
        if status == "confirmed" and isinstance(expected, str) and expected.strip():
            passed = actual is not None and "\n".join(actual) == expected
        elif status == "unreadable" and "text" not in region:
            passed = actual == ["[판독 불가]"]
        else:
            raise ValueError("Photo text regions need confirmed text or unreadable status")
        checks.append({"target": target, "source_status": status, "passed": passed})
        if not passed:
            errors.append({"kind": "PHOTO_TRANSCRIPTION", "target": target,
                           "detail": "Named editable region differs from the approved text or unreadable marker",
                           "category": "mechanical"})
    return {"source_sha256": source_hash, "checks": checks, "errors": errors,
            "scope": "declared native text only; photo interpretation and visual fidelity require review"}


def compare_pptx(candidate: Path, reference: Path, spec: dict) -> dict:
    """Compare declared preservation scope; emit identifiers, never source text."""
    expected = spec.get("sha256")
    if not isinstance(expected, str) or not re.fullmatch(r"[a-f0-9]{64}", expected):
        raise ValueError("reference_comparison requires a pinned reference sha256")
    if _digest(reference.read_bytes()) != expected:
        raise ValueError("Reference bytes differ from the pinned baseline")
    if not any((spec.get("preserve_text"), spec.get("protected_objects"), spec.get("protected_parts"))):
        raise ValueError("Reference comparison needs a nonempty preservation scope")
    errors, checks = [], []

    def check(ok, kind, target):
        checks.append({"kind": kind, "target": target, "status": "pass" if ok else "fail"})
        if not ok:
            errors.append({"kind": kind, "target": target,
                           "detail": "Final output differs from the pinned preservation scope",
                           "category": "mechanical"})

    with zipfile.ZipFile(reference) as before, zipfile.ZipFile(candidate) as after:
        old, old_text, old_tables, old_unknown, old_counts, old_slides = _inventory(before)
        new, new_text, new_tables, new_unknown, new_counts, new_slides = _inventory(after)
        check(old_slides == new_slides and before.read("ppt/presentation.xml") ==
              after.read("ppt/presentation.xml"), "REFERENCE_PRESENTATION", "deck")
        if spec.get("preserve_text"):
            for key in sorted(old_text.keys() | new_text.keys()):
                check(key in old_text and key in new_text and old_text[key] == new_text[key],
                      "REFERENCE_TEXT", key)
            for key in sorted(old_tables.keys() | new_tables.keys()):
                check(key in old_tables and key in new_tables and old_tables[key] == new_tables[key],
                      "REFERENCE_TABLE_STRUCTURE", key)
        for item in spec.get("protected_objects", []):
            key = f"ppt/slides/slide{int(item['slide'])}.xml/" + item["name"]
            exists = key in old and key in new
            same = (exists and _tree(old[key][1]) == _tree(new[key][1]) and
                    old[key][2:] == new[key][2:])
            if same:
                same = (_dependencies(before, old[key][0], old[key][1]) ==
                        _dependencies(after, new[key][0], new[key][1]))
            if same:
                same = _slide_context(before, old[key][0]) == _slide_context(after, new[key][0])
            check(same, "REFERENCE_PROTECTED_OBJECT", key)
        for part in spec.get("protected_parts", []):
            same = part in before.namelist() and part in after.namelist()
            if same:
                same = before.read(part) == after.read(part)
                if same:
                    same = _dependencies(before, part) == _dependencies(after, part)
            check(same, "REFERENCE_PROTECTED_PART", part)
        unknown = {json.dumps(n, sort_keys=True): n for n in old_unknown + new_unknown}
        if unknown and spec.get("require_complete_text_coverage"):
            errors.append({"kind": "REFERENCE_UNVERIFIED", "target": "deck",
                           "detail": "Some native objects require dedicated text/data checks",
                           "category": "mechanical"})
    return {"reference_sha256": expected, "candidate_sha256": _digest(candidate.read_bytes()),
            "errors": errors, "checks": checks,
            "coverage": {"reference": old_counts, "candidate": new_counts,
                         "unverified": list(unknown.values())},
            "status": "fail" if errors else "partial" if unknown else "pass",
            "boundary": "Native DrawingML text/protected package bytes only; no rendered or application QA"}


def track_repairs(before: dict, after: dict) -> dict:
    """Count finding transitions from two actual runs of the same task contract."""
    old = collections.Counter((e["target"], e["kind"]) for e in before["errors"])
    new = collections.Counter((e["target"], e["kind"]) for e in after["errors"])
    records = []
    for target, kind in sorted(old.keys() | new.keys()):
        a, b = old[(target, kind)], new[(target, kind)]
        # An unverified/missing target is not a repaired target.
        object_target = re.sub(r":R\d+C\d+$", "", target)
        blocked = kind.startswith("UNVERIFIED") or any(e["kind"].startswith(("UNVERIFIED", "MISSING")) and
                      (target.startswith(e["target"]) or e["target"].startswith(object_target))
                      for e in after["errors"])
        records.append({"target": target, "kind": kind, "before": a, "after": b,
                        "status": "unverified" if blocked else "resolved" if a and not b else
                        "new" if not a else "remaining"})
    return {"baseline_sha256": before["deck_sha256"], "final_sha256": after["deck_sha256"],
            "same_contract": True, "records": records,
            "boundary": "Mechanical findings only; no claim of visual/application repair"}
