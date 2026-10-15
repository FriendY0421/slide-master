#!/usr/bin/env python3
"""PPT Master - Process-checked review renderer.

Render an existing private PPTX with the supplied Node runtime. Reuse the
previous operating helper's Windows CPU setter without package or OS changes.
Only finalize a receipt after process exit 0 and all image hashes match.

Usage: python render_pptx_review.py DECK OUTPUT --node NODE --runtime NODE_MODULES --geometry-only
Examples: see docs/ppt-project/RENDERER_CONTINUATION_20261013.md
Dependencies: standard library; existing supplied Artifact Tool/skia-canvas.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('deck',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('--node',type=Path,required=True)
    parser.add_argument('--runtime',type=Path,required=True)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--geometry-only',action='store_true')
    mode.add_argument('--profile',type=Path)
    args=parser.parse_args()
    deck=args.deck.resolve(strict=True)
    output=args.output.resolve()
    with zipfile.ZipFile(deck) as package:
        namespace={'p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
        presentation=ET.fromstring(package.read('ppt/presentation.xml'))
        slide_count=len(presentation.findall('p:sldIdLst/p:sldId',namespace))
        if args.geometry_only:
            for name in package.namelist():
                if name.startswith('ppt/charts/'):
                    parser.error('Geometry-only mode excludes charts/text; provide an approved font profile for text-bearing review')
                if name.endswith('.xml') and name.startswith(('ppt/slides/','ppt/slideMasters/','ppt/slideLayouts/')):
                    xml=ET.fromstring(package.read(name))
                    text_nodes=[]
                    if name.startswith('ppt/slides/'):
                        text_nodes=list(xml.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}t'))
                    else:
                        # Empty slides do not display the template's instructional
                        # placeholder samples. Non-placeholder template text is real.
                        for shape in xml.findall('.//p:sp',namespace)+xml.findall('.//p:graphicFrame',namespace):
                            if shape.find('.//p:ph',namespace) is None:
                                text_nodes.extend(shape.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}t'))
                        if any(value=='1' for hf in xml.findall('p:hf',namespace)
                               for value in hf.attrib.values()):
                            parser.error('Geometry-only mode excludes enabled template footer/header fields')
                    if any((node.text or '').strip() for node in text_nodes):
                        parser.error('Geometry-only mode requires a text-free deck; no silent fallback rendering')
    if output.exists() and any(output.iterdir()):
        parser.error('Use an empty/new output directory; existing review evidence is preserved')
    output.mkdir(parents=True,exist_ok=True)
    before=hashlib.sha256(deck.read_bytes()).hexdigest()
    profile='geometry-only' if args.geometry_only else str(args.profile.resolve(strict=True))
    command=[str(args.node.resolve(strict=True)),str(Path(__file__).with_suffix('.mjs')),
             str(deck),str(output),str(args.runtime.resolve(strict=True)),profile]
    try:
        child=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=300)
    except (OSError,subprocess.TimeoutExpired) as exc:
        (output/'process-result.json').write_text(json.dumps({'completed':False,'error':str(exc)}),encoding='utf-8')
        print(f'Render process failed: {exc}')
        return 1
    status={'exit_code':child.returncode,'completed':child.returncode==0,
            'stdout':child.stdout,'stderr':child.stderr}
    (output/'process-result.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8')
    if child.returncode:
        print(f'Render process failed with exit {child.returncode}; partial artifacts are not a successful receipt')
        return 1
    receipt_path=output/'render-manifest.json'
    try:
        receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
        if receipt['pptx_sha256']!=before or hashlib.sha256(deck.read_bytes()).hexdigest()!=before:
            raise ValueError('Input source changed')
        if not receipt['images'] or len(receipt['images'])!=slide_count:
            raise ValueError('Rendered page count differs from the actual presentation')
        seen_images=set()
        for index,item in enumerate(receipt['images'],start=1):
            if type(item['slide']) is not int or item['slide']!=index:
                raise ValueError('Rendered pages must identify each actual slide once, in presentation order')
            image=(output/item['path']).resolve(strict=True)
            if image in seen_images:
                raise ValueError('Each rendered slide requires a distinct page image')
            seen_images.add(image)
            if image.parent!=output or hashlib.sha256(image.read_bytes()).hexdigest()!=item['sha256']:
                raise ValueError('Missing/outside/changed page image')
        receipt['process_completed']=True
        receipt['process_exit_code']=0
        receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print(f'Render receipt failed: {exc}')
        return 1
    print(json.dumps({'pages':len(receipt['images']),'process_completed':True,
                      'text_font_verified':receipt['text_font_verified']}))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
