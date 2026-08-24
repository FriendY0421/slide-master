#!/usr/bin/env python3
"""Fail-closed template-selection evidence for Slide Master projects."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from console_encoding import configure_utf8_stdio  # noqa: E402

configure_utf8_stdio()

GATE_VERSION = 1
GATE_FILENAME = "template_selection.json"
EXEMPT_REASONS = {
    "beautify-pptx",
    "ppt-template-fill",
    "native-enhance-pptx",
    "create-template",
    "resume-confirmed-project",
    "legacy-project",
}


def _read_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read template selection result: {path} ({exc})") from exc
    if not isinstance(data, dict):
        raise ValueError("template selection result must be a JSON object")
    return data


def validate_selection_record(data: dict) -> list[str]:
    errors: list[str] = []
    status = data.get("status", "selected")
    if status == "exempt":
        if data.get("exempt_reason") not in EXEMPT_REASONS:
            errors.append("unknown template gate exemption reason")
        if not data.get("recorded_at"):
            errors.append("missing exemption recorded_at timestamp")
        return errors
    if status != "selected":
        errors.append("template selection status must be 'selected' or 'exempt'")
        return errors
    choice = str(data.get("template") or "").strip()
    if not choice:
        errors.append("missing template id")
    if not data.get("selected_at"):
        errors.append("missing selected_at timestamp")
    if choice == "free":
        if data.get("workspace") not in (None, ""):
            errors.append("Free Design selection must not carry a template workspace")
    elif not str(data.get("workspace") or "").strip():
        errors.append("registered template selection must carry its workspace")
    return errors


def load_selection_result(path: str | Path) -> dict:
    data = _read_json(Path(path))
    errors = validate_selection_record(data)
    if errors:
        raise ValueError("; ".join(errors))
    record = dict(data)
    record["gate_version"] = GATE_VERSION
    record["status"] = "selected"
    return record


def make_exempt_record(reason: str) -> dict:
    if reason not in EXEMPT_REASONS:
        raise ValueError(f"unsupported template gate exemption: {reason}")
    return {
        "gate_version": GATE_VERSION,
        "status": "exempt",
        "exempt_reason": reason,
        "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }


def write_project_gate(project_path: str | Path, record: dict) -> Path:
    errors = validate_selection_record(record)
    if errors:
        raise ValueError("; ".join(errors))
    target = Path(project_path) / GATE_FILENAME
    payload = dict(record)
    payload["gate_version"] = GATE_VERSION
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, target)
    return target


def validate_project_gate(project_path: str | Path) -> list[str]:
    gate_path = Path(project_path) / GATE_FILENAME
    if not gate_path.is_file():
        return [f"missing {GATE_FILENAME} — template selection gate was not completed"]
    try:
        data = _read_json(gate_path)
    except ValueError as exc:
        return [str(exc)]
    return validate_selection_record(data)


def _print_errors(errors: list[str]) -> int:
    print("[template-gate] FAIL", file=sys.stderr)
    for error in errors:
        print(f"  - {error}", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if not args:
        print(
            "usage: template_gate.py validate <project_path> | "
            "record <project_path> <selection_result.json> | "
            "exempt <project_path> <reason>",
            file=sys.stderr,
        )
        return 2

    command = args[0]
    try:
        if command == "validate" and len(args) == 2:
            errors = validate_project_gate(args[1])
            if errors:
                return _print_errors(errors)
            print("[template-gate] PASS")
            return 0

        if command == "record" and len(args) == 3:
            record = load_selection_result(args[2])
            path = write_project_gate(args[1], record)
            print(f"[template-gate] RECORDED — {path}")
            return 0

        if command == "exempt" and len(args) == 3:
            record = make_exempt_record(args[2])
            path = write_project_gate(args[1], record)
            print(f"[template-gate] EXEMPT — {args[2]} — {path}")
            return 0
    except ValueError as exc:
        return _print_errors([str(exc)])

    print("invalid template_gate.py arguments", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
