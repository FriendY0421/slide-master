#!/usr/bin/env python3
"""
PPT Master - Cloud Review Adapter Safety Tests

Isolated synthetic tests of the read-only adapter. They do not make a PPTX,
contact a service, prove authentication or represent real user approval.

Usage:
    python3 cloud_review_existing_selftest.py

Dependencies:
    Existing host fontTools/jsonschema; opt-in reviewed dense source uses existing Pillow.
"""
from __future__ import annotations

import argparse
import json
import importlib.util
import os
import xml.etree.ElementTree as ET
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from unittest.mock import patch

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont, TTCollection, newTable

import cloud_review_existing as target


class CloudReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.deck = self.root / "input" / "sample.pptx"
        self.deck.parent.mkdir()
        self.deck.write_bytes(b"synthetic fixture, not a real presentation")
        self.font = self.root / "font.otf"
        self.make_font(self.font)
        self.profile = self.root / "profile.json"
        self.profile.write_text(json.dumps({
            "font_family": "Fixture",
            "font_files": [{"path": "font.otf", "sha256": target.sha256(self.font)}],
        }))
        self.host = self.root / "host"
        self.host.mkdir()
        (self.host / "container_tools").mkdir()
        self.scripts = self.root / "scripts"
        self.scripts.mkdir()
        for name in ("inspect_presentation_package_integrity.py", "inspect_presentation_layout_geometry.py"):
            (self.host / "container_tools" / name).write_text("fixture")
        for name in ("render_pptx_review.py", "render_pptx_review.mjs", "dense_pptx_quality.py"):
            (self.scripts / name).write_text("fixture")
        self.args = argparse.Namespace(
            deck=self.deck, expected_sha256=target.sha256(self.deck),
            profile=self.profile, host_skill_dir=self.host, review_scripts=self.scripts,
            dense_contract=None, output=self.root / "review",
        )
        self.runtime = dict(zip(target.RUNTIME_KEYS, [Path("/supplied/node"), Path("/supplied/modules"),
                                                     Path("/supplied/python")]))

    def make_font(self, path: Path, weight: int = 400, *, italic: bool = False,
                  width: int = 5, label: str = "fixture", korean: bool = False) -> None:
        builder = FontBuilder(1000, isTTF=True)
        glyphs = [".notdef", "space", "A"] + (["ga"] if korean else [])
        builder.setupGlyphOrder(glyphs)
        builder.setupCharacterMap({32: "space", 65: "A"} | ({0xAC00: "ga"} if korean else {}))
        builder.setupGlyf({name: TTGlyphPen(None).glyph() for name in glyphs})
        builder.setupHorizontalMetrics({name: (500, 0) for name in glyphs})
        builder.setupHorizontalHeader(ascent=800, descent=-200)
        style = "Bold" if weight == 700 else "Regular"
        if italic:
            style += " Italic"
        builder.setupNameTable({"familyName": "Fixture", "styleName": style,
                                "uniqueFontIdentifier": label, "fullName": "Fixture " + style,
                                "psName": "Fixture-" + style.replace(" ", "")})
        selection = (32 if weight == 700 else 64) | int(italic)
        builder.setupOS2(usWeightClass=weight, usWidthClass=width, fsSelection=selection,
                         sTypoAscender=800, sTypoDescender=-200, usWinAscent=800, usWinDescent=200)
        builder.setupPost(italicAngle=-12 if italic else 0)
        builder.setupMaxp()
        builder.font["head"].macStyle = (1 if weight == 700 else 0) | (2 if italic else 0)
        builder.save(path)

    def bindings(self, dense: dict | None = None) -> dict:
        return target.bind_dense_fonts(dense or self.dense_fixture(), self.root / "dense.json",
                                       target.validate_profile(self.profile), self.profile)

    def two_faces(self) -> dict:
        bold = self.root / "bold.otf"
        self.make_font(bold, 700)
        profile = json.loads(self.profile.read_text())
        profile["font_files"].append({"path": bold.name, "sha256": target.sha256(bold)})
        self.profile.write_text(json.dumps(profile))
        dense = self.dense_fixture()
        dense["font_files"]["Fixture"]["bold"] = profile["font_files"][-1].copy()
        return dense

    def skia_records(self, bindings: dict) -> list:
        return [{key: face[key] for key in ("family", "weight", "style", "width", "sha256")}
                | {"file": face["renderer_path"]} for face in bindings.values()]

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_missing_runtime_rejected(self) -> None:
        with self.assertRaises(ValueError):
            target.supplied_runtime({})

    def test_relative_runtime_rejected(self) -> None:
        with self.assertRaises(ValueError):
            target.supplied_runtime({target.RUNTIME_KEYS[0]: "./node"})

    def test_profile_hash_mismatch_rejected(self) -> None:
        self.font.write_bytes(b"changed")
        with self.assertRaises(ValueError):
            target.validate_profile(self.profile)

    def test_profile_nonobject_rejected(self) -> None:
        self.profile.write_text("[]")
        with self.assertRaises(ValueError):
            target.validate_profile(self.profile)

    def test_wrong_final_file_rejected_before_execution(self) -> None:
        self.args.expected_sha256 = "0" * 64
        with patch.object(target.subprocess, "run") as run, self.assertRaises(ValueError):
            target.review(self.args)
        run.assert_not_called()

    def test_existing_receipts_preserved(self) -> None:
        self.args.output.mkdir()
        marker = self.args.output / "keep.txt"
        marker.write_text("preserve")
        with patch.object(target, "supplied_runtime", return_value=self.runtime):
            with self.assertRaises(FileExistsError):
                target.review(self.args)
        self.assertEqual(marker.read_text(), "preserve")

    def test_source_directory_cannot_be_output(self) -> None:
        self.args.output = self.deck.parent
        with patch.object(target, "supplied_runtime", return_value=self.runtime):
            with self.assertRaises(ValueError):
                target.review(self.args)

    def test_structure_only_cannot_satisfy_final_qa(self) -> None:
        contract = self.root / "dense.json"
        contract.write_text('{"text_metrics":"structure_only","font_family":"Fixture"}')
        self.args.dense_contract = contract
        with patch.object(target, "supplied_runtime", return_value=self.runtime):
            with self.assertRaises(ValueError):
                target.review(self.args)

    def test_font_contract_mismatch_rejected(self) -> None:
        contract = self.root / "dense.json"
        contract.write_text('{"text_metrics":"actual_font","font_family":"Different"}')
        self.args.dense_contract = contract
        with patch.object(target, "supplied_runtime", return_value=self.runtime):
            with self.assertRaises(ValueError):
                target.review(self.args)

    def dense_fixture(self, path: str = "font.otf", digest: str | None = None) -> dict:
        return {
            "text_metrics": "actual_font", "font_family": "Fixture",
            "font_files": {"Fixture": {"regular": {
                "path": path, "sha256": digest or target.sha256(self.font),
            }}},
            "slides": [{"objects": {"label": {"kind": "text"}}}],
        }

    def test_same_family_different_font_bytes_rejected_before_execution(self) -> None:
        other = self.root / "different-version.otf"
        self.make_font(other, label="different bytes, same family and face")
        contract = self.root / "dense.json"
        contract.write_text(json.dumps(self.dense_fixture(other.name, target.sha256(other))))
        self.args.dense_contract = contract
        with patch.object(target, "supplied_runtime", return_value=self.runtime):
            with patch.object(target.subprocess, "run") as run, self.assertRaisesRegex(
                ValueError, "role-specific font bytes/metadata differ",
            ):
                target.review(self.args)
        run.assert_not_called()
        self.assertFalse(self.args.output.exists())

    def test_dense_font_content_must_match_its_declared_hash(self) -> None:
        dense = self.dense_fixture()
        self.font.write_bytes(b"changed after the declared measurement profile")
        with self.assertRaisesRegex(ValueError, "Dense regular font bytes changed"):
            target.bind_dense_fonts(dense, self.root / "dense.json",
                                    json.loads(self.profile.read_text()), self.profile)

    def test_identical_font_bytes_at_another_path_are_compatible(self) -> None:
        copy = self.root / "font-copy.otf"
        copy.write_bytes(self.font.read_bytes())
        result = target.bind_dense_fonts(
            self.dense_fixture(copy.name), self.root / "dense.json",
            target.validate_profile(self.profile), self.profile,
        )
        self.assertEqual(result["regular"]["sha256"], target.sha256(self.font))

    def test_dense_actual_measurement_hash_mismatch_rejected(self) -> None:
        self.args.output.mkdir()
        (self.args.output / "dense-report.json").write_text(json.dumps({
            "text_metrics_mode": "actual_font", "font_files_sha256": {"measured.otf": "0" * 64},
        }))
        with self.assertRaisesRegex(ValueError, "Measured dense fonts differ"):
            target.check_font_receipt(
                "dense", self.args.output, self.bindings(),
                self.dense_fixture(),
            )

    def test_missing_actual_dense_font_for_text_rejected(self) -> None:
        self.args.output.mkdir()
        (self.args.output / "dense-report.json").write_text(json.dumps({
            "text_metrics_mode": "actual_font", "font_files_sha256": {},
        }))
        with self.assertRaisesRegex(ValueError, "no measured font files"):
            target.check_font_receipt(
                "dense", self.args.output, self.bindings(),
                self.dense_fixture(),
            )

    def test_actual_renderer_hash_mismatch_rejected(self) -> None:
        (self.args.output / "render").mkdir(parents=True)
        (self.args.output / "render/render-manifest.json").write_text(json.dumps({
            "registered_fonts": {"renderer.otf": "0" * 64},
        }))
        with self.assertRaisesRegex(ValueError, "Actual renderer font bytes/paths differ"):
            target.check_font_receipt(
                "render", self.args.output, self.bindings(),
                self.dense_fixture(),
            )

    def test_matching_actual_font_receipts_accepted(self) -> None:
        (self.args.output / "render").mkdir(parents=True)
        digest = target.sha256(self.font)
        (self.args.output / "dense-report.json").write_text(json.dumps({
            "text_metrics_mode": "actual_font", "font_files_sha256": {str(self.font): digest},
        }))
        (self.args.output / "render/render-manifest.json").write_text(json.dumps({
            "registered_fonts": {str(self.font): digest},
        }))
        for name in ("dense", "render"):
            target.check_font_receipt(
                name, self.args.output, self.bindings(), self.dense_fixture(),
            )

    def test_correct_two_face_mapping_and_skia_metadata_pass(self) -> None:
        bound = self.bindings(self.two_faces())
        self.assertEqual({role: spec["weight"] for role, spec in bound.items()},
                         {"regular": 400, "bold": 700})
        target.check_renderer_faces(self.skia_records(bound), bound)

    def test_swapped_regular_bold_rejected_despite_identical_sha_set(self) -> None:
        dense = self.two_faces()
        faces = dense["font_files"]["Fixture"]
        before = {spec["sha256"] for spec in faces.values()}
        faces["regular"], faces["bold"] = faces["bold"], faces["regular"]
        self.assertEqual(before, {spec["sha256"] for spec in faces.values()})
        contract = self.root / "dense.json"
        contract.write_text(json.dumps(dense))
        self.args.dense_contract = contract
        with patch.object(target, "supplied_runtime", return_value=self.runtime):
            with patch.object(target.subprocess, "run") as run, self.assertRaisesRegex(
                ValueError, "role/family disagrees with actual font metadata",
            ):
                target.review(self.args)
        run.assert_not_called()
        self.assertFalse(self.args.output.exists())

    def test_file_name_does_not_determine_role(self) -> None:
        dense = self.two_faces()
        misleading = self.root / "Bold-by-name-only.otf"
        misleading.write_bytes(self.font.read_bytes())
        dense["font_files"]["Fixture"]["regular"]["path"] = misleading.name
        self.assertEqual(self.bindings(dense)["regular"]["weight"], 400)

    def test_regular_file_cannot_measure_bold_role(self) -> None:
        dense = self.two_faces()
        dense["font_files"]["Fixture"]["bold"] = dense["font_files"]["Fixture"]["regular"].copy()
        with self.assertRaisesRegex(ValueError, "role/family disagrees"):
            self.bindings(dense)

    def test_duplicate_renderer_face_is_ambiguous(self) -> None:
        profile = json.loads(self.profile.read_text())
        profile["font_files"].append(profile["font_files"][0].copy())
        self.profile.write_text(json.dumps(profile))
        with self.assertRaisesRegex(ValueError, "mapping is ambiguous"):
            self.bindings()

    def test_missing_renderer_face_rejected(self) -> None:
        dense = self.two_faces()
        profile = json.loads(self.profile.read_text())
        profile["font_files"].pop()
        self.profile.write_text(json.dumps(profile))
        with self.assertRaisesRegex(ValueError, "face roles differ"):
            self.bindings(dense)

    def test_skia_role_swap_with_same_hash_set_rejected(self) -> None:
        bound = self.bindings(self.two_faces())
        records = self.skia_records(bound)
        records[0]["weight"], records[1]["weight"] = records[1]["weight"], records[0]["weight"]
        with self.assertRaisesRegex(ValueError, "role/metadata differs"):
            target.check_renderer_faces(records, bound)

    def test_skia_italic_mapping_rejected(self) -> None:
        bound = self.bindings(self.two_faces())
        records = self.skia_records(bound)
        records[0]["style"] = "italic"
        with self.assertRaisesRegex(ValueError, "role/metadata differs"):
            target.check_renderer_faces(records, bound)

    def test_skia_duplicate_role_rejected(self) -> None:
        bound = self.bindings(self.two_faces())
        records = self.skia_records(bound)
        with self.assertRaisesRegex(ValueError, "unsupported or ambiguous"):
            target.check_renderer_faces([records[0], records[0]], bound)

    def test_skia_missing_record_rejected(self) -> None:
        bound = self.bindings(self.two_faces())
        with self.assertRaisesRegex(ValueError, "each unique bound face"):
            target.check_renderer_faces(self.skia_records(bound)[:1], bound)

    def test_nonzero_collection_index_rejected(self) -> None:
        dense = self.dense_fixture()
        dense["font_files"]["Fixture"]["regular"]["index"] = 1
        with self.assertRaisesRegex(ValueError, "collection indexes"):
            self.bindings(dense)

    def test_actual_italic_font_metadata_rejected(self) -> None:
        italic = self.root / "italic.otf"
        self.make_font(italic, italic=True)
        with self.assertRaisesRegex(ValueError, "Italic/oblique"):
            target.font_metadata(italic)

    def test_actual_condensed_font_metadata_rejected(self) -> None:
        condensed = self.root / "condensed.otf"
        self.make_font(condensed, width=3)
        with self.assertRaisesRegex(ValueError, "normal-width"):
            target.font_metadata(condensed)

    def test_inconsistent_bold_flag_rejected(self) -> None:
        font = TTFont(self.font)
        font["head"].macStyle = 1
        font.save(self.font)
        font.close()
        with self.assertRaisesRegex(ValueError, "bold style flags disagree"):
            target.font_metadata(self.font)

    def test_numeric_weight_subfamily_with_regular_style_flags(self) -> None:
        numeric = self.root / "numeric.otf"
        self.make_font(numeric, 700)
        with TTFont(numeric) as font:
            font["OS/2"].fsSelection = 64
            font["head"].macStyle = 0
            for record in font["name"].names:
                if record.nameID in {2, 17}:
                    record.string = "700".encode(record.getEncoding())
            font.save(numeric)
        self.assertEqual(target.font_metadata(numeric)["role"], "bold")
        self.assertEqual(target.font_metadata(numeric)["subfamily"], "700")

        for label, selection, mac_style in [
            ("Bold", 64, 0), ("400", 64, 0), ("700", 32, 0),
            ("700", 64, 1), ("700", 0, 0),
        ]:
            with self.subTest(label=label, selection=selection, mac_style=mac_style):
                with TTFont(numeric) as font:
                    font["OS/2"].fsSelection = selection
                    font["head"].macStyle = mac_style
                    for record in font["name"].names:
                        if record.nameID in {2, 17}:
                            record.string = label.encode(record.getEncoding())
                    font.save(numeric)
                with self.assertRaises(ValueError):
                    target.font_metadata(numeric)

    def test_variable_font_rejected(self) -> None:
        font = TTFont(self.font)
        font["fvar"] = newTable("fvar")
        font["fvar"].axes = []
        font["fvar"].instances = []
        font.save(self.font)
        font.close()
        with self.assertRaisesRegex(ValueError, "Variable fonts"):
            target.font_metadata(self.font)

    def test_font_collection_rejected(self) -> None:
        collection = TTCollection()
        collection.fonts = [TTFont(self.font)]
        path = self.root / "collection.ttc"
        collection.save(path)
        collection.close()
        with self.assertRaisesRegex(ValueError, "single-face"):
            target.font_metadata(path)

    def test_explicit_italic_drawingml_rejected(self) -> None:
        with ZipFile(self.deck, "w") as package:
            package.writestr("ppt/slides/slide1.xml", '<a:rPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" i="1"/>')
        with self.assertRaisesRegex(ValueError, "Italic DrawingML"):
            target.check_dense_style_scope(self.deck, self.dense_fixture())

    def test_inherited_italic_drawingml_rejected(self) -> None:
        with ZipFile(self.deck, "w") as package:
            package.writestr("ppt/slideMasters/slideMaster1.xml", '<a:defRPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" i="true"/>')
        with self.assertRaisesRegex(ValueError, "Italic DrawingML"):
            target.check_dense_style_scope(self.deck, self.dense_fixture())

    def test_boolean_true_bold_encoding_rejected(self) -> None:
        with ZipFile(self.deck, "w") as package:
            package.writestr("ppt/slides/slide1.xml", '<a:rPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" b="true"/>')
        with self.assertRaisesRegex(ValueError, "Unsupported bold encoding"):
            target.check_dense_style_scope(self.deck, self.dense_fixture())

    def test_normal_drawingml_style_scope_passes(self) -> None:
        with ZipFile(self.deck, "w") as package:
            package.writestr("ppt/slides/slide1.xml", '<a:rPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" b="1" i="0"/>')
        target.check_dense_style_scope(self.deck, self.dense_fixture())

    def style_fixture(self, *, defaults: str = "", run_attrs: str = "",
                      placeholder: bool = False, extra_xml: dict | None = None) -> dict:
        ns = 'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
        ph = '<p:ph/>' if placeholder else ''
        xml = f'<p:sld {ns}><p:cSld><p:spTree><p:sp><p:nvSpPr><p:cNvPr name="label"/><p:nvPr>{ph}</p:nvPr></p:nvSpPr><p:txBody><a:p><a:pPr>{defaults}</a:pPr><a:r><a:rPr {run_attrs}/><a:t>A</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld></p:sld>'
        with ZipFile(self.deck, "w") as package:
            package.writestr("ppt/slides/slide1.xml", xml)
            for name, contents in (extra_xml or {}).items():
                package.writestr(name, contents)
        return self.dense_fixture()

    def test_inherited_paragraph_bold_with_missing_run_flag_rejected(self) -> None:
        dense = self.style_fixture(defaults='<a:defRPr b="1"/>')
        with self.assertRaisesRegex(ValueError, "Inherited bold"):
            target.check_dense_style_scope(self.deck, dense)

    def test_explicit_regular_overrides_paragraph_bold(self) -> None:
        dense = self.style_fixture(defaults='<a:defRPr b="1"/>', run_attrs='b="0"')
        target.check_dense_style_scope(self.deck, dense)

    def test_placeholder_omitted_bold_flag_requires_explicit_role(self) -> None:
        dense = self.style_fixture(placeholder=True)
        with self.assertRaisesRegex(ValueError, "Inherited bold"):
            target.check_dense_style_scope(self.deck, dense)

    def test_plain_text_without_bold_defaults_accepts_omitted_flag(self) -> None:
        dense = self.style_fixture()
        target.check_dense_style_scope(self.deck, dense)

    def test_master_other_style_bold_rejected_for_omitted_flag(self) -> None:
        dense = self.style_fixture(extra_xml={"ppt/slideMasters/slideMaster1.xml":
            '<p:sldMaster xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><p:txStyles><p:otherStyle><a:lvl1pPr><a:defRPr b="1"/></a:lvl1pPr></p:otherStyle></p:txStyles></p:sldMaster>'})
        with self.assertRaisesRegex(ValueError, "Inherited bold"):
            target.check_dense_style_scope(self.deck, dense)

    def test_font_map_mismatch_stops_before_package_and_render(self) -> None:
        dense = self.two_faces()
        contract = self.root / "dense.json"
        contract.write_text(json.dumps(dense))
        self.args.dense_contract = contract
        with ZipFile(self.deck, "w") as package:
            package.writestr("ppt/slides/slide1.xml", '<a:rPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" b="1"/>')
        self.args.expected_sha256 = target.sha256(self.deck)
        wrong_receipt = target.subprocess.CompletedProcess([], 0, "[]", "")
        with patch.object(target, "supplied_runtime", return_value=self.runtime):
            with patch.object(target.subprocess, "run", return_value=wrong_receipt) as run:
                result = target.review(self.args)
        self.assertEqual(run.call_count, 1)
        self.assertEqual(result["stages"], [{"name": "font-map", "exit_code": 0, "accepted": False}])
        self.assertFalse(result["qa_processes_passed"])
        self.assertFalse(result["renderer_face_map_verified"])

    def test_failure_stops_later_stages(self) -> None:
        failure = target.subprocess.CompletedProcess([], 7, "", "fixture failure")
        with patch.object(target, "supplied_runtime", return_value=self.runtime):
            with patch.object(target.subprocess, "run", return_value=failure) as run:
                result = target.review(self.args)
        self.assertFalse(result["qa_processes_passed"])
        self.assertEqual(run.call_count, 1)
        self.assertFalse(result["production_authorized"])

    def test_success_never_claims_visual_review_or_approval(self) -> None:
        success = target.subprocess.CompletedProcess([], 0, "fixture", "")
        with patch.object(target, "supplied_runtime", return_value=self.runtime):
            with patch.object(target.subprocess, "run", return_value=success):
                result = target.review(self.args)
        self.assertTrue(result["qa_processes_passed"])
        for key in ("production_authorized", "visual_review_completed", "powerpoint_verified",
                    "recipient_opened"):
            self.assertFalse(result[key])

    def test_input_change_after_child_invalidates_receipt(self) -> None:
        def change(*args, **kwargs):
            self.deck.write_bytes(b"changed")
            return target.subprocess.CompletedProcess([], 0, "", "")
        with patch.object(target, "supplied_runtime", return_value=self.runtime):
            with patch.object(target.subprocess, "run", side_effect=change):
                result = target.review(self.args)
        self.assertFalse(result["source_unchanged"])
        self.assertFalse(result["qa_processes_passed"])


    def scope_fixture(self, *, text: str = "A가 A가", latin: str = "Fixture",
                      ea: str = "Fixture", order: tuple = (1,), bold: bool = False,
                      extra: str = "", kind: str = "text") -> tuple[dict, dict]:
        self.make_font(self.font, korean=True)
        profile = json.loads(self.profile.read_text())
        profile["font_files"][0]["sha256"] = target.sha256(self.font)
        self.profile.write_text(json.dumps(profile))
        dense = self.two_faces() if bold else self.dense_fixture()
        slots = (f'<a:latin typeface="{latin}"/>' if latin else '')
        slots += (f'<a:ea typeface="{ea}"/>' if ea else '')
        rpr = f'<a:rPr b="{int(bold)}" sz="1200">{slots}</a:rPr>'
        run = f'<a:r>{rpr}<a:t>{text}</a:t></a:r>'
        body = f'<a:bodyPr/><a:p>{run}</a:p>'
        if kind == "table":
            content = f'<a:tbl><a:tr><a:tc><a:txBody>{body}</a:txBody></a:tc></a:tr></a:tbl>'
            shape = ('<p:graphicFrame><p:nvGraphicFramePr><p:cNvPr name="label"/>'
                     '</p:nvGraphicFramePr><a:graphic><a:graphicData>'
                     f'{content}</a:graphicData></a:graphic></p:graphicFrame>')
        else:
            shape = f'<p:sp><p:nvSpPr><p:cNvPr name="label"/></p:nvSpPr><p:txBody>{body}</p:txBody></p:sp>'
        ns = ('xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
              'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
              'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"')
        entries = ''.join(f'<p:sldId id="{255+n}" r:id="r{part}"/>' for n, part in enumerate(order))
        rels = ''.join(
            f'<Relationship Id="r{part}" Type="http://schemas.openxmlformats.org/'
            'officeDocument/2006/relationships/slide" '
            f'Target="slides/slide{part}.xml"/>' for part in order)
        with ZipFile(self.deck, "w") as package:
            package.writestr("ppt/presentation.xml",
                             f'<p:presentation {ns}><p:sldIdLst>{entries}</p:sldIdLst></p:presentation>')
            package.writestr("ppt/_rels/presentation.xml.rels",
                             '<Relationships xmlns="http://schemas.openxmlformats.org/'
                             f'package/2006/relationships">{rels}</Relationships>')
            for part in set(order):
                package.writestr(f"ppt/slides/slide{part}.xml",
                                 f'<p:sld {ns}><p:cSld><p:spTree>{shape}{extra}</p:spTree></p:cSld></p:sld>')
        dense["slides"] = [{"slide": 1, "objects": {"label": {"kind": kind}}}]
        return dense, self.bindings(dense)

    def scope_result(self, **kwargs) -> dict:
        dense, bound = self.scope_fixture(**kwargs)
        return target.inspect_dense_scope(self.deck, dense, bound)

    def test_matching_explicit_korean_latin_slots_and_cmap_pass(self) -> None:
        result = self.scope_result()
        self.assertTrue(result["passed"])
        self.assertEqual(result["supported_objects"], 1)
        self.assertEqual(result["completed_objects"], 0)

    def test_mixed_run_different_latin_slot_is_unsupported(self) -> None:
        result = self.scope_result(latin="Other")
        self.assertFalse(result["passed"])
        self.assertIn("slot latin", str(result))

    def test_different_ea_slot_is_unsupported(self) -> None:
        self.assertFalse(self.scope_result(ea="Other")["passed"])

    def test_missing_latin_slot_is_unresolved(self) -> None:
        self.assertFalse(self.scope_result(latin="")["passed"])

    def test_missing_ea_slot_is_unresolved(self) -> None:
        self.assertFalse(self.scope_result(ea="")["passed"])

    def test_theme_slot_is_unresolved(self) -> None:
        self.assertFalse(self.scope_result(latin="+mn-lt")["passed"])

    def test_actual_cmap_missing_korean_codepoint_is_unsupported(self) -> None:
        result = self.scope_result(text="A나")
        self.assertFalse(result["passed"])
        self.assertIn("U+B098", str(result))

    def test_bold_cmap_is_checked_separately(self) -> None:
        result = self.scope_result(bold=True)
        self.assertFalse(result["passed"])
        self.assertIn("U+AC00", str(result))

    def test_native_table_slots_are_also_checked(self) -> None:
        self.assertTrue(self.scope_result(kind="table")["passed"])
        self.assertFalse(self.scope_result(kind="table", latin="Other")["passed"])

    def test_reordered_slides_are_rejected_without_rewriting(self) -> None:
        dense, bound = self.scope_fixture(order=(2, 1))
        before = target.sha256(self.deck)
        result = target.inspect_dense_scope(self.deck, dense, bound)
        self.assertFalse(result["passed"])
        self.assertEqual(result["logical_slide_parts"][0], "ppt/slides/slide2.xml")
        self.assertEqual(before, target.sha256(self.deck))

    def test_normal_two_slide_order_passes_with_uninspected_count(self) -> None:
        result = self.scope_result(order=(1, 2))
        self.assertTrue(result["passed"])
        self.assertEqual(result["uninspected_objects"], 1)

    def test_uncontracted_objects_are_not_reported_complete(self) -> None:
        result = self.scope_result(extra='<p:pic><p:nvPicPr><p:cNvPr name="photo"/></p:nvPicPr></p:pic>')
        self.assertEqual((result["completed_objects"], result["unsupported_objects"],
                          result["uninspected_objects"]), (0, 0, 1))

    def test_unknown_target_kind_is_unsupported(self) -> None:
        self.assertFalse(self.scope_result(kind="chart")["passed"])

    def test_missing_target_is_unsupported_not_complete(self) -> None:
        dense, bound = self.scope_fixture()
        dense["slides"][0]["objects"] = {"absent": {"kind": "text"}}
        result = target.inspect_dense_scope(self.deck, dense, bound)
        self.assertEqual(result["unsupported_objects"], 1)
        self.assertEqual(result["uninspected_objects"], 1)

    def test_duplicate_slide_target_rejected(self) -> None:
        dense, bound = self.scope_fixture()
        dense["slides"] *= 2
        with self.assertRaisesRegex(ValueError, "duplicate"):
            target.inspect_dense_scope(self.deck, dense, bound)

    def test_font_changed_after_binding_rejected_by_cmap_guard(self) -> None:
        dense, bound = self.scope_fixture()
        self.font.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "bytes changed"):
            target.inspect_dense_scope(self.deck, dense, bound)

    def test_scope_failure_stops_dense_and_render_and_preserves_counts(self) -> None:
        dense, bound = self.scope_fixture(latin="Other")
        contract = self.root / "dense.json"
        contract.write_text(json.dumps(dense))
        self.args.dense_contract = contract
        self.args.expected_sha256 = target.sha256(self.deck)
        mapped = target.subprocess.CompletedProcess([], 0, json.dumps(self.skia_records(bound)), "")
        with patch.object(target, "supplied_runtime", return_value=self.runtime), patch.object(
            target.subprocess, "run", return_value=mapped
        ) as run:
            result = target.review(self.args)
        self.assertEqual(run.call_count, 1)
        self.assertFalse(result["qa_processes_passed"])
        self.assertEqual(result["dense_scope"]["unsupported_objects"], 1)
        self.assertEqual(result["dense_scope"]["completed_objects"], 0)
        self.assertTrue((self.args.output / "dense-scope-process.json").is_file())

    def test_existing_dense_mixed_korean_english_wrap_boundaries(self) -> None:
        # Opt-in read-only regression against the already-reviewed dense source;
        # absence is a skip, never a substitute estimator or installed package.
        path = os.environ.get("SLIDE_MASTER_REVIEWED_DENSE_SOURCE")
        if not path:
            self.skipTest("Existing reviewed dense source not supplied")
        self.assertEqual(target.sha256(Path(path)),
                         "cfe39dd481c4eba232c2c41bd7ceb2a92fcdc7c1d903ac5a8e2ca6dfc92a00f3")
        spec = importlib.util.spec_from_file_location("reviewed_dense", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        dense, _ = self.scope_fixture(text="가A 가A")
        dense["slides"] = []
        ns = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
        props = '<a:rPr sz="1200"><a:latin typeface="Fixture"/><a:ea typeface="Fixture"/></a:rPr>'
        body = ET.fromstring(f'<a:txBody {ns}><a:bodyPr/><a:p><a:r>{props}<a:t>가A 가A</a:t></a:r></a:p></a:txBody>')
        results = []
        for width in (30, 29, 12, 11):
            inspector = module.DenseInspector(dense, self.root)
            inspector.text(body, width, 100, "mixed", {}, None)
            results.append(inspector.measurements[-1]["wrapped_lines"])
        self.assertEqual(results, [1, 2, 2, 4])
        # Explicit line breaks and no-wrap retain fixed 12pt text.
        body = ET.fromstring(f'<a:txBody {ns}><a:bodyPr/><a:p><a:r>{props}<a:t>가A</a:t></a:r>'
                             f'<a:br/><a:r>{props}<a:t>가A</a:t></a:r></a:p></a:txBody>')
        inspector = module.DenseInspector(dense, self.root)
        inspector.text(body, 30, 100, "break", {}, None)
        self.assertEqual(inspector.measurements[-1]["wrapped_lines"], 2)
        body.find("a:bodyPr", module.NS).set("wrap", "none")
        inspector = module.DenseInspector(dense, self.root)
        inspector.text(body, 10, 100, "nowrap", {}, None)
        self.assertTrue(any(error["kind"] == "TEXT_WIDTH" for error in inspector.errors))


    def test_tab_stop_layout_is_unsupported(self) -> None:
        self.assertFalse(self.scope_result(text="A\t가")["passed"])

    def test_cmap_notdef_mapping_is_missing_coverage(self) -> None:
        dense, bound = self.scope_fixture()
        font = TTFont(self.font)
        for cmap in font["cmap"].tables:
            if cmap.isUnicode():
                cmap.cmap[0xB098] = ".notdef"
        font.save(self.font)
        font.close()
        # Refresh the verified binding; reject the glyph, not a stale hash.
        bound["regular"]["sha256"] = target.sha256(self.font)
        with ZipFile(self.deck) as package:
            parts = {name: package.read(name) for name in package.namelist()}
        parts["ppt/slides/slide1.xml"] = parts["ppt/slides/slide1.xml"].replace("가".encode(), "나".encode())
        with ZipFile(self.deck, "w") as package:
            for name, value in parts.items():
                package.writestr(name, value)
        self.assertFalse(target.inspect_dense_scope(self.deck, dense, bound)["passed"])

    def test_scope_positive_adapter_counts_complete_only_after_dense_receipt(self) -> None:
        dense, bound = self.scope_fixture()
        contract = self.root / "dense.json"
        contract.write_text(json.dumps(dense))
        self.args.dense_contract = contract
        self.args.expected_sha256 = target.sha256(self.deck)
        def child(command, **kwargs):
            if "-e" in command:
                stdout = json.dumps(self.skia_records(bound))
            else:
                stdout = "fixture"
                if any(str(arg).endswith("dense_pptx_quality.py") for arg in command):
                    (self.args.output / "dense-report.json").write_text(json.dumps({
                        "text_metrics_mode": "actual_font",
                        "font_files_sha256": {str(self.font): target.sha256(self.font)},
                    }))
                if any(str(arg).endswith("render_pptx_review.py") for arg in command):
                    (self.args.output / "render").mkdir()
                    (self.args.output / "render/render-manifest.json").write_text(json.dumps({
                        "registered_fonts": {str(self.font): target.sha256(self.font)},
                    }))
            return target.subprocess.CompletedProcess(command, 0, stdout, "")
        with patch.object(target, "supplied_runtime", return_value=self.runtime), patch.object(
            target.subprocess, "run", side_effect=child
        ):
            result = target.review(self.args)
        self.assertTrue(result["qa_processes_passed"])
        self.assertEqual(result["dense_scope"]["completed_objects"], 1)
        self.assertFalse(result["per_glyph_font_verified"])
        self.assertFalse(result["powerpoint_verified"])


    def test_edit_review_requires_bound_pre_edit_source(self) -> None:
        self.args.operation = "edit"
        with patch.object(target, "supplied_runtime", return_value=self.runtime), patch.object(
            target.subprocess, "run"
        ) as run, self.assertRaisesRegex(ValueError, "pre-edit source"):
            target.review(self.args)
        run.assert_not_called()

    def test_preservation_failure_stops_all_external_checks(self) -> None:
        self.args.operation = "edit"
        self.args.edit_source = self.deck
        self.args.edit_source_sha256 = self.args.expected_sha256
        blocked = {"passed": False, "delivery_blocked": True, "regeneration_eligible": True}
        with patch.object(target, "supplied_runtime", return_value=self.runtime), patch.object(
            target, "preservation_gate", return_value=blocked
        ), patch.object(target.subprocess, "run") as run:
            report = target.review(self.args)
        run.assert_not_called()
        self.assertFalse(report["qa_processes_passed"])
        self.assertEqual(report["stages"], [{"name": "chart-workbook-preservation",
                                           "exit_code": 1, "accepted": False}])
        self.assertTrue(report["chart_workbook_preservation"]["regeneration_eligible"])
        self.assertFalse(report["production_authorized"])

    def test_review_mode_cannot_ignore_edit_source_fields(self) -> None:
        self.args.operation = "review"
        self.args.edit_source = self.deck
        with patch.object(target, "supplied_runtime", return_value=self.runtime), self.assertRaisesRegex(
            ValueError, "Explicit edit/regenerate"
        ):
            target.review(self.args)


    def test_pre_edit_source_change_invalidates_successful_review(self) -> None:
        original = self.root / "original.pptx"
        original.write_bytes(self.deck.read_bytes())
        self.args.operation = "edit"
        self.args.edit_source = original
        self.args.edit_source_sha256 = target.sha256(original)
        def child(*args, **kwargs):
            original.write_bytes(b"changed pre-edit source")
            return target.subprocess.CompletedProcess([], 0, "fixture", "")
        with patch.object(target, "supplied_runtime", return_value=self.runtime), patch.object(
            target, "preservation_gate", return_value={"passed": True}
        ), patch.object(target.subprocess, "run", side_effect=child):
            report = target.review(self.args)
        self.assertFalse(report["qa_processes_passed"])
        self.assertFalse(report["edit_source_unchanged"])


class GateSchemaTests(unittest.TestCase):
    """Ten reproducible boundary checks; isolated evidence is never approval."""

    def setUp(self) -> None:
        from jsonschema import Draft202012Validator
        root = Path(__file__).resolve().parents[4]
        schema = json.loads((root / "docs/ppt-project/PHOTO_ANALYSIS_REVIEW_SCHEMA.json").read_text())
        Draft202012Validator.check_schema(schema)
        self.validator = Draft202012Validator(schema)
        self.data = {
            "schema_version": "1.0", "source": {
                "provenance": "isolated_test_fixture", "sha256": "a" * 64,
                "pixel_size": [100, 100], "actual_pixels_reviewed": True,
            }, "page_count": 1, "items": [{
                "id": "fixture", "kind": "text", "page": 1,
                "position": [0, 0, 1, 1], "confidence": "unknown",
                "basis": "isolated schema probe", "editable_plan": "native_text",
            }], "uncertainties": [], "missing_originals": [],
            "approval_required": True, "generation_allowed": False,
        }

    def test_valid_isolated_analysis_schema(self) -> None:
        self.assertFalse(list(self.validator.iter_errors(self.data)))

    def test_analysis_never_grants_generation(self) -> None:
        self.data["generation_allowed"] = True
        self.assertTrue(list(self.validator.iter_errors(self.data)))

    def test_analysis_cannot_skip_approval(self) -> None:
        self.data["approval_required"] = False
        self.assertTrue(list(self.validator.iter_errors(self.data)))

    def test_analysis_requires_actual_pixels(self) -> None:
        self.data["source"]["actual_pixels_reviewed"] = False
        self.assertTrue(list(self.validator.iter_errors(self.data)))

    def test_analysis_rejects_unverified_digest(self) -> None:
        self.data["source"]["sha256"] = "filename-only"
        self.assertTrue(list(self.validator.iter_errors(self.data)))

    def test_visual_estimate_cannot_claim_exact_font(self) -> None:
        self.data["items"][0]["font"] = {
            "family_candidates": ["Fixture"], "size_pt_range": [10, 12],
            "basis": "visual_estimate", "exact_identification_verified": True,
            "license_status": "pending",
        }
        self.assertTrue(list(self.validator.iter_errors(self.data)))

    def test_unknown_analysis_fields_rejected(self) -> None:
        self.data["runtime_enabled"] = True
        self.assertTrue(list(self.validator.iter_errors(self.data)))

    def test_missing_picker_evidence_rejected(self) -> None:
        from picker_surface_gate import validate_picker_evidence
        self.assertTrue(validate_picker_evidence({}))

    def test_missing_template_selection_rejected(self) -> None:
        from template_gate import validate_selection_record
        self.assertTrue(validate_selection_record({}))

    def test_missing_storyline_approval_rejected(self) -> None:
        from storyline_gate import validate_approval
        self.assertTrue(validate_approval({}))


if __name__ == "__main__":
    from console_encoding import configure_utf8_stdio
    configure_utf8_stdio()
    unittest.main(verbosity=2)
