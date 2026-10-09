#!/usr/bin/env python3
"""PPT Master - Private request revision and callback binding.

Usage: imported by presentation_request.py --state-file projects/private/state.json
Examples: use one private state file per host request; never reuse another thread's state
Dependencies: standard library only
See docs/ppt-project/PHOTO_REQUEST_ENTRY.md. This does not authenticate host events.
"""
from __future__ import annotations

import contextlib
import copy
import hashlib
import json
import os
from pathlib import Path
from collections.abc import Iterator

PURPOSE_FIELDS = ('purpose_choice', 'purpose_confirmed', 'purpose_confirmation_ref')


def digest_json(value: object) -> str:
    """Hash canonical request data without changing its literal values."""
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def input_context(brief: dict, base: Path, request_ref: str) -> str:
    """Bind the request identity, settings, attached bytes and observation bytes."""
    current = copy.deepcopy(brief)
    for key in (*PURPOSE_FIELDS, 'request_text', 'purpose_menu_required'):
        current.pop(key, None)
    files = []
    for key in ('template_files', 'sample_files', 'reference_files', 'content_files'):
        files.extend(current.get(key, []) if isinstance(current.get(key, []), list) else [])
    review = current.get('reference_review', {})
    if isinstance(review, dict):
        files.extend(item['observations_file'] for item in review.values()
                     if isinstance(item, dict) and isinstance(item.get('observations_file'), str))
    hashes = {}
    for raw in files:
        if isinstance(raw, str):
            path = Path(raw)
            path = (path if path.is_absolute() else base / path).resolve()
            hashes[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    return digest_json({'brief': current, 'files': hashes, 'request_ref': request_ref})


@contextlib.contextmanager
def locked_state(path: Path, private_root: Path) -> Iterator[dict]:
    """Lock one private session; concurrent callbacks must retry through the host."""
    path = path.resolve()
    if not path.is_relative_to(private_root.resolve()):
        raise ValueError('Request state must stay in gitignored repository projects/')
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_name(path.name + '.lock')
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise ValueError('Request is already processing; retry after its result, do not submit another build') from exc
    os.close(fd)
    try:
        state = json.loads(path.read_text()) if path.exists() else {'schema_version': 1, 'revision': 0}
        if (not isinstance(state, dict) or type(state.get('schema_version')) is not int
                or state.get('schema_version') != 1
                or type(state.get('revision')) is not int or state['revision'] < 0):
            raise ValueError('Invalid request state; preserve it and use a new private request state')
        yield state
        temporary = path.with_name(path.name + '.tmp')
        temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
        temporary.replace(path)
    finally:
        lock.unlink()


def apply_session(state: dict, prepared: dict, origin: dict, raw_brief: dict, base: Path,
                  request_ref: str | None, choice: str | None, token: str | None, cancel: bool) -> None:
    """Reset changed input revisions; reject stale callbacks before selection."""
    if not isinstance(request_ref, str) or not request_ref.strip():
        raise ValueError('Stateful requests require the actual request reference')
    context = input_context(raw_brief, base, request_ref)
    if choice is not None or (cancel and state.get('input_context_sha256') is not None):
        # A callback belongs to the currently stored revision, never to an
        # older brief that would reset the session before its token is checked.
        current_token = digest_json({'context': state.get('input_context_sha256'),
                                     'revision': state['revision']})
        if (context != state.get('input_context_sha256')
                or ((choice is not None or token is not None) and token != current_token)):
            raise ValueError('Stale or missing selection context; '
                             'preserve the current selection and use the latest session token')
    # Validate and prepare changes off to the side; rejection must be a no-op
    # even for API callers that do not use the file transaction.
    stored = state
    state = copy.deepcopy(stored)
    if state.get('input_context_sha256') != context:
        revision = state['revision'] + 1
        state.clear()
        state.update(schema_version=1, revision=revision, input_context_sha256=context,
                     request_ref=request_ref, cancelled=False)
    if cancel:
        if choice is not None:
            raise ValueError('Cancellation and a new purpose selection cannot be combined')
        state['revision'] += 1
        state['cancelled'] = True
        state.pop('selection', None)
        state.pop('execution', None)
    if choice is not None:
        state['cancelled'] = False
        state['revision'] += 1
    if state.get('cancelled'):
        for key in PURPOSE_FIELDS:
            prepared.pop(key, None)
        origin['purpose_origin'] = 'cancelled'
    elif choice is None and state.get('selection'):
        prepared.update(state['selection'])
        origin['purpose_origin'] = 'bound_session'
    elif prepared.get('purpose_confirmed') is True:
        state['selection'] = {key: prepared[key] for key in PURPOSE_FIELDS}
    selection_token = digest_json({'context': context, 'revision': state['revision']})
    origin.update(input_context_sha256=context, selection_context_sha256=selection_token,
                  state_revision=state['revision'], cancelled=state.get('cancelled', False))
    stored.clear()
    stored.update(state)
