"""Bind native plan/output counts to the separate current task brief."""

from __future__ import annotations

import hashlib
from pathlib import Path

from .ooxml import _load_json


def validate_task_count(plan: dict, brief_path: Path | None, output_count: int | None = None) -> dict:
    """Check an external confirmed request; retain legacy briefs without a count."""
    requested = plan.get('requested_slide_count')
    if brief_path is not None and not brief_path.is_file():
        raise RuntimeError('Current task brief file missing; provide --design-brief')
    if brief_path is None:
        if requested is not None or plan.get('task_brief_sha256'):
            raise RuntimeError('Native requested count requires the separate current --design-brief')
        return {}
    brief = _load_json(brief_path)
    if brief.get('workflow_version') != 2 and 'slide_count' not in brief:
        if requested is not None:
            raise RuntimeError('Native requested count missing from separate task brief')
        return {}
    from presentation_brief import validate_brief
    from presentation_intake import validate_slide_count
    report = validate_brief(brief, brief_path.resolve().parent)
    if brief.get('mode') != 'custom' or not report['ready_for_plan']:
        raise RuntimeError('Native fill requires a complete confirmed custom task brief')
    errors = validate_slide_count(brief, len(plan.get('slides', [])), output_count)
    if requested is not None and requested != brief['slide_count']:
        errors.append('Plan requested count differs from separate current task brief')
    digest = hashlib.sha256(brief_path.read_bytes()).hexdigest()
    if plan.get('task_brief_sha256') and plan['task_brief_sha256'] != digest:
        errors.append('Native task brief changed since plan approval; review plan again')
    if errors:
        raise RuntimeError('; '.join(errors))
    return {'requested_slide_count': brief['slide_count'], 'design_brief_sha256': digest}
