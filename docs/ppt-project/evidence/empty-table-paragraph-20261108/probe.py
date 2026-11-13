"""Reproduce blank paragraph-mark faults using the existing public dense deck.

No fonts are loaded: this is a structural fault probe, not a render test.
Pass an output directory outside the repository; no fixture overwrites occur.
"""
from pathlib import Path
import copy
import importlib.util
import json
import sys
import zipfile
from xml.etree import ElementTree as ET


def main():
    root = Path(__file__).resolve().parents[4]
    work = Path(sys.argv[1]).resolve()
    work.mkdir(parents=True, exist_ok=True)
    scripts = root / ".claude/skills/ppt-master/scripts"
    sys.path.insert(0, str(scripts))
    spec = importlib.util.spec_from_file_location("dense_probe", scripts / "dense_pptx_quality.py")
    dense = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dense)
    ns = dense.NS
    source = root / "docs/ppt-project/evidence/reference-quality-20261107/after.pptx"
    contract = {
        "font_family": "Pretendard", "text_metrics": "structure_only",
        "slide_size_pt": [960, 540],
        "slides": [{"slide": 1, "region_pt": [0, 0, 960, 540], "objects": {
            "process-table": {"kind": "table", "header_rows": 1, "header_pt": 12,
                              "header_max_pt": 12, "body_pt": 11, "max_font_pt": 12}
        }}],
    }
    strict = copy.deepcopy(contract)
    strict["slides"][0]["objects"]["process-table"]["require_empty_cell_paragraph_style"] = True

    def target(root):
        return next(f for f in root.findall(".//p:graphicFrame", ns)
                    if f.find("p:nvGraphicFramePr/p:cNvPr", ns).get("name") == "process-table")

    with zipfile.ZipFile(source) as z:
        original = {info.filename: z.read(info.filename) for info in z.infolist()}
    tree = ET.fromstring(original["ppt/slides/slide1.xml"])
    body = target(tree).find(".//a:tbl", ns).findall("a:tr", ns)[1].find("a:tc/a:txBody", ns)
    para = ET.SubElement(body, f"{{{ns['a']}}}p")
    mark = ET.SubElement(para, f"{{{ns['a']}}}endParaRPr", {"sz": "1100"})
    for slot in ("latin", "ea"):
        ET.SubElement(mark, f"{{{ns['a']}}}{slot}", {"typeface": "Pretendard"})
    stable = ET.tostring(tree)
    results = []
    for mode in ("correct", "missing_mark", "oversized_18pt", "wrong_ea_family", "missing_ea"):
        page = ET.fromstring(stable)
        body = target(page).find(".//a:tbl", ns).findall("a:tr", ns)[1].find("a:tc/a:txBody", ns)
        p = body.findall("a:p", ns)[-1]
        mark = p.find("a:endParaRPr", ns)
        if mode == "missing_mark":
            p.remove(mark)
        elif mode == "oversized_18pt":
            mark.set("sz", "1800")
        elif mode == "wrong_ea_family":
            mark.find("a:ea", ns).set("typeface", "SomeOtherFamily")
        elif mode == "missing_ea":
            mark.remove(mark.find("a:ea", ns))
        output = work / f"{mode}.pptx"
        with zipfile.ZipFile(output, "x", zipfile.ZIP_DEFLATED) as z:
            for name, data in original.items():
                z.writestr(name, ET.tostring(page) if name == "ppt/slides/slide1.xml" else data)
        report = dense.inspect_pptx(output, strict, root)
        hits = [e["kind"] for e in report["errors"] if e["kind"].startswith("EMPTY_CELL_")]
        assert bool(hits) == (mode != "correct"), (mode, hits)
        default = dense.inspect_pptx(output, contract, root)
        assert "empty_table_paragraph_check" not in default
        assert not any(e["kind"].startswith("EMPTY_CELL_") for e in default["errors"])
        results.append({"case": mode, "guard_errors": len(hits),
                        "kinds": sorted(set(hits)), "pass": True})
    print(json.dumps({"scope": "synthetic structural fault probe; not native rendering",
                      "results": results, "passed": True}, indent=2))


if __name__ == "__main__":
    main()
