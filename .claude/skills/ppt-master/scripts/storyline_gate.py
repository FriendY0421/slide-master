#!/usr/bin/env python3
"""Fail-closed approval evidence for the user-reviewed slide-by-slide storyline."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from pathlib import Path

GATE_VERSION = 1
GATE_FILENAME = "storyline_approval.json"


def _read_json(path: str | Path) -> dict:
    p = Path(path)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read storyline JSON: {p} ({exc})") from exc
    if not isinstance(data, dict):
        raise ValueError("storyline JSON must be an object")
    return data


def _canonical_storyline(data: dict) -> bytes:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _storyline_hash(data: dict) -> str:
    return hashlib.sha256(_canonical_storyline(data)).hexdigest()


def validate_storyline(data: dict) -> list[str]:
    errors: list[str] = []
    slides = data.get("slides")
    if not isinstance(slides, list) or not slides:
        return ["storyline requires a non-empty slides array"]
    for idx, slide in enumerate(slides, 1):
        if not isinstance(slide, dict):
            errors.append(f"slide {idx} must be an object")
            continue
        if not str(slide.get("title") or "").strip():
            errors.append(f"slide {idx} missing title")
        if not str(slide.get("core_message") or "").strip():
            errors.append(f"slide {idx} missing core_message")
        points = slide.get("content_points")
        if points is not None and not isinstance(points, list):
            errors.append(f"slide {idx} content_points must be an array")
    return errors


def make_approval(storyline: dict, approval_note: str = "") -> dict:
    errors = validate_storyline(storyline)
    if errors:
        raise ValueError("; ".join(errors))
    return {
        "gate_version": GATE_VERSION,
        "status": "approved",
        "approved_by": "user",
        "approved_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "approval_note": approval_note,
        "slide_count": len(storyline["slides"]),
        "storyline_sha256": _storyline_hash(storyline),
        "storyline": storyline,
    }


def validate_approval(data: dict) -> list[str]:
    errors: list[str] = []
    if data.get("status") != "approved":
        errors.append("storyline approval status must be approved")
    if data.get("approved_by") != "user":
        errors.append("storyline must be explicitly approved by the user")
    if not data.get("approved_at"):
        errors.append("missing approved_at timestamp")
    storyline = data.get("storyline")
    if not isinstance(storyline, dict):
        errors.append("missing approved storyline snapshot")
        return errors
    errors.extend(validate_storyline(storyline))
    expected = str(data.get("storyline_sha256") or "")
    actual = _storyline_hash(storyline)
    if expected != actual:
        errors.append("storyline snapshot hash mismatch")
    if data.get("slide_count") != len(storyline.get("slides", [])):
        errors.append("slide_count does not match approved storyline")
    return errors


def load_storyline_approval(path: str | Path) -> dict:
    data = _read_json(path)
    errors = validate_approval(data)
    if errors:
        raise ValueError("; ".join(errors))
    return data


def write_project_gate(project_path: str | Path, approval: dict) -> Path:
    errors = validate_approval(approval)
    if errors:
        raise ValueError("; ".join(errors))
    target = Path(project_path) / GATE_FILENAME
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(json.dumps(approval, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, target)
    return target



def project_requires_storyline_gate(project_path: str | Path) -> bool:
    """Require the new gate only for current gate-v3 selected new-deck projects."""
    selection = Path(project_path) / "template_selection.json"
    if not selection.is_file():
        return False
    try:
        data = json.loads(selection.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(data, dict) or data.get("status", "selected") != "selected":
        return False
    try:
        version = int(data.get("gate_version", 1))
    except (TypeError, ValueError):
        version = 1
    return version >= 3

def validate_project_gate(project_path: str | Path) -> list[str]:
    path = Path(project_path) / GATE_FILENAME
    if not path.is_file():
        return [f"missing {GATE_FILENAME} — slide-by-slide storyline was not approved"]
    try:
        return validate_approval(_read_json(path))
    except ValueError as exc:
        return [str(exc)]


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    approve = sub.add_parser("approve")
    approve.add_argument("storyline_json")
    approve.add_argument("--output", required=True)
    approve.add_argument("--approved-by-user", action="store_true", required=True)
    approve.add_argument("--note", default="")
    validate = sub.add_parser("validate")
    validate.add_argument("approval_json")
    args = parser.parse_args()
    try:
        if args.command == "approve":
            approval = make_approval(_read_json(args.storyline_json), args.note)
            Path(args.output).write_text(json.dumps(approval, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"STORYLINE_APPROVAL={args.output}")
            return 0
        load_storyline_approval(args.approval_json)
        print("[storyline-gate] PASS")
        return 0
    except ValueError as exc:
        print(f"[storyline-gate] FAIL — {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
