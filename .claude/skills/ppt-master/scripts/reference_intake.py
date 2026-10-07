#!/usr/bin/env python3
"""PPT Master - Reference input facts.

Inspect synthetic or private reference bytes. Raster/PDF observations are
reconstruction inputs, never proof of original PowerPoint master or exact fonts.

Usage: python3 scripts/reference_intake.py FILE
Examples: python3 scripts/reference_intake.py projects/private/reference.png
Dependencies: Pillow; pypdf for PDF (existing runtime, no automatic install)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from console_encoding import configure_utf8_stdio

configure_utf8_stdio()
IMAGE_TYPES = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tif', '.tiff'}


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
    args=parser.parse_args(argv)
    try:
        result=inspect_reference(args.file);payload=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
        if args.output: args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(payload,encoding='utf-8')
        print(payload,end='');return 0
    except (OSError, ValueError, zipfile.BadZipFile, ET.ParseError) as exc:
        print('Reference inspection blocked: '+str(exc),file=sys.stderr);return 1


if __name__=='__main__':
    raise SystemExit(main())
