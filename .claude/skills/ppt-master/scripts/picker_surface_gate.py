#!/usr/bin/env python3
"""Create and validate evidence that the template picker was visibly rendered."""

from __future__ import annotations

import argparse
import json
import hashlib
import os
import re
import sys
import time
from pathlib import Path

SURFACES = {
    "app_block",
    "genui",
    "conversation_native_visual",
    "inline_html",
    "github_visual_catalog",
    "text_last_resort",
}
PRIMARY_SURFACES = {"app_block", "genui"}
EVIDENCE_VERSION = 2


def validate_picker_binding(data: dict, choice: str, preset: str, source_commit: str | None) -> list[str]:
    """Bind a new selection to the shown manifest and explicit final pair."""
    errors = []
    if source_commit is not None and (
            not isinstance(source_commit, str) or not re.fullmatch(r'[0-9a-f]{40}', source_commit)):
        return ['picker requires an immutable catalog commit']
    if data.get('picker_evidence_version') != EVIDENCE_VERSION:
        errors.append('new recommendation requires bound picker evidence v2')
    manifest = data.get('manifest')
    if not isinstance(manifest, dict):
        return errors + ['missing displayed catalog manifest']
    digest = hashlib.sha256(json.dumps(manifest, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    if digest != data.get('manifest_sha256'):
        errors.append('displayed manifest hash mismatch')
    if data.get('source_commit') != source_commit or manifest.get('source_commit') != source_commit:
        errors.append('picker/catalog commit mismatch')
    if source_commit and data.get('source_ref') != 'github:' + source_commit:
        errors.append('picker source_ref is not the pinned catalog commit')
    keys = set()
    for field in ('all_templates', 'shortlist'):
        entries = manifest.get(field, [])
        if not isinstance(entries, list) or any(
                not isinstance(entry, dict) or not isinstance(entry.get('key'), str) for entry in entries):
            errors.append('invalid displayed manifest candidates')
            continue
        keys.update(entry['key'] for entry in entries)
    free = manifest.get('free_design', {})
    if isinstance(free, dict) and free.get('key') == 'free':
        keys.add('free')
    displayed = data.get('displayed_candidate_keys', [])
    if not isinstance(displayed, list) or any(not isinstance(key, str) or key not in keys for key in displayed):
        errors.append('displayed candidates differ from manifest')
        displayed = []
    if len(set(displayed)) != len(displayed) or len(displayed) != data.get('candidate_count'):
        errors.append('displayed candidate count mismatch')
    if choice not in displayed:
        errors.append('final template was not among displayed candidates')
    if data.get('selected_template') != choice or data.get('selected_preset') != preset or data.get('confirmed') is not True:
        errors.append('picker final confirmed pair differs from selection')
    return errors


def validate_picker_evidence(data: dict) -> list[str]:
    errors: list[str] = []
    if data.get("status") != "rendered":
        errors.append("picker status must be 'rendered'")
    surface = str(data.get("surface") or "").strip()
    if surface not in SURFACES:
        errors.append("unknown picker surface")
    if not data.get("rendered_at"):
        errors.append("missing picker rendered_at timestamp")
    if not str(data.get("source_ref") or "").strip():
        errors.append("missing picker source_ref")
    try:
        count = int(data.get("candidate_count", 0))
    except (TypeError, ValueError):
        count = 0
    if count < 1:
        errors.append("picker candidate_count must be >= 1")
    if surface and surface not in PRIMARY_SURFACES:
        if not str(data.get("fallback_reason") or "").strip():
            errors.append("non-primary picker surface requires fallback_reason")
    if data.get('picker_evidence_version') == 2:
        errors.extend(validate_picker_binding(data, data.get('selected_template', ''),
                                              data.get('selected_preset', ''), data.get('source_commit')))
    return errors


def load_picker_evidence(path: str | Path) -> dict:
    p = Path(path)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read picker evidence: {p} ({exc})") from exc
    if not isinstance(data, dict):
        raise ValueError("picker evidence must be a JSON object")
    errors = validate_picker_evidence(data)
    if errors:
        raise ValueError("; ".join(errors))
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Record/validate visible template-picker evidence.")
    sub = parser.add_subparsers(dest="command", required=True)

    record = sub.add_parser("record")
    record.add_argument("output", type=Path)
    record.add_argument("--surface", choices=sorted(SURFACES), required=True)
    record.add_argument("--purpose", default="")
    record.add_argument("--source-ref", required=True)
    record.add_argument("--candidate-count", type=int, required=True)
    record.add_argument("--detail-preview-max", type=int, default=6)
    record.add_argument("--fallback-reason", default="")
    record.add_argument("--rendered", action="store_true")
    record.add_argument('--manifest', type=Path, required=True)
    record.add_argument('--candidate-keys', required=True, help='comma-separated actually displayed keys')
    record.add_argument('--selected-template', required=True)
    record.add_argument('--selected-preset', required=True)
    record.add_argument('--confirmed', action='store_true')

    validate = sub.add_parser("validate")
    validate.add_argument("input", type=Path)

    args = parser.parse_args(argv)

    if args.command == "validate":
        try:
            data = load_picker_evidence(args.input)
        except ValueError as exc:
            print(f"[picker-surface-gate] FAIL — {exc}", file=sys.stderr)
            return 1
        print("[picker-surface-gate] PASS")
        print("PICKER_EVIDENCE=" + json.dumps(data, ensure_ascii=False))
        return 0

    if not args.rendered:
        print(
            "[picker-surface-gate] FAIL — pass --rendered only after the surface was visibly produced",
            file=sys.stderr,
        )
        return 2

    data = {
        "picker_evidence_version": EVIDENCE_VERSION,
        "status": "rendered",
        "surface": args.surface,
        "purpose": args.purpose,
        "source_ref": args.source_ref,
        "candidate_count": args.candidate_count,
        "detail_preview_max": max(1, args.detail_preview_max),
        "fallback_reason": args.fallback_reason or None,
        "rendered_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    try:
        manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
        data.update({'manifest': manifest,
                     'manifest_sha256': hashlib.sha256(json.dumps(
                         manifest, sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
                     'source_commit': manifest.get('source_commit'),
                     'displayed_candidate_keys': args.candidate_keys.split(','),
                     'selected_template': args.selected_template,
                     'selected_preset': args.selected_preset, 'confirmed': args.confirmed})
    except (OSError, ValueError, AttributeError) as exc:
        print(f'[picker-surface-gate] FAIL — invalid manifest: {exc}', file=sys.stderr)
        return 2
    errors = validate_picker_evidence(data)
    errors.extend(validate_picker_binding(data, args.selected_template, args.selected_preset, data['source_commit']))
    if errors:
        print("[picker-surface-gate] FAIL", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    tmp = args.output.with_suffix(args.output.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, args.output)
    print(f"PICKER_EVIDENCE_FILE={args.output}")
    print("PICKER_EVIDENCE=" + json.dumps(data, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
