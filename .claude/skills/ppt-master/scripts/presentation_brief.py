#!/usr/bin/env python3
"""Validate a per-task presentation brief; never writes company defaults.

Usage: python3 scripts/presentation_brief.py BRIEF.json [--output REPORT.json]
This is intake only. Existing template/preset/storyline/fill-plan gates remain.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import math
from pathlib import Path


def validate_brief(brief: dict, base: Path) -> dict:
    missing, errors = [], []
    mode = brief.get("mode")
    if brief.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if brief.get("scope") != "task":
        errors.append("scope must be task; global company defaults are not written")
    if mode not in {"builtin", "custom"}:
        missing.append("제작 모드: 기본 제공 템플릿 또는 사용자 정의")
    if not brief.get("content_text") and not brief.get("content_files"):
        missing.append("이번 작업의 내용 자료")
    def check_files(values, label):
        if not isinstance(values, list) or any(not isinstance(v, str) for v in values):
            errors.append(label + " must be a list of paths")
            return
        for raw in values:
            path = Path(raw)
            path = path if path.is_absolute() else base / path
            if not path.is_file():
                errors.append(label + " file missing: " + raw)
    check_files(brief.get("content_files", []), "content_files")
    if mode == "builtin":
        for key, label in [("template_id", "기본 템플릿 선택"),
                           ("production_preset_id", "제작 프리셋 선택")]:
            if not brief.get(key):
                missing.append(label)
        if brief.get("template_files") or brief.get("sample_files"):
            errors.append("Company source files belong to custom mode")
    if mode == "custom":
        templates = brief.get("template_files", [])
        if not templates:
            missing.append("원본 PPTX 템플릿")
        check_files(templates, "template_files")
        if isinstance(templates, list) and any(not str(p).lower().endswith(".pptx") for p in templates):
            errors.append("Custom native fill requires original PPTX, not a flattened image")
        samples = brief.get("sample_files", [])
        check_files(samples, "sample_files")
        if not samples and brief.get("sample_policy") != "not_provided":
            missing.append("참고 샘플 PPTX 또는 샘플 없음 확인")
        for key, label in [("font_policy", "글꼴 기준"), ("font_size_policy", "pt 크기 기준")]:
            policy = brief.get(key)
            if not isinstance(policy, dict) or policy.get("basis") not in {"source", "specified"}:
                missing.append(label + ": 원본 유지 또는 이번 작업 지정값")
            elif policy["basis"] == "specified":
                if not policy.get("values"):
                    missing.append(label + " 지정값")
                else:
                    values = policy["values"]
                    if not isinstance(values, dict):
                        errors.append(key + ".values must map roles to values")
                    elif key == "font_policy" and any(not isinstance(v, str) or not v.strip() for v in values.values()):
                        errors.append("font_policy values must be non-empty family names")
                    elif key == "font_size_policy" and any(type(v) not in (int, float)
                            or not math.isfinite(v) or v <= 0 for v in values.values()):
                        errors.append("font_size_policy values must be finite positive point sizes")
        if "writing_rules" in brief and (not isinstance(brief["writing_rules"], list)
                or any(not isinstance(v, str) or not v.strip() for v in brief["writing_rules"])):
            errors.append("writing_rules must be a list of non-empty strings")
        if not brief.get("writing_rules") and brief.get("writing_rules_policy") != "source":
            missing.append("PPT 작성 기준 또는 원본 기준 유지 확인")
        if brief.get("template_id") or brief.get("production_preset_id"):
            errors.append("Custom native fidelity does not silently impose a builtin template/preset")
    return {
        "schema_version": 1, "mode": mode, "scope": "task",
        "input_complete": not missing and not errors,
        "inputs_confirmed": brief.get("inputs_confirmed") is True,
        "ready_for_plan": not missing and not errors and brief.get("inputs_confirmed") is True,
        "ready_for_generation": False,
        "missing_required": missing, "errors": errors,
        "question": "이번 작업에서 다음 항목만 함께 확인해 주세요: " + "; ".join(missing) if missing else None,
        "rule_priority": ["explicit current-task user instructions", "confirmed task brief",
                          "original template and selected reference samples", "mode defaults"],
        "next_gate": "existing template/preset/storyline gates" if mode == "builtin"
                     else "review native slide mapping and confirm fill plan",
        "privacy": "User source files stay local/private; no public GitHub upload or external AI transfer is authorized",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("brief", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check-environment", action="store_true")
    args = parser.parse_args()
    try:
        brief = json.loads(args.brief.read_text(encoding="utf-8"))
        if not isinstance(brief, dict):
            raise ValueError("Brief must be an object")
        report = validate_brief(brief, args.brief.resolve().parent)
        if args.check_environment:
            report["environment"] = check_environment(brief, args.brief.resolve().parent)
        output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output, encoding="utf-8")
        print(output, end="")
        return 0 if report["input_complete"] and report.get("environment", {}).get("ok", True) else 1
    except (OSError, ValueError, TypeError) as exc:
        print("Brief validation failed: " + str(exc))
        return 1


def check_environment(brief: dict, base: Path) -> dict:
    # Reuse existing cloud preparation probes without running the SVG route's
    # main preflight/gates or imposing Pretendard on a company template.
    from preflight import check_core_deps, font_installed
    failures = check_core_deps()
    runtime = {}
    for key in ("CODEX_PRIMARY_RUNTIME_NODE", "CODEX_PRIMARY_RUNTIME_NODE_MODULES",
                "CODEX_PRIMARY_RUNTIME", "CODEX_PRIMARY_RUNTIME_PYTHON"):
        raw = os.environ.get(key, "")
        valid = bool(raw) and Path(raw).is_absolute() and Path(raw).exists()
        runtime[key] = valid
        if not valid:
            failures.append("Supplied runtime path unavailable: " + key)
    files = brief.get("font_files", [])
    if not isinstance(files, list) or not all(isinstance(p, str) for p in files):
        failures.append("font_files must be a list of project-relative paths")
        files = []
    available_files = []
    for raw in files:
        path = Path(raw) if Path(raw).is_absolute() else base / raw
        found = path.is_file()
        available_files.append({"path": raw, "available": found})
        if not found:
            failures.append("Declared font file missing: " + raw)
    families = brief.get("font_families", [])
    if not isinstance(families, list) or not all(isinstance(f, str) for f in families):
        failures.append("font_families must be a list of names")
        families = []
    installed = {f: font_installed(f) for f in families}
    if not files and (not families or any(found is not True for found in installed.values())):
        failures.append("Declare available font files or verify every required system family")
    return {"ok": not failures, "errors": failures, "supplied_runtime": runtime,
            "font_files": available_files, "system_font_families": installed,
            "font_render_verified": False, "officecli_available": shutil.which("officecli") is not None,
            "native_application_verified": False}


if __name__ == "__main__":
    raise SystemExit(main())
