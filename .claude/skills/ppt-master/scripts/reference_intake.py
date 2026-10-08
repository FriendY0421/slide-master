#!/usr/bin/env python3
"""PPT Master - Reference input facts.

Inspect synthetic or private reference bytes. Raster/PDF observations are
reconstruction inputs, never proof of original PowerPoint master or exact fonts.

Usage: python3 scripts/reference_intake.py FILE [--observations OBSERVATIONS.json]
Examples: python3 scripts/reference_intake.py projects/private/reference.png
Dependencies: Pillow; pypdf for PDF (existing runtime, no automatic install)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from console_encoding import configure_utf8_stdio

configure_utf8_stdio()
IMAGE_TYPES = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tif', '.tiff'}


def bind_photo_observations(reference: dict, observations: dict) -> dict:
    """Preserve inspected photo measurements/estimates bound to exact bytes.

    See docs/ppt-project/PHOTO_ORIGINAL_RECONSTRUCTION.md. This is an analysis
    sidecar for the existing template designer, not OCR or a new PPTX engine.
    """
    if reference['input_type'] not in IMAGE_TYPES:
        raise ValueError('Photo observations require an image reference')
    if not isinstance(observations, dict) or observations.get('source_sha256') != reference['input_sha256']:
        raise ValueError('Photo observations differ from the actual input SHA256')
    if type(observations.get('schema_version')) is not int or observations['schema_version'] != 1:
        raise ValueError('Photo observations require schema_version 1')
    fields = {'font_family', 'font_size_pt', 'color', 'font_weight', 'line_spacing_pt',
              'paragraph_spacing_pt', 'row_gap_px', 'column_gap_px', 'alignment',
              'image_crop_px', 'text', 'geometry_px', 'tracking_pt'}
    bases = {'visual_estimate', 'visible_text', 'user_instruction', 'unknown'}
    certainty = {'observed', 'estimated', 'confirmed', 'unverified'}
    width, height = reference['pixel_size']

    def bounds(box: object) -> bool:
        return (isinstance(box, list) and len(box) == 4
                and all(type(v) in (int, float) and math.isfinite(v) for v in box)
                and box[0] >= 0 and box[1] >= 0 and box[2] > 0 and box[3] > 0
                and box[0] + box[2] <= width and box[1] + box[3] <= height)

    region = observations.get('screen_region_px')
    if not bounds(region):
        raise ValueError('Photo screen region must be inside the actual image')
    ratio = observations.get('slide_aspect_ratio')
    if type(ratio) not in (int, float) or not math.isfinite(ratio) or ratio <= 0:
        raise ValueError('Photo slide aspect ratio requires an explicit positive estimate')
    quad = observations.get('screen_quad_px')
    if quad is not None:
        if (not isinstance(quad, list) or len(quad) != 4 or any(
                not isinstance(p, list) or len(p) != 2 or any(
                    type(v) not in (int, float) or not math.isfinite(v) for v in p)
                or not (region[0] <= p[0] <= region[0] + region[2]
                        and region[1] <= p[1] <= region[1] + region[3]) for p in quad)):
            raise ValueError('Photo screen quadrilateral must have four bounded pixel corners')
        turns = []
        for index in range(4):
            a, b, c = quad[index], quad[(index + 1) % 4], quad[(index + 2) % 4]
            turns.append((b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0]))
        if not (all(v > 0 for v in turns) or all(v < 0 for v in turns)):
            raise ValueError('Photo screen quadrilateral must be convex and ordered')
    items = observations.get('items')
    if not isinstance(items, list) or not items:
        raise ValueError('Photo observations require per-element items')
    seen = set()
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get('element_id'), str) or not item['element_id']:
            raise ValueError('Photo observation requires an element_id')
        if any(not isinstance(item.get(k), str) for k in ('property', 'basis', 'certainty')) or (
                item['property'] not in fields or item['basis'] not in bases
                or item['certainty'] not in certainty):
            raise ValueError('Photo observation requires a supported property, basis and certainty')
        identity = (item['element_id'], item['property'])
        if identity in seen:
            raise ValueError('Conflicting duplicate photo element/property observation')
        seen.add(identity)
        if 'value' not in item or not bounds(item.get('source_bounds_px')):
            raise ValueError('Photo observation requires a value and source pixel bounds')
        box = item['source_bounds_px']
        if (box[0] < region[0] or box[1] < region[1]
                or box[0] + box[2] > region[0] + region[2]
                or box[1] + box[3] > region[1] + region[3]):
            raise ValueError('Photo element bounds must be inside the chosen screen region')
        basis, confidence = item['basis'], item['certainty']
        if item['value'] is None and basis != 'unknown':
            raise ValueError('Null photo values must remain explicitly unverified')
        if basis == 'user_instruction' and (
                not isinstance(item.get('source_ref'), str) or not item['source_ref'].strip()):
            raise ValueError('User-specified photo values require a current instruction reference')
        if ((basis == 'visual_estimate' and confidence != 'estimated')
                or (basis == 'visible_text' and confidence != 'observed')
                or (basis == 'unknown' and (confidence != 'unverified' or item['value'] is not None))
                or (basis == 'user_instruction' and confidence != 'confirmed')):
            raise ValueError('Photo observation certainty conflicts with its provenance')
        if item['property'] in {'font_family', 'color'} and basis == 'visible_text':
            raise ValueError('Photo pixels do not verify exact font names or original theme colors')
        if item.get('render_as') not in ('native_editable', 'preserved_image_crop'):
            raise ValueError('Photo observation requires explicit reconstruction editability')
        if item['render_as'] == 'preserved_image_crop':
            if item['property'] not in {'image_crop_px', 'geometry_px'}:
                raise ValueError('Text/style observations must remain editable reconstruction targets')
            if box[2] * box[3] >= region[2] * region[3] * 0.8:
                raise ValueError('Whole-slide photograph is not an editable reconstruction')
        if item['property'].endswith(('_pt', '_gap_px')) and item['value'] is not None:
            value = item['value']
            if type(value) not in (int, float) or not math.isfinite(value):
                raise ValueError('Photo point sizes/spacing must be finite numbers')
            if item['property'] == 'font_size_pt' and value <= 0:
                raise ValueError('Photo point sizes must be positive')
            if item['property'] != 'tracking_pt' and value < 0:
                raise ValueError('Photo spacing must not be negative')
        if item['value'] is not None:
            field, value = item['property'], item['value']
            if field in {'text', 'font_family', 'color'} and (not isinstance(value, str) or not value):
                raise ValueError('Photo text/font/color values must be non-empty strings')
            if field in {'geometry_px', 'image_crop_px'} and not bounds(value):
                raise ValueError('Photo geometry/crop values must be valid pixel bounds')
            if field in {'geometry_px', 'image_crop_px'} and (
                    value[0] < region[0] or value[1] < region[1]
                    or value[0] + value[2] > region[0] + region[2]
                    or value[1] + value[3] > region[1] + region[3]):
                raise ValueError('Photo geometry/crop values must remain inside the screen region')
            if field == 'alignment' and value not in ('left', 'center', 'right', 'start', 'end', 'justify'):
                raise ValueError('Photo alignment must be explicit')
            if field == 'font_weight' and not (
                    value in ('normal', 'bold') or type(value) is int and value in range(100, 1000, 100)):
                raise ValueError('Photo font weight must be normal/bold or a 100-900 integer')
    if not any(i['render_as'] == 'native_editable' for i in items):
        raise ValueError('Photo reconstruction requires native editable targets')
    result = dict(reference)
    result['photo_observations'] = observations
    result['reconstruction_contract'] = {
        'replication_mode': 'standard', 'visual_fidelity': 'literal',
        'source_master_theme_recovered': False, 'automatic_ocr_performed': False,
        'reference_pixels_inspected': observations.get('pixels_inspected') is True,
        'screen_region_basis': 'visual_estimate', 'slide_aspect_basis': 'visual_estimate',
        'visual_equivalence_guaranteed': False,
        'uncertainties': ['camera perspective/moire', 'original font/theme/logo identity'],
        'requires_comparison_qa': True,
        'next_owner': 'project-private create-template; existing SVG compiler',
    }
    return result


def inspect_reference(path: Path) -> dict:
    """Report exact input facts and the review needed before reconstruction."""
    result = {'input_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'input_type': path.suffix.lower(),
              'fully_editable_reproduction_verified': False, 'font_pt_equivalence_verified': False}
    if path.suffix.lower() in {'.pptx', '.potx'}:
        with zipfile.ZipFile(path) as package:
            names = package.namelist()
            fonts, points = set(), set()
            for name in names:
                if name.startswith(('ppt/slides/', 'ppt/slideMasters/', 'ppt/slideLayouts/', 'ppt/theme/')) and name.endswith('.xml'):
                    for element in ET.fromstring(package.read(name)).iter():
                        family = element.get('typeface')
                        if family and not family.startswith('+'): fonts.add(family)
                        if element.get('sz') and element.tag.rsplit('}', 1)[-1] in {'rPr', 'defRPr', 'endParaRPr'}:
                            points.add(int(element.get('sz')) / 100)
            size = ET.fromstring(package.read('ppt/presentation.xml')).find('{http://schemas.openxmlformats.org/presentationml/2006/main}sldSz')
            if size is None:
                raise ValueError('Native reference has no slide-size structure')
            result.update({'route': 'native_pptx' if path.suffix.lower() == '.pptx' else 'native_potx_extract_then_normalize',
                           'source_structure': 'actual OOXML master/layout/theme parts',
                           'observed_font_families': sorted(fonts), 'direct_point_sizes': sorted(points),
                           'inherited_values': 'not guessed; actual resolution/render still required',
                           'slide_size_emu': {k: int(size.get(k)) for k in ('cx', 'cy')},
                           'master_parts': [n for n in names if n.startswith('ppt/slideMasters/slideMaster') and n.endswith('.xml')],
                           'layout_parts': [n for n in names if n.startswith('ppt/slideLayouts/slideLayout') and n.endswith('.xml')],
                           'theme_parts': [n for n in names if n.startswith('ppt/theme/') and n.endswith('.xml')]})
    elif path.suffix.lower() in IMAGE_TYPES:
        from PIL import Image
        with Image.open(path) as picture:
            picture.load();width, height = picture.size
        ratio = width / height
        result.update({'route': 'reference_reconstruction', 'source_structure': 'pixels; no original master/layout',
                       'pixel_size': [width, height], 'observed_aspect_ratio': ratio,
                       'suggested_slide_ratio': '16:9' if abs(ratio-16/9)<0.03 else '4:3' if abs(ratio-4/3)<0.03 else 'unknown/crop-perspective-review-required',
                       'requires': ['actual pixel visual inspection', 'perspective review', 'crop confirmation', 'OCR/text confirmation', 'slide aspect confirmation'],
                       'font_pt_basis': 'estimated until user confirms', 'background_raster_is_not_full_editability': True})
    elif path.suffix.lower() == '.pdf':
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise ValueError('PDF inspection runtime unavailable; use prepared renderer, do not install automatically') from exc
        from pypdf.errors import PdfReadError
        try:
            reader = PdfReader(path)
        except PdfReadError as exc:
            raise ValueError('Invalid PDF reference; request a readable original') from exc
        result.update({'route': 'reference_reconstruction', 'source_structure': 'PDF page appearance; no original master/layout',
                       'pages': [{'width_pt': float(page.mediabox.width), 'height_pt': float(page.mediabox.height)} for page in reader.pages],
                       'requires': ['render and inspect every selected page', 'crop confirmation', 'OCR/text confirmation', 'slide aspect confirmation'],
                       'font_pt_basis': 'estimated until verified/confirmed'})
    else:
        raise ValueError('Supported references: PPTX/POTX, PDF, photos/screenshots')
    return result


def main(argv: list[str] | None = None) -> int:
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('file',type=Path);parser.add_argument('--output',type=Path)
    parser.add_argument('--observations', type=Path, help='inspected photo sidecar; bind exact source bytes')
    args=parser.parse_args(argv)
    try:
        result=inspect_reference(args.file)
        if args.observations:
            result=bind_photo_observations(result, json.loads(args.observations.read_text(encoding='utf-8')))
        payload=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
        if args.output: args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(payload,encoding='utf-8')
        print(payload,end='');return 0
    except (OSError, ValueError, zipfile.BadZipFile, ET.ParseError) as exc:
        print('Reference inspection blocked: '+str(exc),file=sys.stderr);return 1


if __name__=='__main__':
    raise SystemExit(main())
