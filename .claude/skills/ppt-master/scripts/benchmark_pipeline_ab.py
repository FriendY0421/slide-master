#!/usr/bin/env python3
"""
PPT Master - Pipeline A/B Benchmark

Run deterministic paired subprocess benchmarks from a strict JSON plan. The
harness requires clean committed arms, verifies source/fixture identity around
every pair, discards warmups, balances first-arm order, preserves every
measured pair, and applies pre-registered quality plus CI/MCID decisions.

Usage:
    python3 scripts/benchmark_pipeline_ab.py <plan.json> --control-repo PATH \
        --treatment-repo PATH --fixture PATH --output report.json [options]

Examples:
    python3 scripts/benchmark_pipeline_ab.py benchmark_plan.json \
        --control-repo ../baseline --treatment-repo . --fixture projects/demo \
        --output artifacts/pipeline_ab.json --pairs 10

Dependencies:
    PPT Master local helpers plus the Python standard library
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import random
import re
import shutil
import socket
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Optional

import run_telemetry
from console_encoding import configure_utf8_stdio
from run_telemetry import TelemetryError, hash_path

SCHEMA_VERSION = 1
CACHE_CONDITIONS = {"none", "cold", "miss", "hit"}
CACHE_SCOPES = {"project", "cache-dir"}
QUALITY_MODES = {"non-artifact", "equivalent"}
METRIC_KINDS = {"duration_ms", "stdout_number"}
DIRECTIONS = {"lower", "higher"}
DECISION_KINDS = {"superiority", "noninferiority"}
ORDER_PATTERN = (
    ("control", "treatment"),
    ("treatment", "control"),
    ("treatment", "control"),
    ("control", "treatment"),
    ("treatment", "control"),
    ("control", "treatment"),
    ("control", "treatment"),
    ("treatment", "control"),
)
TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
NUMBER_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")
TAIL_BYTES = 2048


class BenchmarkError(ValueError):
    """Report an invalid benchmark plan or execution prerequisite."""


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _is_within(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _validate_output_location(
    output: Path,
    plan: Path,
    fixture: Path,
    repos: dict[str, Path],
    harness: Path,
    telemetry: Path,
) -> None:
    protected_files = {
        "benchmark plan": plan,
        "benchmark harness": harness,
        "run_telemetry dependency": telemetry,
    }
    for label, path in protected_files.items():
        if output == path:
            raise BenchmarkError(f"output must not overwrite the {label}")
    protected = {"fixture": fixture, **{f"{arm} repo": repo for arm, repo in repos.items()}}
    for label, root in protected.items():
        if _is_within(output, root):
            raise BenchmarkError(f"output must be outside the {label}: {root}")


def _git(repo: Path, *args: str) -> bytes:
    command = ["git", "-C", str(repo), *args]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise BenchmarkError(f"git command failed ({' '.join(command)}): {detail}")
    return result.stdout


def source_identity(repo: Path) -> dict[str, object]:
    """Return a fast identity for a clean committed worktree."""
    root = repo.resolve()
    if not root.is_dir():
        raise BenchmarkError(f"repository is not a directory: {repo}")
    commit = _git(root, "rev-parse", "HEAD").decode("ascii", errors="strict").strip()
    tree = _git(root, "rev-parse", "HEAD^{tree}").decode("ascii", errors="strict").strip()
    status = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if status.strip():
        detail = status.decode("utf-8", errors="replace").strip().splitlines()
        preview = "; ".join(detail[:5])
        raise BenchmarkError(f"benchmark arm must be a clean committed worktree: {root} ({preview})")
    return {
        "root": str(root),
        "git_commit": commit,
        "git_tree": tree,
        "git_clean": True,
        "git_status_sha256": _sha256_bytes(status),
        "source_sha256": _sha256_bytes(f"{commit}\0{tree}".encode("ascii")),
    }


def _validate_argv(value: object, location: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise BenchmarkError(f"{location} must be a non-empty argv array")
    if not all(isinstance(item, str) and item for item in value):
        raise BenchmarkError(f"{location} entries must be non-empty strings")
    return value


def _validate_hooks(value: object, location: str) -> list[dict[str, object]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise BenchmarkError(f"{location} must be an array")
    hooks: list[dict[str, object]] = []
    for index, raw_hook in enumerate(value):
        if not isinstance(raw_hook, dict) or set(raw_hook) != {"name", "command"}:
            raise BenchmarkError(f"{location}[{index}] requires only name and command")
        name = raw_hook["name"]
        if not isinstance(name, str) or not TOKEN_RE.fullmatch(name):
            raise BenchmarkError(f"{location}[{index}].name is invalid")
        hooks.append({"name": name, "command": _validate_argv(raw_hook["command"], location)})
    return hooks


def _validate_metric(value: object, location: str) -> dict[str, str]:
    if value is None:
        return {"kind": "duration_ms", "name": "duration_ms", "unit": "ms"}
    if not isinstance(value, dict) or set(value) != {"kind", "name", "unit"}:
        raise BenchmarkError(f"{location} requires exactly kind, name, and unit")
    kind = value["kind"]
    if kind not in METRIC_KINDS:
        raise BenchmarkError(f"{location}.kind must be one of {sorted(METRIC_KINDS)}")
    for key in ("name", "unit"):
        if not isinstance(value[key], str) or not TOKEN_RE.fullmatch(value[key]):
            raise BenchmarkError(f"{location}.{key} is invalid")
    return {"kind": kind, "name": value["name"], "unit": value["unit"]}


def _validate_decision(value: object, location: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise BenchmarkError(f"{location} must be an object")
    kind = value.get("kind")
    if kind not in DECISION_KINDS:
        raise BenchmarkError(f"{location}.kind must be one of {sorted(DECISION_KINDS)}")
    threshold_keys = {
        "superiority": ("relative_mcid", "absolute_mcid"),
        "noninferiority": ("max_relative_regression", "max_absolute_regression"),
    }
    relative_key, absolute_key = threshold_keys[kind]
    required = {"kind", "direction", relative_key, absolute_key}
    if set(value) != required:
        raise BenchmarkError(f"{location} requires exactly {sorted(required)} for {kind}")
    direction = value["direction"]
    if direction not in DIRECTIONS:
        raise BenchmarkError(f"{location}.direction must be one of {sorted(DIRECTIONS)}")
    relative = value[relative_key]
    absolute = value[absolute_key]
    for key, number in ((relative_key, relative), (absolute_key, absolute)):
        valid_number = isinstance(number, (int, float)) and not isinstance(number, bool)
        if not valid_number or not math.isfinite(number) or number < 0:
            raise BenchmarkError(f"{location}.{key} must be a finite non-negative number")
    if relative == 0 and absolute == 0:
        raise BenchmarkError(f"{location} must pre-register at least one positive threshold")
    decision = {
        "kind": kind,
        "direction": direction,
        relative_key: float(relative),
        absolute_key: float(absolute),
    }
    if kind == "superiority":
        decision["ci_rule"] = "both 95% CI lower bounds must meet their MCIDs"
    else:
        decision["ci_rule"] = (
            "both 95% CI lower bounds must be at least the negative allowed regressions"
        )
    return decision


def load_plan(path: Path) -> tuple[dict[str, object], str]:
    """Load and validate the strict benchmark plan."""
    raw = path.read_bytes()
    try:
        plan = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BenchmarkError(f"invalid UTF-8 JSON plan: {exc}") from exc
    if not isinstance(plan, dict) or set(plan) != {"schema_version", "cases"}:
        raise BenchmarkError("plan requires exactly schema_version and cases")
    if plan["schema_version"] != SCHEMA_VERSION:
        raise BenchmarkError(f"unsupported plan schema_version: {plan['schema_version']!r}")
    if not isinstance(plan["cases"], list) or not plan["cases"]:
        raise BenchmarkError("plan.cases must be a non-empty array")

    cases: list[dict[str, object]] = []
    case_ids: set[str] = set()
    allowed = {
        "id",
        "stage",
        "cache_condition",
        "cache_scope",
        "quality_mode",
        "metric",
        "decision",
        "prepare",
        "control_prepare",
        "treatment_prepare",
        "command",
        "control_command",
        "treatment_command",
        "guards",
        "pair_guards",
    }
    for index, raw_case in enumerate(plan["cases"]):
        if not isinstance(raw_case, dict):
            raise BenchmarkError(f"cases[{index}] must be an object")
        extra = set(raw_case) - allowed
        missing = {"id", "stage", "cache_condition", "quality_mode", "decision", "command"} - set(raw_case)
        if extra or missing:
            raise BenchmarkError(f"invalid cases[{index}] keys; missing={sorted(missing)}, extra={sorted(extra)}")
        case_id = raw_case["id"]
        stage = raw_case["stage"]
        condition = raw_case["cache_condition"]
        cache_scope = raw_case.get("cache_scope")
        quality_mode = raw_case["quality_mode"]
        if not isinstance(case_id, str) or not TOKEN_RE.fullmatch(case_id):
            raise BenchmarkError(f"cases[{index}].id is invalid")
        if case_id in case_ids:
            raise BenchmarkError(f"duplicate case id: {case_id}")
        case_ids.add(case_id)
        if not isinstance(stage, str) or not TOKEN_RE.fullmatch(stage):
            raise BenchmarkError(f"cases[{index}].stage is invalid")
        if condition not in CACHE_CONDITIONS:
            raise BenchmarkError(f"cases[{index}].cache_condition must be one of {sorted(CACHE_CONDITIONS)}")
        if condition == "hit":
            if cache_scope not in CACHE_SCOPES:
                raise BenchmarkError(
                    f"cases[{index}].cache_scope must be one of {sorted(CACHE_SCOPES)} "
                    "when cache_condition=hit"
                )
        elif "cache_scope" in raw_case:
            raise BenchmarkError(
                f"cases[{index}].cache_scope is allowed only when cache_condition=hit"
            )
        if quality_mode not in QUALITY_MODES:
            raise BenchmarkError(f"cases[{index}].quality_mode must be one of {sorted(QUALITY_MODES)}")
        raw_prepare = raw_case.get("prepare", [])
        if not isinstance(raw_prepare, list):
            raise BenchmarkError(f"cases[{index}].prepare must be an array of argv arrays")
        prepare = [_validate_argv(command, f"cases[{index}].prepare") for command in raw_prepare]
        arm_prepares: dict[str, list[list[str]]] = {}
        for arm in ("control", "treatment"):
            raw_arm_prepare = raw_case.get(f"{arm}_prepare", [])
            if not isinstance(raw_arm_prepare, list):
                raise BenchmarkError(f"cases[{index}].{arm}_prepare must be an array of argv arrays")
            arm_prepares[arm] = [
                _validate_argv(command, f"cases[{index}].{arm}_prepare")
                for command in raw_arm_prepare
            ]
            if condition == "hit":
                effective_prepare = [*prepare, *arm_prepares[arm]]
                if not effective_prepare:
                    raise BenchmarkError(
                        f"cases[{index}] cache_condition=hit requires prepare for the {arm} arm"
                    )
                scope_placeholder = (
                    "{project}" if cache_scope == "project" else "{cache_dir}"
                )
                if not any(
                    scope_placeholder in argument
                    for command in effective_prepare
                    for argument in command
                ):
                    raise BenchmarkError(
                        f"cases[{index}] cache_condition=hit prepare for the {arm} arm "
                        f"must reference {scope_placeholder} for cache_scope={cache_scope}"
                    )
        pair_guards = _validate_hooks(raw_case.get("pair_guards"), f"cases[{index}].pair_guards")
        if quality_mode == "equivalent" and not pair_guards:
            raise BenchmarkError(f"cases[{index}] quality_mode=equivalent requires at least one pair_guard")
        arm_commands = {
            arm: _validate_argv(
                raw_case.get(f"{arm}_command", raw_case["command"]),
                f"cases[{index}].{arm}_command",
            )
            for arm in ("control", "treatment")
        }
        if condition == "hit":
            scope_placeholder = "{project}" if cache_scope == "project" else "{cache_dir}"
            for arm in ("control", "treatment"):
                if not any(scope_placeholder in argument for argument in arm_commands[arm]):
                    raise BenchmarkError(
                        f"cases[{index}] cache_condition=hit timed command for the {arm} arm "
                        f"must reference {scope_placeholder} for cache_scope={cache_scope}"
                    )
        cases.append(
            {
                "id": case_id,
                "stage": stage,
                "cache_condition": condition,
                "cache_scope": cache_scope,
                "quality_mode": quality_mode,
                "metric": _validate_metric(raw_case.get("metric"), f"cases[{index}].metric"),
                "decision": _validate_decision(raw_case["decision"], f"cases[{index}].decision"),
                "prepare": prepare,
                "control_prepare": arm_prepares["control"],
                "treatment_prepare": arm_prepares["treatment"],
                "command": _validate_argv(raw_case["command"], f"cases[{index}].command"),
                "control_command": arm_commands["control"],
                "treatment_command": arm_commands["treatment"],
                "guards": _validate_hooks(raw_case.get("guards"), f"cases[{index}].guards"),
                "pair_guards": pair_guards,
            }
        )
    return {"schema_version": SCHEMA_VERSION, "cases": cases}, _sha256_bytes(raw)


def _expand(argv: list[str], values: dict[str, str]) -> list[str]:
    expanded: list[str] = []
    for argument in argv:
        for key, value in values.items():
            argument = argument.replace("{" + key + "}", value)
        expanded.append(argument)
    return expanded


def _as_bytes(value: bytes | str | None) -> bytes:
    if value is None:
        return b""
    return value if isinstance(value, bytes) else value.encode("utf-8", errors="replace")


def _command_result(
    argv: list[str],
    cwd: Path,
    timeout: float,
    metric: dict[str, str] | None = None,
) -> dict[str, object]:
    started = time.perf_counter_ns()
    try:
        completed = subprocess.run(
            argv,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        elapsed_ns = time.perf_counter_ns() - started
        stdout = completed.stdout
        stderr = completed.stderr
        returncode: int | None = completed.returncode
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        elapsed_ns = time.perf_counter_ns() - started
        stdout = _as_bytes(exc.stdout)
        stderr = _as_bytes(exc.stderr)
        returncode = None
        timed_out = True
    result: dict[str, object] = {
        "argv": argv,
        "returncode": returncode,
        "timed_out": timed_out,
        "elapsed_ns": elapsed_ns,
        "stdout_bytes": len(stdout),
        "stderr_bytes": len(stderr),
        "stdout_sha256": _sha256_bytes(stdout),
        "stderr_sha256": _sha256_bytes(stderr),
    }
    if timed_out or returncode != 0:
        result["stdout_tail"] = stdout[-TAIL_BYTES:].decode("utf-8", errors="replace")
        result["stderr_tail"] = stderr[-TAIL_BYTES:].decode("utf-8", errors="replace")
    if metric is not None and not timed_out and returncode == 0:
        if metric["kind"] == "duration_ms":
            result["metric_value"] = elapsed_ns / 1_000_000
        else:
            try:
                token = stdout.decode("utf-8", errors="strict").strip()
            except UnicodeDecodeError:
                token = ""
            if not NUMBER_RE.fullmatch(token):
                result["metric_error"] = "stdout_number requires stdout to contain exactly one finite number"
            else:
                value = float(token)
                if not math.isfinite(value) or value < 0:
                    result["metric_error"] = "stdout_number must be finite and non-negative"
                else:
                    result["metric_value"] = value
    return result


def _succeeded(result: dict[str, object] | None) -> bool:
    return (
        bool(result)
        and not result["timed_out"]
        and result["returncode"] == 0
        and "metric_error" not in result
    )


def _run_arm(
    arm: str,
    repo: Path,
    case: dict[str, object],
    values: dict[str, str],
    python: str,
    timeout: float,
) -> dict[str, object]:
    prepare_commands = [*case["prepare"], *case[f"{arm}_prepare"]]
    prepare_results: list[dict[str, object]] = []
    for command in prepare_commands:
        result = _command_result(_expand(command, values), repo, timeout)
        prepare_results.append(result)
        if not _succeeded(result):
            break
    timed_result: dict[str, object] | None = None
    guard_results: list[dict[str, object]] = []
    if all(_succeeded(result) for result in prepare_results):
        timed_result = _command_result(
            _expand(case[f"{arm}_command"], values),
            repo,
            timeout,
            case["metric"],
        )
    if _succeeded(timed_result):
        for hook in case["guards"]:
            result = _command_result(_expand(hook["command"], values), repo, timeout)
            guard_results.append({"name": hook["name"], "result": result})
            if not _succeeded(result):
                break
    valid = (
        len(prepare_results) == len(prepare_commands)
        and all(_succeeded(result) for result in prepare_results)
        and _succeeded(timed_result)
        and len(guard_results) == len(case["guards"])
        and all(_succeeded(item["result"]) for item in guard_results)
    )
    arm_result = {
        "arm": arm,
        "valid": valid,
        "prepare": prepare_results,
        "timed": timed_result,
        "guards": guard_results,
    }
    return arm_result


def _run_pair(
    case: dict[str, object],
    order: tuple[str, str],
    repos: dict[str, Path],
    fixture: Path,
    python: str,
    timeout: float,
    expected_sources: dict[str, dict[str, object]],
    expected_fixture_sha256: str,
) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix=f"ppt-ab-{case['id']}-") as temporary:
        pair_root = Path(temporary)
        integrity_problems: list[str] = []
        source_before = {arm: source_identity(repo) for arm, repo in repos.items()}
        for arm in ("control", "treatment"):
            if source_before[arm] != expected_sources[arm]:
                integrity_problems.append(f"{arm} source identity changed before pair")
        fixture_before = hash_path(fixture)
        if fixture_before != expected_fixture_sha256:
            integrity_problems.append("fixture identity changed before pair")

        arms: dict[str, dict[str, object]] = {}
        values: dict[str, dict[str, str]] = {}
        copy_hashes: dict[str, str] = {}
        for arm in ("control", "treatment"):
            project = pair_root / f"{arm}-project"
            cache_dir = pair_root / f"{arm}-cache"
            shutil.copytree(fixture, project)
            cache_dir.mkdir()
            copy_hashes[arm] = hash_path(project)
            if copy_hashes[arm] != expected_fixture_sha256:
                integrity_problems.append(f"{arm} project copy does not match the registered fixture")
            values[arm] = {
                "python": python,
                "repo": str(repos[arm]),
                "project": str(project),
                "fixture": str(fixture),
                "cache_dir": str(cache_dir),
            }

        fixture_after_copy = hash_path(fixture)
        if fixture_after_copy != expected_fixture_sha256:
            integrity_problems.append("fixture identity changed while pair projects were copied")
        if integrity_problems:
            raise BenchmarkError("; ".join(integrity_problems))
        for arm in order:
            arms[arm] = _run_arm(
                arm,
                repos[arm],
                case,
                values[arm],
                python,
                timeout,
            )
        comparison_problems: list[str] = []
        if all(arm["valid"] for arm in arms.values()):
            control_value = float(arms["control"]["timed"]["metric_value"])
            if control_value == 0:
                comparison_problems.append(
                    "control primary metric is zero; relative improvement is undefined"
                )
        pair_values = {
            "python": python,
            "fixture": str(fixture),
            "control_repo": str(repos["control"]),
            "treatment_repo": str(repos["treatment"]),
            "control_project": values["control"]["project"],
            "treatment_project": values["treatment"]["project"],
            "control_cache_dir": values["control"]["cache_dir"],
            "treatment_cache_dir": values["treatment"]["cache_dir"],
        }
        pair_guards: list[dict[str, object]] = []
        if all(arm["valid"] for arm in arms.values()) and not comparison_problems:
            for hook in case["pair_guards"]:
                result = _command_result(
                    _expand(hook["command"], pair_values),
                    repos["control"],
                    timeout,
                )
                pair_guards.append({"name": hook["name"], "result": result})
                if not _succeeded(result):
                    break
        valid = (
            not integrity_problems
            and not comparison_problems
            and all(arm["valid"] for arm in arms.values())
            and len(pair_guards) == len(case["pair_guards"])
            and all(_succeeded(item["result"]) for item in pair_guards)
        )
        fixture_after = hash_path(fixture)
        if fixture_after != expected_fixture_sha256:
            integrity_problems.append("fixture identity changed during pair execution")
        source_after = {arm: source_identity(repo) for arm, repo in repos.items()}
        for arm in ("control", "treatment"):
            if source_after[arm] != expected_sources[arm]:
                integrity_problems.append(f"{arm} source identity changed during pair execution")
        valid = valid and not integrity_problems
        return {
            "order": list(order),
            "valid": valid,
            "arms": arms,
            "pair_guards": pair_guards,
            "comparison_problems": comparison_problems,
            "integrity": {
                "valid": not integrity_problems,
                "problems": integrity_problems,
                "fixture_before": fixture_before,
                "fixture_after_copy": fixture_after_copy,
                "fixture_after": fixture_after,
                "project_copy_sha256": copy_hashes,
                "source_before": source_before,
                "source_after": source_after,
            },
        }


def _percentile(values: list[float], quantile: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def _mad(values: list[float]) -> float:
    center = statistics.median(values)
    return statistics.median(abs(value - center) for value in values)


def _bootstrap_ci(
    absolute_improvements: list[float],
    relative_improvements: list[float],
    samples: int,
    seed: int,
) -> tuple[list[float], list[float]]:
    generator = random.Random(seed)
    absolute_medians: list[float] = []
    relative_medians: list[float] = []
    count = len(absolute_improvements)
    for _ in range(samples):
        indices = [generator.randrange(count) for _ in range(count)]
        absolute_medians.append(statistics.median(absolute_improvements[index] for index in indices))
        relative_medians.append(statistics.median(relative_improvements[index] for index in indices))
    return (
        [_percentile(absolute_medians, 0.025), _percentile(absolute_medians, 0.975)],
        [_percentile(relative_medians, 0.025), _percentile(relative_medians, 0.975)],
    )


def summarize_case(
    case_report: dict[str, object],
    bootstrap_samples: int,
    seed: int,
) -> dict[str, object]:
    """Summarize all retained pairs for one exact case/cache condition."""
    control_values: list[float] = []
    treatment_values: list[float] = []
    control_ms: list[float] = []
    treatment_ms: list[float] = []
    for observation in case_report["observations"]:
        control_timed = observation["arms"]["control"]["timed"]
        treatment_timed = observation["arms"]["treatment"]["timed"]
        control_values.append(float(control_timed["metric_value"]))
        treatment_values.append(float(treatment_timed["metric_value"]))
        control_ms.append(float(control_timed["elapsed_ns"]) / 1_000_000)
        treatment_ms.append(float(treatment_timed["elapsed_ns"]) / 1_000_000)
    direction = case_report["decision"]["direction"]
    if direction == "lower":
        absolute_improvements = [
            control - treatment for control, treatment in zip(control_values, treatment_values)
        ]
        relative_improvements = [
            1 - treatment / control for control, treatment in zip(control_values, treatment_values)
        ]
    else:
        absolute_improvements = [
            treatment - control for control, treatment in zip(control_values, treatment_values)
        ]
        relative_improvements = [
            treatment / control - 1 for control, treatment in zip(control_values, treatment_values)
        ]
    group_seed = seed + int(_sha256_bytes(str(case_report["id"]).encode("utf-8"))[:8], 16)
    absolute_ci, relative_ci = _bootstrap_ci(
        absolute_improvements,
        relative_improvements,
        bootstrap_samples,
        group_seed,
    )
    contract = case_report["decision"]
    if contract["kind"] == "superiority":
        absolute_threshold = contract["absolute_mcid"]
        relative_threshold = contract["relative_mcid"]
    else:
        absolute_threshold = -contract["max_absolute_regression"]
        relative_threshold = -contract["max_relative_regression"]
    absolute_pass = absolute_ci[0] >= absolute_threshold
    relative_pass = relative_ci[0] >= relative_threshold
    return {
        "case_id": case_report["id"],
        "stage": case_report["stage"],
        "cache_condition": case_report["cache_condition"],
        "cache_scope": case_report["cache_scope"],
        "quality_mode": case_report["quality_mode"],
        "pair_count": len(absolute_improvements),
        "metric": case_report["metric"],
        "control_median": round(statistics.median(control_values), 9),
        "treatment_median": round(statistics.median(treatment_values), 9),
        "paired_absolute_improvement": {
            "median": round(statistics.median(absolute_improvements), 9),
            "mad": round(_mad(absolute_improvements), 9),
            "bootstrap_95_ci": [round(value, 9) for value in absolute_ci],
        },
        "paired_relative_improvement": {
            "median": round(statistics.median(relative_improvements), 9),
            "mad": round(_mad(relative_improvements), 9),
            "bootstrap_95_ci": [round(value, 9) for value in relative_ci],
        },
        "timing_diagnostic_ms": {
            "control_median": round(statistics.median(control_ms), 6),
            "treatment_median": round(statistics.median(treatment_ms), 6),
        },
        "decision_contract": contract,
        "decision": {
            "status": "go" if absolute_pass and relative_pass else "no-go",
            "kind": contract["kind"],
            "absolute_ci_lower_threshold": absolute_threshold,
            "relative_ci_lower_threshold": relative_threshold,
            "absolute_ci_meets_threshold": absolute_pass,
            "relative_ci_meets_threshold": relative_pass,
        },
    }


def _write_report(path: Path, report: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run paired A/B subprocess benchmarks from a strict JSON plan.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("plan", help="benchmark plan JSON")
    parser.add_argument("--control-repo", required=True, help="control Git worktree")
    parser.add_argument("--treatment-repo", required=True, help="treatment Git worktree")
    parser.add_argument("--fixture", required=True, help="immutable project fixture directory")
    parser.add_argument("--output", required=True, help="JSON report path")
    parser.add_argument("--pairs", type=int, default=10, help="measured pairs; even and at least 10")
    parser.add_argument("--timeout", type=float, default=600.0, help="per-command timeout in seconds")
    parser.add_argument("--bootstrap-samples", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260801)
    parser.add_argument("--python", default=sys.executable, help="Python executable for {python}")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    configure_utf8_stdio()
    args = build_parser().parse_args(argv)
    if args.pairs < 10 or args.pairs % 2:
        print("Error: --pairs must be an even integer of at least 10", file=sys.stderr)
        return 1
    if args.timeout <= 0 or args.bootstrap_samples < 1000:
        print("Error: --timeout must be positive and --bootstrap-samples must be at least 1000", file=sys.stderr)
        return 1

    plan_path = Path(args.plan).resolve()
    fixture = Path(args.fixture).resolve()
    repos = {
        "control": Path(args.control_repo).resolve(),
        "treatment": Path(args.treatment_repo).resolve(),
    }
    output = Path(args.output).resolve()
    harness_path = Path(__file__).resolve()
    telemetry_path = Path(run_telemetry.__file__).resolve()
    try:
        if not fixture.is_dir():
            raise BenchmarkError(f"fixture is not a directory: {fixture}")
        _validate_output_location(
            output,
            plan_path,
            fixture,
            repos,
            harness_path,
            telemetry_path,
        )
        plan, plan_sha256 = load_plan(plan_path)
        fixture_sha256 = hash_path(fixture)
        source_before = {arm: source_identity(repo) for arm, repo in repos.items()}
        harness_sha256 = _sha256_bytes(harness_path.read_bytes())
        telemetry_sha256 = _sha256_bytes(telemetry_path.read_bytes())
    except (OSError, UnicodeError, BenchmarkError, TelemetryError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    report: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "comparable": False,
        "all_go": False,
        "reasons": [],
        "improvement_direction": "positive values favor treatment; each case pre-registers lower or higher",
        "outlier_policy": "none; no deletion, replacement, retry, or winsorization",
        "cache_policy": "summaries are separate per exact case and cache_condition",
        "schedule": "ABBA/BAAB first-arm pattern, repeated",
        "pairs_requested": args.pairs,
        "bootstrap_samples": args.bootstrap_samples,
        "seed": args.seed,
        "plan": {"path": str(plan_path), "sha256": plan_sha256, "sha256_after": None},
        "harness": {
            "path": str(harness_path),
            "schema_version": SCHEMA_VERSION,
            "sha256": harness_sha256,
            "sha256_after": None,
        },
        "dependencies": {
            "run_telemetry": {
                "path": str(telemetry_path),
                "sha256": telemetry_sha256,
                "sha256_after": None,
            }
        },
        "fixture": {"path": str(fixture), "sha256": fixture_sha256},
        "runtime": {
            "host": socket.gethostname(),
            "python": sys.version,
            "python_executable": args.python,
            "platform": platform.platform(),
        },
        "source_before": source_before,
        "source_after": None,
        "cases": [],
        "summaries": [],
    }
    reasons: list[str] = report["reasons"]
    stop = False
    for case in plan["cases"]:
        case_report: dict[str, object] = {
            "id": case["id"],
            "stage": case["stage"],
            "cache_condition": case["cache_condition"],
            "cache_scope": case["cache_scope"],
            "quality_mode": case["quality_mode"],
            "metric": case["metric"],
            "decision": case["decision"],
            "warmup": None,
            "observations": [],
        }
        report["cases"].append(case_report)
        try:
            warmup = _run_pair(
                case,
                ORDER_PATTERN[0],
                repos,
                fixture,
                args.python,
                args.timeout,
                source_before,
                fixture_sha256,
            )
            warmup["discarded"] = True
            case_report["warmup"] = warmup
            if not warmup["valid"]:
                reasons.append(f"case {case['id']}: discarded warmup failed; no measured retry")
                stop = True
                break
            for pair_index in range(args.pairs):
                order = ORDER_PATTERN[pair_index % len(ORDER_PATTERN)]
                observation = _run_pair(
                    case,
                    order,
                    repos,
                    fixture,
                    args.python,
                    args.timeout,
                    source_before,
                    fixture_sha256,
                )
                observation["pair"] = pair_index + 1
                case_report["observations"].append(observation)
                if not observation["valid"]:
                    reasons.append(f"case {case['id']}: pair {pair_index + 1} failed a command or guard")
                    stop = True
                    break
        except (OSError, BenchmarkError, subprocess.SubprocessError) as exc:
            reasons.append(f"case {case['id']}: execution error: {exc}")
            stop = True
        if stop:
            break

    try:
        source_after = {arm: source_identity(repo) for arm, repo in repos.items()}
        report["source_after"] = source_after
        for arm in ("control", "treatment"):
            if source_after[arm] != source_before[arm]:
                reasons.append(f"{arm} source identity changed during the benchmark")
    except (OSError, UnicodeError, BenchmarkError) as exc:
        reasons.append(f"post-run source identity failed: {exc}")
    try:
        plan_after = _sha256_bytes(plan_path.read_bytes())
        report["plan"]["sha256_after"] = plan_after
        if plan_after != plan_sha256:
            reasons.append("benchmark plan changed during the benchmark")
    except OSError as exc:
        reasons.append(f"post-run plan identity failed: {exc}")
    try:
        fixture_after = hash_path(fixture)
        report["fixture"]["sha256_after"] = fixture_after
        if fixture_after != fixture_sha256:
            reasons.append("fixture identity changed during the benchmark")
    except (OSError, TelemetryError) as exc:
        reasons.append(f"post-run fixture identity failed: {exc}")
    try:
        harness_after = _sha256_bytes(harness_path.read_bytes())
        report["harness"]["sha256_after"] = harness_after
        if harness_after != harness_sha256:
            reasons.append("benchmark harness changed during the benchmark")
    except OSError as exc:
        reasons.append(f"post-run harness identity failed: {exc}")
    try:
        telemetry_after = _sha256_bytes(telemetry_path.read_bytes())
        report["dependencies"]["run_telemetry"]["sha256_after"] = telemetry_after
        if telemetry_after != telemetry_sha256:
            reasons.append("run_telemetry dependency changed during the benchmark")
    except OSError as exc:
        reasons.append(f"post-run dependency identity failed: {exc}")

    complete = len(report["cases"]) == len(plan["cases"]) and all(
        len(case["observations"]) == args.pairs for case in report["cases"]
    )
    if not complete and not reasons:
        reasons.append("benchmark did not produce every requested pair")
    report["comparable"] = complete and not reasons
    if report["comparable"]:
        report["summaries"] = [
            summarize_case(case, args.bootstrap_samples, args.seed)
            for case in report["cases"]
        ]
        report["all_go"] = all(
            summary["decision"]["status"] == "go" for summary in report["summaries"]
        )
    try:
        _write_report(output, report)
    except OSError as exc:
        print(f"Error: could not write report: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "report": str(output),
                "comparable": report["comparable"],
                "all_go": report["all_go"],
                "cases_completed": len(report["summaries"]),
                "reasons": reasons,
            },
            ensure_ascii=False,
        )
    )
    return 0 if report["comparable"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
