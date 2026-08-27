#!/usr/bin/env python3
"""Create and validate evidence that the template picker was visibly rendered."""

from __future__ import annotations

import argparse
import json
import os
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
EVIDENCE_VERSION = 1


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
    errors = validate_picker_evidence(data)
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
