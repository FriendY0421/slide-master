#!/usr/bin/env python3
"""PPT Master - Request entry and bound private photo-review handoff.

Prepare the purpose menu or retain the current user's explicit choice. Only the
opt-in photo-review flag calls the existing compiler; other routes keep their
own gates. This does not render a host UI or authenticate host events.

Usage: python3 scripts/presentation_request.py BRIEF.json --request-text REQUEST
Examples: python3 scripts/presentation_request.py projects/private/brief.json
          --request-text '복제해줘' --request-ref CURRENT_MESSAGE
Dependencies: existing intake, photo compiler and supplied Presentations runtime
See docs/ppt-project/PHOTO_REQUEST_ENTRY.md.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile

from console_encoding import configure_utf8_stdio
from presentation_brief import check_environment, validate_brief
from reference_intake import IMAGE_TYPES

configure_utf8_stdio()
CHOICES = ('copy_original', 'edit_existing', 'new_from_template')


def prepare_request(brief: dict, text: str, request_ref: str | None,
                    choice: str | None, choice_ref: str | None) -> tuple[dict, dict]:
    """Retain actual selection provenance; keywords alone remain recommendations."""
    if not isinstance(brief, dict) or brief.get('workflow_version') != 2:
        raise ValueError('New request entry requires workflow_version 2')
    if not text.strip():
        raise ValueError('Current request text required')
    if request_ref is not None and not request_ref.strip():
        raise ValueError('Current request reference must not be empty')
    if (choice is None) != (choice_ref is None):
        raise ValueError('Purpose choice and its current confirmation reference must be supplied together')
    current = copy.deepcopy(brief)
    current.update(request_text=text, purpose_menu_required=True)
    origin = 'task_brief' if current.get('purpose_confirmed') is True else None
    if choice is not None:
        if choice not in CHOICES or not choice_ref.strip():
            raise ValueError('Explicit purpose choice and nonempty confirmation reference required')
        selected, reference, origin = choice, choice_ref, 'explicit_selection'
    else:
        command = ''.join(text.split()).strip('.! ?~').casefold()
        direct = command in {'복제해줘', '복제해주세요', '똑같이', '똑같이만들어줘',
                             '똑같이만들어주세요', '원본그대로', '원본그대로복제해줘',
                             '사진과똑같이만들어줘', '원본그대로만들어줘',
                             'duplicate', 'copytheoriginal'}
        if not direct or not isinstance(request_ref, str) or not request_ref.strip():
            return current, {'purpose_origin': origin, 'host_event_authenticated': False}
        selected, reference, origin = 'copy_original', request_ref, 'explicit_request'
    current.update(purpose_choice=selected, purpose_confirmed=True, purpose_confirmation_ref=reference)
    return current, {'purpose_origin': origin, 'host_event_authenticated': False}


def bind_photo_plan(brief: dict, report: dict, plan: dict, base: Path) -> dict:
    """Bind the selected purpose and exact current observations before a build."""
    if not report.get('ready_for_plan') or report.get('mode') != 'custom':
        raise ValueError('Current confirmed custom intake must be ready before photo review')
    menu = report['purpose_menu_contract']
    if menu.get('selected') != 'copy_original' or menu.get('confirmed') is not True:
        raise ValueError('Photo review requires actual original-copy selection')
    references = report['references']
    if not references or any(ref['input_type'] not in IMAGE_TYPES for ref in references):
        raise ValueError('This handoff supports image references only; retain the selected owner for other sources')
    if not isinstance(plan, dict):
        raise ValueError('Model photo plan must be an object')
    bound = copy.deepcopy(plan)
    expected = {'purpose_choice': 'copy_original', 'purpose_confirmed': True,
                'purpose_confirmation_ref': menu['confirmation_ref']}
    for key, value in expected.items():
        if key in bound and (type(bound[key]) is not type(value) or bound[key] != value):
            raise ValueError('Photo plan purpose conflicts with the current request selection')
        bound[key] = value
    if bound.get('slide_count') != report['requested_slide_count']:
        raise ValueError('Photo plan slide count differs from current intake')
    sources = {ref['input_sha256']: ref for ref in references}
    pages = bound.get('pages')
    if (not isinstance(pages, list) or not pages or any(not isinstance(page, dict)
            or not isinstance(page.get('source'), dict) for page in pages)):
        raise ValueError('Complete model-observed photo plan required; entry performs no OCR')
    if {page.get('source', {}).get('sha256') for page in pages} != set(sources):
        raise ValueError('Photo plan source hashes differ from current input references')
    for page in pages:
        reference = sources[page['source']['sha256']]
        if page.get('observations') != reference.get('photo_observations'):
            raise ValueError('Photo plan observations differ from current inspected sidecar')
    if not isinstance(bound.get('font_choice'), dict):
        raise ValueError('Explicit photo font choice required')
    if any(not isinstance(page.get('elements'), list) or any(not isinstance(element, dict)
            for element in page['elements']) for page in pages):
        raise ValueError('Photo elements must be objects in complete lists')
    family = bound['font_choice'].get('family')
    policy = brief.get('font_policy', {})
    if policy.get('basis') == 'specified' and any(
            value.casefold() != str(family).casefold() for value in policy['values'].values()):
        raise ValueError('Photo plan font differs from current task font policy')
    sizes = brief.get('font_size_policy', {})
    if sizes.get('basis') == 'specified':
        allowed = set(sizes['values'].values())
        if any(element.get('font_pt') not in allowed for page in pages
               for element in page.get('elements', []) if element.get('type') == 'text'):
            raise ValueError('Photo plan point size is outside current task values')
    # A private snapshot changes its directory. Resolve only actual file fields;
    # keep literal text, observations and confirmation references unchanged.
    def absolute(value: str) -> str:
        path = Path(value)
        return str((path if path.is_absolute() else base / path).resolve())
    for page in pages:
        if page['source'].get('file'):
            page['source']['file'] = absolute(page['source']['file'])
        for element in page.get('elements', []):
            if element.get('type') == 'image':
                element['asset_file'] = absolute(element['asset_file'])
    fonts = bound.get('font_choice', {})
    if 'font_files' in fonts:
        fonts['font_files'] = {key: absolute(value) for key, value in fonts['font_files'].items()}
    if fonts.get('font_license_review', {}).get('evidence_file'):
        fonts['font_license_review']['evidence_file'] = absolute(fonts['font_license_review']['evidence_file'])
    return bound


def build_bound_review(brief: dict, report: dict, plan_path: Path, parent: Path,
                       shared_skill: Path, evidence: dict) -> dict:
    """Call the existing owner with one bound snapshot, never a stale re-read."""
    import photo_reconstruct as photo
    plan_bytes = plan_path.read_bytes()
    plan = bind_photo_plan(brief, report, json.loads(plan_bytes), plan_path.parent)
    parent = parent.resolve()
    if not parent.is_relative_to(photo.REPO / 'projects'):
        raise ValueError('Request review output must stay in gitignored repository projects/')
    parent.mkdir(parents=True, exist_ok=True)
    snapshot_bytes = (json.dumps(plan, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    with tempfile.TemporaryDirectory(prefix='_entry_', dir=parent) as temporary:
        snapshot = Path(temporary) / 'bound-plan.json'
        snapshot.write_bytes(snapshot_bytes)
        progress = io.StringIO()
        with contextlib.redirect_stdout(progress):
            result = photo.build_review(snapshot, parent, shared_skill)
    workspace = Path(result['workspace'])
    entry = {**evidence, 'schema_version': 1, 'selected_purpose': 'copy_original',
             'execution_performed': True,
             'purpose_confirmation_ref': report['purpose_menu_contract']['confirmation_ref'],
             'reference_sha256': [ref['input_sha256'] for ref in report['references']],
             'original_model_plan_sha256': hashlib.sha256(plan_bytes).hexdigest(),
             'bound_model_plan_sha256': hashlib.sha256(snapshot_bytes).hexdigest(),
             'effective_brief_sha256': hashlib.sha256(
                 json.dumps(brief, ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
             'final_pptx_sha256': result['final_sha256'], 'host_ui_rendered': False,
             'execution_owner': 'existing project-private photo_reconstruct.build_review',
             'user_delivery_ready': False}
    photo.write_json(workspace / 'analysis/request-entry.json', entry)
    photo.write_json(workspace / 'analysis/request-intake.json', report)
    photo.write_json(workspace / 'analysis/effective-task-brief.json', brief)
    (workspace / 'analysis/request-entry.log').write_text(progress.getvalue(), encoding='utf-8')
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('brief', type=Path)
    parser.add_argument('--request-text', required=True)
    parser.add_argument('--request-ref', help='actual current user-message reference for a direct copy command')
    parser.add_argument('--purpose-choice', choices=CHOICES)
    parser.add_argument('--purpose-confirmation-ref',
                        help='actual current menu selection or explicit request reference')
    parser.add_argument('--check-environment', action='store_true')
    parser.add_argument('--build-photo-review', type=Path)
    parser.add_argument('--workspace-parent', type=Path)
    parser.add_argument('--presentations-skill-dir', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    try:
        brief_bytes = args.brief.read_bytes()
        brief, origin = prepare_request(json.loads(brief_bytes), args.request_text, args.request_ref,
                                        args.purpose_choice, args.purpose_confirmation_ref)
        report = validate_brief(brief, args.brief.resolve().parent)
        report['request_entry'] = {**origin, 'execution_performed': False,
                                   'brief_input_sha256': hashlib.sha256(brief_bytes).hexdigest(),
                                   'request_text_sha256': hashlib.sha256(args.request_text.encode()).hexdigest()}
        if args.check_environment or args.build_photo_review:
            report['environment'] = check_environment(brief, args.brief.resolve().parent)
            if not report['environment']['ok']:
                report['ready_for_plan'] = False
        if args.build_photo_review:
            if not args.presentations_skill_dir:
                raise ValueError('Read the shared Presentations skill and provide its verified directory')
            parent = args.workspace_parent or Path(__file__).resolve().parents[4] / 'projects'
            report['photo_review'] = build_bound_review(brief, report, args.build_photo_review.resolve(),
                                                       parent, args.presentations_skill_dir,
                                                       report['request_entry'])
            report['request_entry']['execution_performed'] = True
        payload = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(payload, encoding='utf-8')
        print(payload, end='')
        return 0 if report['input_complete'] and report.get('environment', {}).get('ok', True) else 1
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print('Request entry blocked: ' + str(exc))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
