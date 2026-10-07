"""Bind native plan/output counts to the separate current task brief."""

from __future__ import annotations

import hashlib
from pathlib import Path

from .ooxml import _load_json


def validate_task_count(plan: dict, brief_path: Path | None, output_count: int | None = None) -> dict:
    """Require a current approved brief/count/hash; absence never implies resume."""
    requested = plan.get('requested_slide_count')
    if brief_path is None or not brief_path.is_file():
        raise RuntimeError('Current task brief file missing; provide --design-brief')
    brief = _load_json(brief_path)
    if not isinstance(brief, dict) or brief.get('workflow_version') != 2:
        raise RuntimeError('Native creation/resume requires a current workflow_version 2 task brief')
    if plan.get('status') != 'confirmed':
        raise RuntimeError('Native task binding requires a confirmed fill plan')
    from presentation_brief import validate_brief
    from presentation_intake import validate_slide_count
    report = validate_brief(brief, brief_path.resolve().parent)
    if brief.get('mode') != 'custom' or not report['ready_for_plan']:
        raise RuntimeError('Native fill requires a complete confirmed custom task brief')
    errors = validate_slide_count(brief, len(plan.get('slides', [])), output_count)
    if type(requested) is not int or requested <= 0 or requested != brief['slide_count']:
        errors.append('Plan requested count differs from separate current task brief')
    digest = hashlib.sha256(brief_path.read_bytes()).hexdigest()
    if plan.get('task_brief_sha256') != digest:
        errors.append('Native task brief hash missing or changed since approval; bind current brief and review plan')
    if errors:
        raise RuntimeError('; '.join(errors))
    return {'requested_slide_count': brief['slide_count'], 'design_brief_sha256': digest}
