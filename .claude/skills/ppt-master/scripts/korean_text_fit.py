#!/usr/bin/env python3
"""PPT Master - Measured Korean text fit precheck.

Measure actual licensed font glyph advances/ink with Pillow FreeType. Preserve
words and mixed number/English/% tokens. Do not shrink, truncate or add slides.
This precheck must be followed by final PPTX rendering and visual inspection.

Usage: python3 scripts/korean_text_fit.py CONTRACT.json --brief BRIEF.json
Examples: python3 scripts/korean_text_fit.py projects/private/fit.json --brief projects/private/brief.json
Dependencies: existing Pillow and fontTools runtime
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path

from console_encoding import configure_utf8_stdio
from private_font_cache import font_availability, inspect_font

configure_utf8_stdio()


def measure_text_fit(contract: dict, base: Path, brief: dict, brief_base: Path) -> dict:
    """Measure exact font/spacing/box inputs; overflow requires user review."""
    try:
        from PIL import ImageFont
        from fontTools.ttLib import TTFont
    except ImportError as exc:
        raise ValueError('Prepared Pillow/fontTools runtime required; no automatic installation') from exc
    verified=font_availability(brief,brief_base)
    if not verified['ok']: raise ValueError(verified.get('question') or 'Required licensed font unavailable')
    path=Path(contract['font_file']);path=path if path.is_absolute() else base/path
    face=inspect_font(path)
    if face['sha256'] not in verified['licensed_font_sha256'] or not any(record['sha256']==face['sha256'] for record in verified['records']):
        raise ValueError('Fit font not in licensed verified task inventory')
    size=contract['font_size_pt'];line=contract['line_spacing_pt'];paragraph=contract.get('paragraph_after_pt',contract.get('paragraph_spacing_pt',0));before=contract.get('paragraph_before_pt',0);tracking=contract.get('letter_spacing_pt',0)
    role=contract['role']
    size_policy=brief.get('font_size_policy',{})
    if size_policy.get('basis')=='specified' and size_policy.get('values',{}).get(role)!=size:
        raise ValueError('Fit point size differs from confirmed task role; no silent shrink')
    family_policy=brief.get('font_policy',{})
    role_family=family_policy.get('values',{}).get(role)
    alias_confirmed=any(alias['requested']==role_family and alias['sha256']==face['sha256'] for alias in verified['alias_resolutions'])
    if family_policy.get('basis')=='specified' and role_family not in face['family_aliases'] and not alias_confirmed:
        raise ValueError('Fit font family differs from confirmed task role')
    if any(type(v) not in (int,float) or not math.isfinite(v) for v in (size,line,paragraph,before,tracking)) or size<=0 or line<=0 or paragraph<0 or before<0:
        raise ValueError('Use explicit finite positive font/line spacing and nonnegative paragraph spacing and explicit letter spacing')
    text=contract['text'];box=contract['box_px'];margin=contract['margins_px']
    if not isinstance(text,str) or not text: raise ValueError('Required unchanged source text')
    if any(type(v) not in (int,float) or not math.isfinite(v) or v<0 for v in list(box.values())+list(margin.values())): raise ValueError('Invalid box/margins')
    width=box['width']-margin['left']-margin['right'];height=box['height']-margin['top']-margin['bottom']
    if width<=0 or height<=0: raise ValueError('Margins consume the text box')
    with TTFont(path,lazy=True) as font: cmap=font.getBestCmap()
    missing=sorted(set(c for c in text if not c.isspace() and ord(c) not in cmap))
    scale=4;px=size*96/72;measure=ImageFont.truetype(str(path),round(px*scale));advance=tracking*96/72
    def measured(s): return measure.getlength(s)/scale+max(len(s)-1,0)*advance
    rows=[];oversized=[];baseline=margin['top']+measure.getmetrics()[0]/scale
    for para_index,para in enumerate(text.split('\n')):
        baseline+=before*96/72
        current=''
        units=[]
        for token in para.split():
            if units and re.fullmatch(r'[+-]?\d+(?:[.,]\d+)?',units[-1]) and re.fullmatch(r'%p?|[A-Za-z]+',token):
                units[-1]+=' '+token
            else:
                units.append(token)
        for token in units:
            candidate=(current+' '+token).strip()
            if current and measured(candidate)>width:
                rows.append({'paragraph':para_index,'text':current,'baseline_px':baseline,'width_px':measured(current)});baseline+=line*96/72;current=token
            else: current=candidate
            if measured(token)>width and token not in oversized: oversized.append(token)
        rows.append({'paragraph':para_index,'text':current,'baseline_px':baseline,'width_px':measured(current)})
        baseline+=line*96/72+paragraph*96/72
    bottom=max(row['baseline_px']+measure.getbbox(row['text'],anchor='ls')[3]/scale for row in rows)
    ink_top=min(row['baseline_px']+measure.getbbox(row['text'],anchor='ls')[1]/scale for row in rows)
    ink_height=bottom-margin['top'];line_ink_heights=[(measure.getbbox(row['text'],anchor='ls')[3]-measure.getbbox(row['text'],anchor='ls')[1])/scale for row in rows]
    spacing_overlap=any(h>line*96/72 for h in line_ink_heights)
    overflow=bool(missing or oversized or ink_height>height or ink_top<margin['top'] or spacing_overlap)
    if tracking and any(0x1100<=ord(c)<=0x11ff or 0x0300<=ord(c)<=0x036f for c in text): overflow=True
    return {'method':'actual Pillow FreeType glyph advance/bbox at 4x scale; not native PowerPoint wrapping',
            'source_text_sha256':hashlib.sha256(text.encode()).hexdigest(),'font':face,'parameters':contract,
            'lines':rows,'usable_width_px':width,'usable_height_px':height,'measured_ink_height_px':ink_height,
            'missing_glyphs':missing,'oversized_words':oversized,'line_spacing_overlap':spacing_overlap,'overflow':overflow,
            'text_tokens_preserved':''.join(text.split())==''.join(''.join(row['text'].split()) for row in rows),
            'automatic_font_shrink':False,'content_omitted':False,'slide_count_changed':False,
            'next_action':'Request missing font/glyph support or user summary/split/approved box-spacing change' if overflow else 'Render final PPTX and visually inspect every page',
            'final_render_verified':False,'native_application_verified':False}


def main(argv: list[str] | None = None) -> int:
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('contract',type=Path);parser.add_argument('--brief',type=Path,required=True);parser.add_argument('--output',type=Path)
    args=parser.parse_args(argv)
    try:
        result=measure_text_fit(json.loads(args.contract.read_text(encoding='utf-8')),args.contract.resolve().parent,json.loads(args.brief.read_text(encoding='utf-8')),args.brief.resolve().parent)
        payload=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
        if args.output: args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(payload,encoding='utf-8')
        print(payload,end='');return 1 if result['overflow'] else 0
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print('Text fit blocked: '+str(exc),file=sys.stderr);return 1


if __name__=='__main__':
    raise SystemExit(main())
