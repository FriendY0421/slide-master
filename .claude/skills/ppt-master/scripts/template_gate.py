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
from picker_surface_gate import validate_picker_evidence  # noqa: E402

configure_utf8_stdio()

GATE_VERSION = 3
REPO_ROOT = Path(__file__).resolve().parents[4]
PRESETS_PATH = REPO_ROOT / "docs" / "gpts" / "PRODUCTION_PRESETS.json"
GATE_FILENAME = "template_selection.json"
EXEMPT_REASONS = {
    "beautify-pptx",
    "ppt-template-fill",
    "native-enhance-pptx",
    "create-template",
    "resume-confirmed-project",
    "legacy-project",
}


def _valid_preset_ids() -> set[str]:
    try:
        doc = json.loads(PRESETS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    presets = doc.get("presets", []) if isinstance(doc, dict) else []
    return {str(item.get("id") or "").strip() for item in presets if isinstance(item, dict) and item.get("id")}


def _read_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read template selection result: {path} ({exc})") from exc
    if not isinstance(data, dict):
        raise ValueError("template selection result must be a JSON object")
    return data


def _record_version(data: dict) -> int:
    try:
        return int(data.get("gate_version", 1))
    except (TypeError, ValueError):
        return 1


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

    # Gate v1/v2 records remain valid for legacy/resume compatibility.
    if _record_version(data) >= 3:
        preset = str(data.get("production_preset") or "").strip()
        if not preset:
            errors.append("gate v3 selection requires production_preset")
        else:
            valid_presets = _valid_preset_ids()
            if valid_presets and preset not in valid_presets:
                errors.append(f"unknown production_preset: {preset}")

    if _record_version(data) >= 2:
        surface = str(data.get("selection_surface") or "").strip()
        if not surface:
            errors.append("gate v2 selection requires selection_surface")
        elif surface == "direct_user_specified_template":
            if data.get("selection_method") != "direct_user_specified_template":
                errors.append(
                    "direct template selection requires direct_user_specified_template method"
                )
        else:
            picker = data.get("picker_evidence")
            if not isinstance(picker, dict):
                errors.append("gate v2 recommendation selection requires picker_evidence")
            else:
                picker_errors = validate_picker_evidence(picker)
                errors.extend(f"picker: {err}" for err in picker_errors)
                if picker.get("surface") != surface:
                    errors.append("selection_surface does not match picker evidence surface")
    return errors


def load_selection_result(path: str | Path) -> dict:
    data = _read_json(Path(path))
    errors = validate_selection_record(data)
    if errors:
        raise ValueError("; ".join(errors))
    record = dict(data)
    record["gate_version"] = _record_version(data)
    record["status"] = data.get("status", "selected")
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
    payload["gate_version"] = (
        _record_version(record)
        if record.get("status", "selected") == "selected"
        else GATE_VERSION
    )
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
