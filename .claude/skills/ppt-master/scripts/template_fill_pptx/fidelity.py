"""Opt-in company-template lock: original bytes and explicitly editable areas.

Does not certify rendering or resolve inherited fonts. The native XML comparison
keeps typography, margins, geometry, fixed text, fields and chrome untouched.
"""

from __future__ import annotations

import copy
import hashlib
from xml.etree import ElementTree as ET

from .ooxml import NS
from .text_fill import _shape_key_maps
from .table_fill import _table_key_maps


def validate_source_lock(pptx_path, plan, transition):
    contract = plan.get("template_fidelity")
    if contract is None:
        return False
    if not isinstance(contract, dict) or contract.get("schema_version") != 1:
        raise RuntimeError("template_fidelity requires schema_version 1")
    if contract.get("source_sha256") != hashlib.sha256(pptx_path.read_bytes()).hexdigest():
        raise RuntimeError("Template fidelity source SHA256 mismatch; review original again")
    if transition != "keep":
        raise RuntimeError("Template fidelity requires --transition keep")
    for item in plan.get("slides", []):
        if any(key in item for key in ("notes", "speaker_notes", "transition")):
            raise RuntimeError("Template fidelity preserves source notes and transitions")
        if item.get("chart_edits"):
            raise RuntimeError("Template fidelity v1 preserves charts unchanged")
        allowed = item.get("editable_targets")
        if not isinstance(allowed, dict):
            raise RuntimeError("Template fidelity requires per-slide editable_targets")
        slots = allowed.get("slots", [])
        cells = allowed.get("table_cells", [])
        if (not isinstance(slots, list) or not all(isinstance(s, str) for s in slots)
                or not isinstance(cells, list) or not all(isinstance(c, dict) for c in cells)):
            raise RuntimeError("Invalid editable_targets lists")
        for replacement in item.get("replacements", []):
            if (replacement.get("slot_id") not in slots
                    or any(k in replacement for k in ("shape_id", "shape_name", "optional"))):
                raise RuntimeError("Replacement outside explicit editable slot allowlist")
            if "paragraph_run_texts" not in replacement:
                raise RuntimeError("Template fidelity requires paragraph_run_texts for slots")
        for table in item.get("table_edits", []):
            if any(k in table for k in ("shape_id", "shape_name", "optional")):
                raise RuntimeError("Template fidelity requires canonical table_id")
            for cell in table.get("cells", []):
                if type(cell.get("row")) is not int or type(cell.get("col")) is not int:
                    raise RuntimeError("Template fidelity cell indices must be integers")
                key = {"table_id": table.get("table_id"), "row": cell.get("row"), "col": cell.get("col")}
                if key not in cells:
                    raise RuntimeError("Table edit outside explicit editable cell allowlist")
                if "paragraph_run_texts" not in cell:
                    raise RuntimeError("Template fidelity requires paragraph_run_texts for cells")
    return True


def _signature(node):
    # Namespace prefixes, attribute order and pretty-print whitespace are not
    # content. Keep all meaningful XML, including paragraph/run styles.
    return (node.tag, tuple(sorted(node.attrib.items())),
            node.text if node.text and node.text.strip() else "",
            tuple(_signature(child) for child in node))


def _mask_editable_text(root, source_slide, item):
    slots = _shape_key_maps(root, source_slide)
    for replacement in item.get("replacements", []):
        target = slots.get("slot_id:" + replacement["slot_id"])
        if target is None:
            raise RuntimeError("Template fidelity slot missing from source/output")
        if target.find(".//a:fld", NS) is not None:
            raise RuntimeError("Template fidelity cannot replace dynamic field text")
        for node in target.findall(".//a:t", NS):
            node.text = "<editable>"
    tables = _table_key_maps(root, source_slide)
    for table in item.get("table_edits", []):
        frame = tables.get("table_id:" + table["table_id"])
        if frame is None:
            raise RuntimeError("Template fidelity table missing from source/output")
        for cell in table.get("cells", []):
            rows = frame.findall(".//a:tbl/a:tr", NS)
            target = rows[cell["row"]].findall("a:tc", NS)[cell["col"]]
            if target.find(".//a:fld", NS) is not None:
                raise RuntimeError("Template fidelity cannot replace table fields")
            for node in target.findall(".//a:t", NS):
                node.text = "<editable>"


def validate_slide_fidelity(before, after, source_slide, item):
    before, after = copy.deepcopy(before), copy.deepcopy(after)
    _mask_editable_text(before, source_slide, item)
    _mask_editable_text(after, source_slide, item)
    if _signature(before) != _signature(after):
        raise RuntimeError("Template fidelity changed formatting, geometry or a fixed element")


def validate_shared_parts(original, output):
    prefixes = ("ppt/slideMasters/", "ppt/slideLayouts/", "ppt/theme/", "ppt/media/", "ppt/fonts/")
    for name, data in output.items():
        if name.startswith(prefixes) and (name not in original or data != original[name]):
            raise RuntimeError("Template fidelity changed shared design part: " + name)
    if ET.fromstring(original["ppt/presentation.xml"]).find("p:sldSz", NS).attrib != ET.fromstring(
            output["ppt/presentation.xml"]).find("p:sldSz", NS).attrib:
        raise RuntimeError("Template fidelity changed slide size")
