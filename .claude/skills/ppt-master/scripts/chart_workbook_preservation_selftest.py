#!/usr/bin/env python3
"""PPT Master - Synthetic chart preservation regressions.

Usage: python3 chart_workbook_preservation_selftest.py
Examples: See CLOUD_REVIEW_FONT_ORDER_20261020.md for actual fixture evidence.
Dependencies: Standard library only; no network, fonts or renderer.
"""
from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

import chart_workbook_preservation as gate


class PreservationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "source.pptx"
        self.candidate = self.root / "candidate.pptx"
        self.package(self.source)
        self.package(self.candidate)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def package(self, path: Path, *, workbook: bool = True, external: bool = False,
                missing_relation: bool = False, chart: bool = True, formula: str = "SUM(A1:A2)",
                value: int = 12, data_node: bool = True) -> None:
        rel = 'http://schemas.openxmlformats.org/package/2006/relationships'
        office = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
        drawing = 'http://schemas.openxmlformats.org/drawingml/2006/chart'
        with ZipFile(path, 'w') as z:
            z.writestr('ppt/presentation.xml',
                       f'<p:presentation xmlns:p="{gate.NS["p"]}" xmlns:r="{office}">'
                       '<p:sldIdLst><p:sldId r:id="s"/></p:sldIdLst></p:presentation>')
            z.writestr('ppt/_rels/presentation.xml.rels',
                       f'<Relationships xmlns="{rel}"><Relationship Id="s" Type="{office}/slide" '
                       'Target="slides/slide9.xml"/></Relationships>')
            node = '<c:chart r:id="c"/>' if chart else ''
            z.writestr('ppt/slides/slide9.xml',
                       f'<p:sld xmlns:p="{gate.NS["p"]}" xmlns:c="{drawing}" xmlns:r="{office}">'
                       f'{node}</p:sld>')
            z.writestr('ppt/slides/_rels/slide9.xml.rels',
                       f'<Relationships xmlns="{rel}"><Relationship Id="c" Type="{office}/chart" '
                       'Target="../charts/chart7.xml"/></Relationships>')
            data = '<c:externalData r:id="w"/>' if data_node else ''
            z.writestr('ppt/charts/chart7.xml',
                       f'<c:chartSpace xmlns:c="{drawing}" xmlns:r="{office}">'
                       f'<c:chart><c:plotArea><c:barChart/></c:plotArea></c:chart>{data}</c:chartSpace>')
            if not missing_relation:
                mode = ' TargetMode="External"' if external else ''
                z.writestr('ppt/charts/_rels/chart7.xml.rels',
                           f'<Relationships xmlns="{rel}"><Relationship Id="w" Type="{office}/package"'
                           f'{mode} Target="../embeddings/data.xlsx"/></Relationships>')
            if workbook:
                stream = io.BytesIO()
                with ZipFile(stream, 'w') as book:
                    book.writestr('xl/workbook.xml', '<workbook/>')
                    f = f'<f>{formula}</f>' if formula else ''
                    book.writestr('xl/worksheets/sheet1.xml',
                                  '<worksheet xmlns="http://schemas.openxmlformats.org/'
                                  f'spreadsheetml/2006/main"><c r="A3">{f}<v>{value}</v></c></worksheet>')
                z.writestr('ppt/embeddings/data.xlsx', stream.getvalue())

    def run_gate(self, **kwargs) -> dict:
        return gate.preservation_gate(self.source, self.candidate,
                                      gate.digest(self.source.read_bytes()),
                                      gate.digest(self.candidate.read_bytes()), **kwargs)

    def manifest(self) -> Path:
        files = []
        for role in ['authoring_code', 'source_data']:
            path = self.root / role
            path.write_text('isolated fixture')
            files.append({'path': path.name, 'sha256': gate.digest(path.read_bytes()), 'role': role})
        m = self.root / 'authoring.json'
        m.write_text(json.dumps({'source_pptx_sha256': gate.digest(self.source.read_bytes()), 'files': files}))
        return m

    def test_preserved_logical_owner_and_workbook_pass(self) -> None:
        self.assertTrue(self.run_gate()['passed'])

    def test_missing_workbook_blocks(self) -> None:
        self.package(self.candidate, workbook=False)
        self.assertTrue(self.run_gate()['delivery_blocked'])

    def test_missing_workbook_relation_blocks(self) -> None:
        self.package(self.candidate, missing_relation=True)
        self.assertFalse(self.run_gate()['passed'])

    def test_removed_externaldata_blocks(self) -> None:
        self.package(self.candidate, data_node=False)
        self.assertFalse(self.run_gate()['passed'])

    def test_chart_replaced_by_picture_blocks(self) -> None:
        self.package(self.candidate, chart=False)
        self.assertFalse(self.run_gate()['passed'])

    def test_external_workbook_blocks(self) -> None:
        self.package(self.candidate, external=True)
        self.assertFalse(self.run_gate()['passed'])

    def test_formula_loss_blocks(self) -> None:
        self.package(self.candidate, formula='')
        self.assertFalse(self.run_gate()['passed'])

    def test_formula_change_blocks(self) -> None:
        self.package(self.candidate, formula='SUM(A1:A1)')
        self.assertFalse(self.run_gate()['passed'])

    def test_numeric_edit_with_same_formulas_passes(self) -> None:
        self.package(self.candidate, value=13)
        self.assertTrue(self.run_gate()['passed'])

    def test_source_hash_mismatch_rejected(self) -> None:
        with self.assertRaises(ValueError):
            gate.preservation_gate(self.source, self.candidate, '0'*64, gate.digest(self.candidate.read_bytes()))

    def test_rebuild_without_source_manifest_blocked(self) -> None:
        self.assertFalse(self.run_gate(mode='regenerate')['passed'])

    def test_verified_source_allows_separate_regeneration(self) -> None:
        result = self.run_gate(mode='regenerate', authoring_manifest=self.manifest())
        self.assertTrue(result['passed'])
        self.assertFalse(result['automatic_regeneration_executed'])
        self.assertFalse(result['engine_defect_fixed'])
        self.assertFalse(result['candidate_deliverable'])

    def test_source_manifest_never_overrides_broken_candidate(self) -> None:
        self.package(self.candidate, workbook=False)
        result = self.run_gate(authoring_manifest=self.manifest())
        self.assertTrue(result['regeneration_eligible'])
        self.assertFalse(result['passed'])

    def test_changed_authoring_bytes_block_regeneration(self) -> None:
        manifest = self.manifest()
        (self.root/'source_data').write_text('changed')
        with self.assertRaises(ValueError):
            self.run_gate(mode='regenerate', authoring_manifest=manifest)

    def test_manifest_requires_code_and_data(self) -> None:
        manifest = self.manifest()
        data = json.loads(manifest.read_text());data['files'] = data['files'][:1]
        manifest.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            self.run_gate(mode='regenerate', authoring_manifest=manifest)

    def test_inputs_remain_unchanged(self) -> None:
        before = [p.read_bytes() for p in (self.source,self.candidate)]
        self.run_gate()
        self.assertEqual(before,[p.read_bytes() for p in (self.source,self.candidate)])


    def rewrite_source_chart(self, replacement: bytes) -> None:
        with ZipFile(self.source) as z:
            parts = {name: z.read(name) for name in z.namelist()}
        parts['ppt/charts/chart7.xml'] = parts['ppt/charts/chart7.xml'].replace(
            b'<c:barChart/>', replacement)
        with ZipFile(self.source, 'w') as z:
            for name, data in parts.items():
                z.writestr(name, data)

    def test_series_loss_blocks(self) -> None:
        self.rewrite_source_chart(b'<c:barChart><c:ser/></c:barChart>')
        self.assertFalse(self.run_gate()['passed'])

    def test_source_range_loss_blocks(self) -> None:
        self.rewrite_source_chart(b'<c:barChart><c:f>Sheet1!$A$1:$A$2</c:f></c:barChart>')
        self.assertFalse(self.run_gate()['passed'])

    def test_candidate_hash_mismatch_rejected(self) -> None:
        with self.assertRaises(ValueError):
            gate.preservation_gate(self.source, self.candidate,
                                   gate.digest(self.source.read_bytes()), '0'*64)

    def test_manifest_root_escape_rejected(self) -> None:
        manifest = self.manifest()
        data = json.loads(manifest.read_text())
        data['files'][0]['path'] = str(self.root/'authoring_code')
        manifest.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            self.run_gate(mode='regenerate', authoring_manifest=manifest)


if __name__ == '__main__':
    from console_encoding import configure_utf8_stdio
    configure_utf8_stdio()
    unittest.main(verbosity=2)
