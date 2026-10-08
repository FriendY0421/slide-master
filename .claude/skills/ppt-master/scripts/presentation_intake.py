#!/usr/bin/env python3
"""PPT Master - Current task intake contract.

Library for presentation_brief.py workflow_version 2. Stage only missing questions
and retain the selected route's actual user approval gates.

Usage: used through presentation_brief.py, not as a standalone generator
Examples: validate_intake(brief, brief_directory)
Dependencies: existing reference/font inspection helpers
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from reference_intake import IMAGE_TYPES, inspect_reference, bind_photo_observations


def purpose_menu(request_text: str, choice: str | None, confirmed: bool) -> dict:
    """Recommend a purpose without turning menu state into user approval."""
    choices = [
        {'id': 'copy_original', 'label': '원본 그대로 복제'},
        {'id': 'edit_existing', 'label': '기존 자료 수정·보완'},
        {'id': 'new_from_template', 'label': '템플릿으로 새로 제작'},
    ]
    recommend = 'copy_original' if re.search(
        r'복제|똑같|동일하게|원본\s*그대로|identical|replica|duplicate',
        request_text, re.IGNORECASE) else None
    valid = isinstance(choice, str) and choice in {item['id'] for item in choices}
    return {'choices': choices, 'recommended': recommend,
            'tentative_choice': choice if valid else None,
            'selected': choice if valid and confirmed else None,
            'confirmed': valid and confirmed, 'actually_rendered': False}


def validate_intake(brief: dict, base: Path) -> dict:
    """Bundle missing settings after mode/reference selection, without approval."""
    errors, missing, references = [], [], []
    mode=brief.get('mode');stage='settings'
    menu = purpose_menu(str(brief.get('request_text') or ''), brief.get('purpose_choice'),
                        brief.get('purpose_confirmed') is True)
    for key in ('purpose_confirmed', 'purpose_menu_required'):
        if key in brief and type(brief[key]) is not bool:
            errors.append(key + ' must be boolean')
    if 'output_intent' in brief and brief['output_intent'] not in ('blank_template', 'content_deck'):
        errors.append('Unknown output_intent')
    if brief.get('purpose_choice') and menu['tentative_choice'] is None:
        errors.append('Unknown purpose_choice')
    confirmation = brief.get('purpose_confirmation_ref')
    menu['confirmation_ref'] = confirmation if isinstance(confirmation, str) else None
    if menu['confirmed'] and (not isinstance(confirmation, str) or not confirmation.strip()):
        errors.append('Record the current user purpose-confirmation reference')
        menu['confirmed'], menu['selected'] = False, None
    if menu['selected'] in {'copy_original', 'edit_existing'}:
        if mode is None:
            mode = 'custom'
        elif mode != 'custom':
            errors.append('Original-copy/edit selection requires custom reference mode')
    if brief.get('schema_version')!=1 or brief.get('scope')!='task':
        errors.append('Require schema_version 1 and task scope')
    def files(key):
        raw=brief.get(key,[])
        if not isinstance(raw,list) or any(not isinstance(v,str) or not v.strip() for v in raw):
            errors.append(key+' must be paths');return []
        paths=[Path(v) if Path(v).is_absolute() else base/v for v in raw]
        for p in paths:
            if not p.is_file(): errors.append(key+' file missing: '+str(p))
        return [p for p in paths if p.is_file()]
    content=files('content_files')
    originals=files('template_files');samples=files('sample_files');extra=files('reference_files')
    if mode not in {'builtin','custom'}:
        stage='mode';missing=['제작 모드: 기본 템플릿 / 사용자 정의']
    elif mode=='builtin':
        if originals or samples or extra: errors.append('User reference files require custom mode')
        if not brief.get('template_id'): stage='template';missing=['실제 미리보기 확인 후 기본 템플릿 선택']
        elif not brief.get('production_preset_id'): missing.append('제작 프리셋 선택')
    else:
        if brief.get('template_id') or brief.get('production_preset_id'): errors.append('Custom mode does not impose builtin template/preset')
        for path in originals+samples+extra:
            try: references.append(inspect_reference(path))
            except (OSError,ValueError,zipfile.BadZipFile,ET.ParseError) as exc: errors.append(str(exc))
        if not references: stage='reference';missing=['템플릿 또는 예제 PPTX/POTX/PDF/사진·스크린샷']
        elif any(r['route']=='reference_reconstruction' for r in references):
            # The human receipt is bound to actual bytes; it is not auto-created.
            receipt=brief.get('reference_review',{})
            for reference in references:
                if reference['route']!='reference_reconstruction': continue
                item=receipt.get(reference['input_sha256'],{}) if isinstance(receipt,dict) else {}
                if not isinstance(item, dict):
                    item = {}
                required=['pixels_inspected','crop_confirmed','text_confirmed','aspect_confirmed']
                if reference['input_type'] in IMAGE_TYPES: required.append('perspective_confirmed')
                if any(item.get(k) is not True for k in required):
                    missing.append('참조 픽셀·원근/크롭·텍스트·화면비 확인')
                    break
                if menu['selected'] == 'copy_original' and reference['input_type'] in IMAGE_TYPES:
                    observation_path = item.get('observations_file')
                    if not isinstance(observation_path, str) or not observation_path:
                        missing.append('사진 원본 화면 영역·요소별 관찰/추정 기록')
                        continue
                    try:
                        path = Path(observation_path)
                        path = path if path.is_absolute() else base / path
                        observed = json.loads(path.read_text(encoding='utf-8'))
                        bound = bind_photo_observations(reference, observed)
                        if not bound['reconstruction_contract']['reference_pixels_inspected']:
                            missing.append('사진 원본 픽셀 직접 확인')
                        reference.update(bound)
                    except (OSError, ValueError) as exc:
                        errors.append(str(exc))
    if stage=='settings':
        blank_reference = (menu['selected'] == 'copy_original' and mode == 'custom'
                           and bool(references) and brief.get('output_intent') == 'blank_template'
                           and all(r['input_type'] in IMAGE_TYPES for r in references))
        if not brief.get('content_text') and not content and not blank_reference:
            missing.append('이번 내용 자료')
        for key,label in [('font_policy','글꼴'),('font_size_policy','글자 크기')]:
            policy=brief.get(key)
            if not isinstance(policy,dict) or policy.get('basis') not in {'source','specified'}:
                missing.append(label+' 기준: 선택 양식 유지 또는 지정값');continue
            if policy['basis']=='specified':
                values=policy.get('values')
                if not isinstance(values,dict) or not values: missing.append(label+' 지정값');continue
                if key=='font_policy' and any(not isinstance(v,str) or not v.strip() for v in values.values()): errors.append('Invalid font family values')
                if key=='font_size_policy' and any(type(v) not in (int,float) or not math.isfinite(v) or v<=0 for v in values.values()): errors.append('Point sizes must be finite and positive')
            elif any(r['route']=='reference_reconstruction' for r in references):
                if brief.get('estimated_typography_confirmed') is not True: missing.append(label+' 추정값 확인 또는 지정값')
                elif key=='font_size_policy':
                    sizes=brief.get('estimated_typography',{}).get('point_sizes',{})
                    if not isinstance(sizes,dict) or not sizes or any(type(v) not in (int,float) or not math.isfinite(v) or v<=0 for v in sizes.values()):
                        missing.append('추정 pt 지정값 표시와 확인')
        if type(brief.get('slide_count')) is not int or brief['slide_count']<=0:
            missing.append('전체 슬라이드 장수: 양의 정수')
        rules=brief.get('writing_rules')
        if not (isinstance(rules,list) and rules and all(isinstance(v,str) and v.strip() for v in rules)) and brief.get('writing_rules_policy')!='source':
            missing.append('기본 작성 기준 또는 선택 양식 기준 유지')
    matching=brief.get('font_matching',{})
    if any(r['route']=='reference_reconstruction' for r in references):
        if brief.get('font_policy',{}).get('basis')=='specified' and not matching:
            matching={'mode':'explicit_request','confidence':'not_inferred','user_confirmed':brief.get('inputs_confirmed') is True,'same_font_verified':False}
        elif brief.get('font_policy',{}).get('basis')=='source' or (isinstance(matching,dict) and matching.get('candidates')):
            selected=matching.get('selected',{}) if isinstance(matching,dict) else {}
            candidates=matching.get('candidates',[]) if isinstance(matching,dict) else []
            valid=False
            for candidate in candidates if isinstance(candidates,list) else []:
                if not isinstance(candidate,dict) or candidate.get('sha256')!=selected.get('sha256'):
                    continue
                try:
                    preview=Path(candidate['preview_file']);preview=preview if preview.is_absolute() else base/preview
                    valid=hashlib.sha256(preview.read_bytes()).hexdigest()==candidate['preview_sha256'] and candidate.get('license_status')=='allowed' and candidate.get('rendered_font_sha256')==candidate.get('sha256') and candidate.get('preview_reviewed') is True
                except (OSError,KeyError,ValueError):
                    valid=False
                if valid:
                    break
            if not (isinstance(matching,dict) and matching.get('confidence') in {'low','medium','high'} and matching.get('user_confirmed') is True and matching.get('similarity_approved') is True and selected.get('family') and valid):
                missing.append('보관 폰트 후보 미리보기·허용된 사용권·추정 신뢰도 확인 및 유사 글꼴 선택 승인')
            matching={**matching,'same_font_verified':False,'actual_render_match_verified':False} if isinstance(matching,dict) else {'same_font_verified':False}
    native=bool(references) and all(r['route']=='native_pptx' for r in references)
    route='main_svg' if mode=='builtin' else 'ppt-template-fill' if native else 'reference/template import then confirmed main SVG' if references else None
    if mode=='custom' and any(r['route']=='native_potx_extract_then_normalize' for r in references):
        route='native POTX master/layout extraction; confirmed normalization before fill'
    if (brief.get('purpose_menu_required') is True or 'purpose_choice' in brief
            or 'purpose_confirmed' in brief) and not menu['confirmed']:
        stage = 'purpose'
        missing = ['목적 선택 확인: 원본 그대로 복제 / 기존 자료 수정·보완 / 템플릿으로 새로 제작']
    photo_selection = None
    if menu['selected'] == 'copy_original' and references:
        photo_selection = {'kind': 'user_reference_original', 'confirmed': True,
                           'confirmation_ref': menu['confirmation_ref'],
                           'input_sha256': [r['input_sha256'] for r in references],
                           'registered_active_template': False,
                           'exact_source_font_verified': False}
    return {'schema_version':1,'workflow_version':2,'mode':mode,'scope':'task','stage':stage,
            'purpose_menu_contract':menu, 'reference_selection':photo_selection,
            'mode_menu_contract':{'choices':[{'id':'builtin','label':'기본 템플릿'},{'id':'custom','label':'사용자 정의'}], 'actually_rendered':False},
            'input_complete':not missing and not errors,'inputs_confirmed':brief.get('inputs_confirmed') is True,
            'ready_for_plan':not missing and not errors and brief.get('inputs_confirmed') is True,
            'ready_for_generation':False,'missing_required':missing,'errors':errors,
            'question':'이번 단계에서 다음 항목만 함께 확인해 주세요: '+'; '.join(missing) if missing else None,
            'references':references,'font_matching':matching,'route':route,'requested_slide_count':brief.get('slide_count'),
            'next_gate':'existing template/preset/storyline approval' if mode=='builtin' else 'actual reference review and confirmed reconstruction/fill plan',
            'privacy':'Actual references/fonts remain user-private; no public upload or automatic installation'}


def validate_slide_count(brief: dict, planned_count: int, output_count: int | None = None) -> list[str]:
    """Compare both approved plan and final read-back with the explicit request."""
    expected=brief.get('slide_count')
    if type(expected) is not int or expected<=0: return ['Requested slide_count must be a positive integer']
    errors=[]
    if type(planned_count) is not int or planned_count!=expected: errors.append('Plan slide count differs from requested slide_count')
    if output_count is not None and (type(output_count) is not int or output_count!=expected): errors.append('Output slide count differs from requested slide_count')
    return errors
