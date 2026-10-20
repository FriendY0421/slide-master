#!/usr/bin/env python3
"""
PPT Master - Cloud Existing-File Review

Run existing host package/layout checks and the reviewed 0.4.3 renderer against
one exact PPTX. This is a read-only QA adapter, not a generator, authentication
adapter, approval issuer, font installer, uploader or FAH deployment.
Post-edit callers must select --operation edit and bind the pre-edit source.
Regenerate additionally requires retained authoring code/data hashes. See
docs/ppt-project/CHART_WORKBOOK_PRESERVATION.md for the fail-closed workflow.

Usage:
    python3 cloud_review_existing.py DECK --expected-sha256 SHA --profile PROFILE
        --host-skill-dir DIR --review-scripts DIR --output NEW_DIR

Examples:
    Use the supplied runtime environment variables and a task-local licensed-font
    profile. Keep input, output, receipts and fonts in the private task workspace.

Dependencies:
    Existing host fontTools, validators and reviewed renderer dependencies.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
import re
import subprocess
import xml.etree.ElementTree as ET
from zipfile import BadZipFile, ZipFile
from pathlib import Path

from console_encoding import configure_utf8_stdio
from chart_workbook_preservation import preservation_gate


RUNTIME_KEYS = (
    "CODEX_PRIMARY_RUNTIME_NODE",
    "CODEX_PRIMARY_RUNTIME_NODE_MODULES",
    "CODEX_PRIMARY_RUNTIME_PYTHON",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def supplied_runtime(environ: dict[str, str]) -> dict[str, Path]:
    """Resolve only the host-supplied runtime. Never search/install fallbacks."""
    result = {}
    for key in RUNTIME_KEYS:
        value = environ.get(key, "")
        if not value or not Path(value).is_absolute():
            raise ValueError(f"Missing absolute supplied runtime path: {key}")
        candidate = Path(value).resolve(strict=True)
        if key.endswith("_MODULES"):
            if not candidate.is_dir():
                raise ValueError(f"Runtime module path is not a directory: {key}")
        elif not candidate.is_file() or not os.access(candidate, os.X_OK):
            raise ValueError(f"Runtime executable unavailable: {key}")
        result[key] = candidate
    artifact = result[RUNTIME_KEYS[1]] / "@oai/artifact-tool/package.json"
    if not artifact.is_file():
        raise ValueError("Supplied Artifact Tool package unavailable")
    return result


def validate_profile(profile_path: Path) -> dict:
    """Verify supplied font bytes. The host must establish usage rights separately."""
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    if not isinstance(profile, dict):
        raise ValueError("Font profile must be an object")
    family = profile.get("font_family")
    if not isinstance(family, str) or not family.strip():
        raise ValueError("Explicit font family required")
    if not isinstance(profile.get("font_files"), list) or not profile["font_files"]:
        raise ValueError("Actual licensed font files required")
    for item in profile["font_files"]:
        if not re.fullmatch(r"[a-f0-9]{64}", item.get("sha256", "")):
            raise ValueError("A verified font SHA256 is required")
        font = (profile_path.parent / item["path"]).resolve(strict=True)
        if sha256(font) != item["sha256"]:
            raise ValueError("Font bytes changed")
    return profile


def font_metadata(path: Path) -> dict:
    """Read the actual static face, not its filename or caller-supplied role."""
    from fontTools.ttLib import TTFont, TTLibError

    try:
        with TTFont(path, lazy=False) as font:
            if "fvar" in font:
                raise ValueError("Variable fonts require a separate verified face route")
            names, os2, head, post = font["name"], font["OS/2"], font["head"], font["post"]
            weight = int(os2.usWeightClass)
            role = {400: "regular", 700: "bold"}.get(weight)
            if role is None or int(os2.usWidthClass) != 5:
                raise ValueError("Only static normal-width Regular 400 / Bold 700 faces are supported")
            if os2.fsSelection & ((1 << 0) | (1 << 9)) or head.macStyle & 2 or post.italicAngle != 0:
                raise ValueError("Italic/oblique faces are not supported by the existing dense checker")
            bold = role == "bold"
            # Some numeric subfamilies are separate weight faces rather than
            # legacy style-linked Bold. Preserve their bytes and require both
            # legacy flags to agree, an exact numeric name, and OS/2 weight.
            numeric_weight_face = (
                names.getBestSubFamilyName() == str(weight)
                and not os2.fsSelection & 32 and not head.macStyle & 1
                and bool(os2.fsSelection & 64)
            )
            if not numeric_weight_face and (
                bool(os2.fsSelection & 32) != bold or bool(head.macStyle & 1) != bold
            ):
                raise ValueError("Font weight and bold style flags disagree")
            if not numeric_weight_face and bool(os2.fsSelection & 64) == bold:
                raise ValueError("Font regular style flag disagrees with its weight")
            return {
                "role": role, "family": names.getBestFamilyName(),
                "subfamily": names.getBestSubFamilyName(),
                "weight": weight, "style": "normal", "width": "normal",
            }
    except (TTLibError, KeyError) as exc:
        raise ValueError("A readable single-face static OpenType font is required") from exc


def bind_dense_fonts(dense: dict, contract_path: Path, profile: dict,
                     profile_path: Path) -> dict[str, dict]:
    """Bind role -> actual metadata -> exact bytes for both consumers."""
    family = profile["font_family"]
    faces = dense.get("font_files", {}).get(family)
    if not isinstance(faces, dict) or not faces:
        raise ValueError("Dense contract requires explicit actual face files")
    bindings = {}
    for face, spec in faces.items():
        if face not in {"regular", "bold"} or not isinstance(spec, dict):
            raise ValueError("Unsupported dense font face")
        if spec.get("index", 0) != 0:
            raise ValueError("Nonzero font collection indexes are unsupported")
        digest = spec.get("sha256", "")
        if not re.fullmatch(r"[a-f0-9]{64}", digest):
            raise ValueError("Each dense font face requires a verified SHA256")
        font = (contract_path.parent / spec["path"]).resolve(strict=True)
        if sha256(font) != digest:
            raise ValueError(f"Dense {face} font bytes changed")
        metadata = font_metadata(font)
        if metadata["role"] != face or metadata["family"] != family:
            raise ValueError(f"Dense {face} role/family disagrees with actual font metadata")
        bindings[face] = {**metadata, "sha256": digest, "dense_path": str(font)}
    renderer_roles = {}
    for entry in profile["font_files"]:
        font = (profile_path.parent / entry["path"]).resolve(strict=True)
        if sha256(font) != entry["sha256"]:
            raise ValueError("Renderer font bytes changed")
        metadata = font_metadata(font)
        role = metadata["role"]
        if metadata["family"] != family or role in renderer_roles:
            raise ValueError("Renderer family/face mapping is ambiguous")
        renderer_roles[role] = {**metadata, "sha256": entry["sha256"], "path": str(font)}
    if set(bindings) != set(renderer_roles):
        raise ValueError("Dense and renderer face roles differ")
    for role, bound in bindings.items():
        rendered = renderer_roles[role]
        if any(bound[key] != rendered[key] for key in ("family", "weight", "style", "width", "sha256")):
            raise ValueError("Dense and renderer role-specific font bytes/metadata differ")
        bound["renderer_path"] = rendered["path"]
    return bindings


# The same supported API used by the unmodified 0.4.3 renderer. Its per-file
# registration metadata is checked; aggregate family lists are not face proof.
RENDERER_FONT_PROBE = r"""
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {createRequire}=require('node:module');
const [runtime,profilePath]=process.argv.slice(1);
const req=createRequire(path.join(runtime,'@oai/artifact-tool/package.json'));
const skia=req('skia-canvas'),profile=JSON.parse(fs.readFileSync(profilePath,'utf8'));
const hash=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const paths=profile.font_files.map(entry=>{
  const file=fs.realpathSync(path.resolve(path.dirname(profilePath),entry.path));
  if(hash(file)!==entry.sha256) throw new Error('Font profile bytes changed');
  return file;
});
const faces=skia.FontLibrary.use(profile.font_family,paths);
console.log(JSON.stringify(faces.map(face=>({...face,file:fs.realpathSync(face.file),sha256:hash(face.file)}))));
"""


def check_renderer_faces(records: list, bindings: dict[str, dict]) -> None:
    """Validate Skia's actual per-file role mapping against measurement faces."""
    if not isinstance(records, list) or len(records) != len(bindings):
        raise ValueError("Renderer registration must return each unique bound face")
    seen = set()
    for record in records:
        role = {400: "regular", 700: "bold"}.get(record.get("weight"))
        if role not in bindings or role in seen:
            raise ValueError("Renderer face role is unsupported or ambiguous")
        bound = bindings[role]
        if any(record.get(key) != bound[key] for key in ("family", "weight", "style", "width", "sha256")):
            raise ValueError("Renderer role/metadata differs from the measured face")
        if str(Path(record["file"]).resolve(strict=True)) != bound["renderer_path"]:
            raise ValueError("Renderer face path differs from the bound profile")
        seen.add(role)


def check_font_receipt(name: str, output: Path, bindings: dict[str, dict], dense: dict) -> None:
    """Check the actual measurement/render paths and hashes against bound roles."""
    path_key = "dense_path" if name == "dense" else "renderer_path"
    expected = {face[path_key]: face["sha256"] for face in bindings.values()}
    if name == "dense":
        report = json.loads((output / "dense-report.json").read_text(encoding="utf-8"))
        measured = report.get("font_files_sha256")
        if report.get("text_metrics_mode") != "actual_font" or not isinstance(measured, dict):
            raise ValueError("Actual-font dense receipt required")
        text_required = any(
            obj.get("kind") in {"text", "table"}
            for slide in dense.get("slides", []) for obj in slide.get("objects", {}).values()
        )
        if text_required and not measured:
            raise ValueError("Dense receipt contains no measured font files")
        if any(path not in expected or expected[path] != digest for path, digest in measured.items()):
            raise ValueError("Measured dense fonts differ from bound renderer font bytes/roles")
    elif name == "render":
        report = json.loads((output / "render/render-manifest.json").read_text(encoding="utf-8"))
        registered = report.get("registered_fonts")
        if not isinstance(registered, dict) or registered != expected:
            raise ValueError("Actual renderer font bytes/paths differ from the dense bindings")


def check_dense_style_scope(deck: Path, dense: dict) -> None:
    """Fail closed for styles the unchanged dense checker does not measure."""
    if not any(obj.get("kind") in {"text", "table"}
               for slide in dense.get("slides", []) for obj in slide.get("objects", {}).values()):
        return
    # This intentionally conservative package-wide guard also catches inherited
    # italic declarations. It does not claim to resolve every run's font choice.
    ns = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
    with ZipFile(deck) as package:
        roots = {}
        for name in package.namelist():
            if not name.startswith("ppt/") or not name.endswith(".xml"):
                continue
            roots[name] = ET.fromstring(package.read(name))
            for props in roots[name].iter():
                if props.tag not in {ns + "rPr", ns + "defRPr", ns + "endParaRPr"}:
                    continue
                if props.get("i") not in {None, "0", "false"}:
                    raise ValueError("Italic DrawingML is unsupported by the existing dense checker")
                if props.tag == ns + "rPr" and props.get("b") not in {None, "0", "1", "false"}:
                    raise ValueError("Unsupported bold encoding: existing dense checker requires b=1")
        check_inherited_bold_scope(roots, dense)


def check_inherited_bold_scope(roots: dict, dense: dict) -> None:
    """Allow omitted b only in plain text with no applicable bold default."""
    ns = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
          "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}

    def bold_default(element):
        return any(prop.get("b") not in {None, "0", "false"}
                   for prop in element.findall(".//a:defRPr", ns))

    # A non-placeholder text shape can inherit the presentation default and
    # master otherStyle. Check every master conservatively, not unrelated layout
    # placeholders. Placeholder/table runs require an explicit b instead.
    global_bold = any(
        bold_default(style)
        for root in roots.values()
        for xpath in (".//p:defaultTextStyle", ".//p:otherStyle")
        for style in root.findall(xpath, ns)
    )
    for page in dense.get("slides", []):
        root = roots.get(f"ppt/slides/slide{int(page.get('slide', 1))}.xml")
        if root is None:
            continue  # The existing dense checker rejects missing slides/objects.
        shapes = root.findall("p:cSld/p:spTree/*", ns)
        found = {}
        for shape in shapes:
            identity = shape.find(".//p:cNvPr", ns)
            if identity is not None:
                found.setdefault(identity.get("name"), []).append(shape)
        for name, expected in page.get("objects", {}).items():
            if expected.get("kind") not in {"text", "table"}:
                continue
            matches = found.get(name, [])
            if len(matches) != 1 and expected.get("text_equals"):
                matches = [shape for shape in shapes if "".join(
                    text.text or "" for text in shape.findall(".//a:t", ns)
                ) == expected["text_equals"]]
            if len(matches) != 1:
                continue
            shape = matches[0]
            bodies = (shape.findall(".//a:txBody", ns) if expected["kind"] == "table"
                      else shape.findall("p:txBody", ns))
            for body in bodies:
                missing_bold = any(
                    run.findtext("a:t", "", ns) and
                    (run.find("a:rPr", ns) is None or run.find("a:rPr", ns).get("b") is None)
                    for paragraph in body.findall("a:p", ns) for run in paragraph
                    if run.tag in {"{" + ns["a"] + "}r", "{" + ns["a"] + "}fld"}
                )
                if missing_bold and (expected["kind"] == "table" or
                                     shape.find(".//p:ph", ns) is not None or
                                     global_bold or bold_default(body)):
                    raise ValueError("Inherited bold is unverified; measured runs require explicit b")



def inspect_dense_scope(deck: Path, dense: dict, bindings: dict) -> dict:
    """Preflight explicit single-family text and logical order; never rewrite OOXML.

    The external dense checker still selects ea for a whole run and addresses
    slideN.xml physically. Reject unsupported inputs rather than certify them.
    Counts concern top-level native objects, including uncontracted objects.
    """
    from fontTools.ttLib import TTFont

    ns = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
          "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
          "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
    rel_ns = "{http://schemas.openxmlformats.org/package/2006/relationships}"
    coverage = {}
    for role, binding in bindings.items():
        path = Path(binding["dense_path"])
        if sha256(path) != binding["sha256"]:
            raise ValueError("Bound font bytes changed before cmap inspection")
        with TTFont(path) as font:
            # getBestCmap maps real Unicode codepoints to glyph names. A mapping
            # to glyph zero/.notdef is not evidence of a drawable character.
            coverage[role] = {cp for cp, glyph in (font.getBestCmap() or {}).items()
                              if font.getGlyphID(glyph) != 0}
    errors, records, order = [], [], []
    with ZipFile(deck) as package:
        pres = ET.fromstring(package.read("ppt/presentation.xml"))
        rels = ET.fromstring(package.read("ppt/_rels/presentation.xml.rels"))
        relations = {}
        for rel in rels.findall(rel_ns + "Relationship"):
            if rel.get("Id") in relations:
                raise ValueError("Duplicate presentation relationship ID")
            relations[rel.get("Id")] = rel
        for number, entry in enumerate(pres.findall("p:sldIdLst/p:sldId", ns), 1):
            rel = relations.get(entry.get("{" + ns["r"] + "}id"))
            if rel is None or rel.get("TargetMode", "Internal") != "Internal" or not (
                rel.get("Type", "").endswith("/slide")
            ):
                raise ValueError("Logical slide relationship is missing or unsupported")
            target = rel.get("Target", "")
            part = posixpath.normpath(target.lstrip("/") if target.startswith("/")
                                      else posixpath.join("ppt", target))
            if part in order or part not in package.namelist():
                raise ValueError("Duplicate or missing logical slide part")
            order.append(part)
            if part != f"ppt/slides/slide{number}.xml":
                errors.append(f"P{number}: logical/physical slide order differs; dense mapping unsupported")
        if not order:
            raise ValueError("Presentation has no logical slides")
        targets = {}
        for page in dense.get("slides", []):
            number = int(page.get("slide", 1))
            if number < 1 or number > len(order) or number in targets:
                raise ValueError("Dense slide target is duplicate or outside logical slide order")
            targets[number] = page.get("objects", {})
        for number, part in enumerate(order, 1):
            root = ET.fromstring(package.read(part))
            shapes = [shape for shape in root.findall("p:cSld/p:spTree/*", ns)
                      if shape.tag.rsplit("}", 1)[-1] not in {"nvGrpSpPr", "grpSpPr", "extLst"}]
            matched = set()
            for name, expected in targets.get(number, {}).items():
                matches = [i for i, shape in enumerate(shapes)
                           if (shape.find(".//p:cNvPr", ns) is not None and
                               shape.find(".//p:cNvPr", ns).get("name") == name)]
                if len(matches) != 1 and expected.get("text_equals"):
                    matches = [i for i, shape in enumerate(shapes) if "".join(
                        t.text or "" for t in shape.findall(".//a:t", ns)) == expected["text_equals"]]
                issue = [] if part == f"ppt/slides/slide{number}.xml" else [
                    "Logical/physical slide mapping unsupported"]
                if len(matches) != 1 or matches[0] in matched:
                    records.append({"target": f"P{number}:{name}", "status": "unsupported",
                                    "issues": ["Missing, duplicate or multiply selected object"]})
                    continue
                index = matches[0]
                matched.add(index)
                shape = shapes[index]
                kind = expected.get("kind")
                tag = shape.tag.rsplit("}", 1)[-1]
                required_tag = {"text": "sp", "table": "graphicFrame", "shape": "sp", "image": "pic"}
                if tag != required_tag.get(kind):
                    issue.append("Object kind/group is unsupported by dense inspection")
                if kind in {"text", "table"}:
                    bodies = (shape.findall(".//a:txBody", ns) if kind == "table"
                              else shape.findall("p:txBody", ns))
                    if not bodies or (kind == "table" and shape.find(".//a:tbl", ns) is None):
                        issue.append("Required native text/table body missing")
                    for body in bodies:
                        for run in body.findall("a:p/*", ns):
                            if run.tag.rsplit("}", 1)[-1] not in {"r", "fld"}:
                                continue
                            text = run.findtext("a:t", "", ns)
                            if not text:
                                continue
                            props = run.find("a:rPr", ns)
                            if props is None:
                                issue.append("Explicit final run properties required")
                                continue
                            # Requiring both explicit slots avoids theme/layout
                            # fallback and the ea-first whole-run measurement bug.
                            for slot in ("latin", "ea"):
                                nodes = props.findall("a:" + slot, ns)
                                if len(nodes) != 1 or nodes[0].get("typeface") != dense["font_family"]:
                                    issue.append(f"Font slot {slot} must explicitly match the bound family")
                            cs = props.find("a:cs", ns)
                            if cs is not None and cs.get("typeface") != dense["font_family"]:
                                issue.append("Complex-script font slot differs from the bound family")
                            if "\t" in text:
                                issue.append("Tab-stop layout is not verified by the dense estimator")
                            role = "bold" if props.get("b") == "1" else "regular"
                            if role not in coverage:
                                issue.append(f"No bound actual {role} face")
                            else:
                                missing = sorted({ord(ch) for ch in text if ch not in "\n\r\t"}
                                                 - coverage[role])
                                if missing:
                                    issue.append("Actual cmap lacks " + ", ".join(f"U+{cp:04X}" for cp in missing))
                records.append({"target": f"P{number}:{name}",
                                "status": "unsupported" if issue else "supported", "issues": sorted(set(issue))})
            for index, shape in enumerate(shapes):
                if index not in matched:
                    records.append({"target": f"P{number}:object[{index}]", "status": "uninspected", "issues": []})
    unsupported = sum(r["status"] == "unsupported" for r in records)
    return {"status": "preflight_passed" if not errors and not unsupported else "unsupported",
            "logical_slide_parts": order, "logical_order_supported": not errors,
            "supported_objects": sum(r["status"] == "supported" for r in records),
            "completed_objects": 0, "unsupported_objects": unsupported,
            "uninspected_objects": sum(r["status"] == "uninspected" for r in records),
            "objects": records, "errors": errors, "passed": not errors and unsupported == 0}


def review(args: argparse.Namespace) -> dict:
    deck = args.deck.resolve(strict=True)
    if not re.fullmatch(r"[a-f0-9]{64}", args.expected_sha256):
        raise ValueError("Expected exact-file SHA256 is required")
    if sha256(deck) != args.expected_sha256:
        raise ValueError("PPTX differs from the expected exact final file")
    profile_path = args.profile.resolve(strict=True)
    profile = validate_profile(profile_path)
    runtime = supplied_runtime(dict(os.environ))
    host = args.host_skill_dir.resolve(strict=True) / "container_tools"
    scripts = args.review_scripts.resolve(strict=True)
    required = [
        host / "inspect_presentation_package_integrity.py",
        host / "inspect_presentation_layout_geometry.py",
        scripts / "render_pptx_review.py",
        scripts / "render_pptx_review.mjs",
    ]
    operation = getattr(args, "operation", "review")
    edit_source = getattr(args, "edit_source", None)
    edit_source_sha = getattr(args, "edit_source_sha256", None)
    authoring_manifest = getattr(args, "authoring_manifest", None)
    if operation in {"edit", "regenerate"} and (not edit_source or not edit_source_sha):
        raise ValueError("Edit/regenerate review requires exact pre-edit source and SHA256")
    if operation == "review" and (edit_source or edit_source_sha or authoring_manifest):
        raise ValueError("Explicit edit/regenerate operation required for preservation inputs")
    preservation = {"status": "not_requested"}
    dense = None
    font_bindings = {}
    dense_scope = {"status": "not_requested", "completed_objects": 0,
                   "unsupported_objects": None, "uninspected_objects": None}
    if args.dense_contract:
        dense_scope["status"] = "not_executed"
        required.append(scripts / "dense_pptx_quality.py")
        contract_path = args.dense_contract.resolve(strict=True)
        dense = json.loads(contract_path.read_text(encoding="utf-8"))
        if not isinstance(dense, dict) or dense.get("text_metrics", "actual_font") != "actual_font":
            raise ValueError("Structure-only dense checks cannot satisfy final QA")
        if dense.get("font_family") != profile["font_family"]:
            raise ValueError("Dense contract and renderer must use the same required font")
        font_bindings = bind_dense_fonts(dense, contract_path, profile, profile_path)
        check_dense_style_scope(deck, dense)
    for path in required:
        if not path.is_file():
            raise ValueError(f"Required existing QA component unavailable: {path.name}")
    output = args.output.resolve()
    if output == deck.parent or output in deck.parents:
        raise ValueError("Review output must be separate from the source directory")
    output.mkdir(parents=True, exist_ok=False)
    python = str(runtime["CODEX_PRIMARY_RUNTIME_PYTHON"])
    commands = [
        ("package", [python, str(required[0]), str(deck), "--fail-on-findings"]),
        ("layout", [
            python, str(required[1]), str(deck),
            "--approved-font-family", profile["font_family"],
            "--validate-bullet-geometry", "--validate-heading-fit",
            "--fail-on-findings",
        ]),
    ]
    if args.dense_contract:
        commands.append(("dense", [
            python, str(scripts / "dense_pptx_quality.py"), str(deck),
            "--contract", str(args.dense_contract.resolve()),
            "--output", str(output / "dense-report.json"),
        ]))
    commands.append(("render", [
        python, str(scripts / "render_pptx_review.py"), str(deck),
        str(output / "render"), "--node", str(runtime[RUNTIME_KEYS[0]]),
        "--runtime", str(runtime[RUNTIME_KEYS[1]]), "--profile", str(profile_path),
    ]))
    if font_bindings:
        commands.insert(0, ("font-map", [
            str(runtime[RUNTIME_KEYS[0]]), "-e", RENDERER_FONT_PROBE,
            str(runtime[RUNTIME_KEYS[1]]), str(profile_path),
        ]))
    if dense is not None:
        commands.insert(1, ("dense-scope", []))
    if operation in {"edit", "regenerate"}:
        commands.insert(0, ("chart-workbook-preservation", []))
    stages = []
    for name, command in commands:
        try:
            if name == "chart-workbook-preservation":
                preservation = preservation_gate(
                    edit_source.resolve(strict=True), deck, edit_source_sha, args.expected_sha256,
                    mode=operation, authoring_manifest=authoring_manifest,
                )
                result = subprocess.CompletedProcess(
                    command, 0 if preservation["passed"] else 1, json.dumps(preservation), "",
                )
            elif name == "dense-scope":
                dense_scope = inspect_dense_scope(deck, dense, font_bindings)
                result = subprocess.CompletedProcess(command, 0 if dense_scope["passed"] else 1,
                                                     json.dumps(dense_scope), "")
            else:
                result = subprocess.run(
                    command, capture_output=True, text=True, encoding="utf-8",
                    errors="replace", timeout=360, check=False,
                )
            stage = {
                "name": name, "exit_code": result.returncode,
                "stdout": result.stdout, "stderr": result.stderr,
            }
        except (OSError, ValueError, KeyError, TypeError, ET.ParseError, BadZipFile,
                subprocess.TimeoutExpired) as exc:
            stage = {"name": name, "exit_code": None, "error": str(exc)}
        stage["accepted"] = stage["exit_code"] == 0
        if stage["accepted"] and font_bindings and name in {"font-map", "dense", "render"}:
            try:
                if name == "font-map":
                    check_renderer_faces(json.loads(stage["stdout"]), font_bindings)
                else:
                    check_font_receipt(name, output, font_bindings, dense)
                stage["font_binding_passed"] = True
            except (OSError, ValueError, KeyError, TypeError) as exc:
                stage["accepted"] = False
                stage["font_binding_passed"] = False
                stage["font_binding_error"] = str(exc)
        stages.append(stage)
        (output / f"{name}-process.json").write_text(
            json.dumps(stage, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
        )
        if not stage["accepted"]:
            break
    if dense_scope.get("passed") and any(
        s["name"] == "dense" and s["accepted"] for s in stages
    ):
        dense_scope["completed_objects"] = dense_scope["supported_objects"]
        dense_scope["status"] = "completed_targeted_dense_checks"
    unchanged = sha256(deck) == args.expected_sha256
    if dense_scope and not unchanged:
        dense_scope["completed_objects"] = 0
    edit_source_unchanged = (operation == "review" or sha256(edit_source) == edit_source_sha)
    report = {
        "schema_version": 2,
        "operation": "REVIEW_EXISTING_PPTX",
        "pptx_sha256": args.expected_sha256,
        "source_unchanged": unchanged,
        "qa_processes_passed": unchanged and edit_source_unchanged and len(stages) == len(commands)
        and all(stage["accepted"] for stage in stages),
        "stages": [{"name": s["name"], "exit_code": s["exit_code"], "accepted": s["accepted"]}
                   for s in stages],
        "review_operation": operation,
        "edit_source_unchanged": edit_source_unchanged if operation != "review" else None,
        "chart_workbook_preservation": preservation,
        "dense_scope": dense_scope,
        "optional_native_gates": {
            "status": "unverified", "reason": "Not connected; no verified host interface supplied",
            "gates": ["native_table_arithmetic_gate.py", "native_quantitative_chart_gate.py",
                      "native_chart_title_gate.py"],
        },
        "dense_renderer_font_bindings": font_bindings,
        "renderer_face_map_verified": any(s["name"] == "font-map" and s["accepted"] for s in stages),
        "per_glyph_font_verified": False,
        "component_sha256": {p.name: sha256(p) for p in required},
        "visual_review_completed": False,
        "powerpoint_verified": False,
        "recipient_opened": False,
        "production_authorized": False,
        "scope": "Exact existing-file QA only. Separate actual host evidence is required "
        "for template choice, source analysis, current approval, visual review and delivery.",
    }
    (output / "review-receipt.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    return report


def main(argv: list[str] | None = None) -> int:
    configure_utf8_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck", type=Path)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--host-skill-dir", type=Path, required=True)
    parser.add_argument("--review-scripts", type=Path, required=True)
    parser.add_argument("--dense-contract", type=Path)
    parser.add_argument("--operation", choices=["review", "edit", "regenerate"], default="review")
    parser.add_argument("--edit-source", type=Path)
    parser.add_argument("--edit-source-sha256")
    parser.add_argument("--authoring-manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        report = review(args)
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError, BadZipFile) as exc:
        print(json.dumps({"qa_processes_passed": False, "error": str(exc)}))
        return 2
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["qa_processes_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
