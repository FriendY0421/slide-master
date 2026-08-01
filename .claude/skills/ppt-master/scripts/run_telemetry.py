#!/usr/bin/env python3
"""
PPT Master - Run Telemetry

Append bounded, fixed-schema lifecycle events to a project's run event log.
Each event is one UTF-8 JSON line written with one O_APPEND write.

Usage:
    python3 scripts/run_telemetry.py start <project> --run-id ID --repo-root ROOT \
        --fixture PATH --route ROUTE --cache-condition cold
    python3 scripts/run_telemetry.py event <project> --run-id ID \
        --stage spec --action complete
    python3 scripts/run_telemetry.py metrics <project> --run-id ID \
        --input-bytes N --input-tokens N --file-reads N \
        --duplicate-file-reads N --svg-output-bytes N --svg-pages N \
        --tool-turns N --rewrites N
    python3 scripts/run_telemetry.py end <project> --run-id ID --outcome ok \
        --repo-root ROOT --fixture PATH
    python3 scripts/run_telemetry.py validate <project> --run-id ID

Examples:
    python3 scripts/run_telemetry.py event projects/demo --run-id demo-01 \
        --stage executor --action page_complete --page 1

Dependencies:
    None (only uses standard library)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

from console_encoding import configure_utf8_stdio

SCHEMA_VERSION = 1
MAX_RECORD_BYTES = 8192
LOG_RELATIVE_PATH = Path("analysis") / "run_events.jsonl"
HOST_NAME = socket.gethostname()

EVENT_PAIRS = {
    "run": {"start", "end"},
    "confirm": {"ready", "complete"},
    "spec": {"start", "complete"},
    "images": {"submit", "complete"},
    "executor": {"start", "page_complete", "complete"},
    "qc": {"start", "result"},
    "postprocess": {"start", "complete"},
    "export": {"start", "complete"},
    "verify": {"start", "complete"},
    "cache": {"hit", "miss"},
    "metrics": {"snapshot"},
}
OUTCOMES = {"ok", "error", "aborted", "skipped", "pass", "fail"}
CACHE_CONDITIONS = ("cold", "warm", "mixed", "uncontrolled")
PAGE_EVENTS = {("executor", "page_complete"), ("qc", "result")}
CONTEXT_KEYS = {
    "git_commit",
    "git_dirty",
    "git_diff_sha256",
    "source_sha256",
    "fixture_id",
    "fixture_sha256",
    "route",
    "cache_condition",
}
END_CONTEXT_KEYS = {
    "git_commit",
    "git_dirty",
    "git_diff_sha256",
    "source_sha256",
    "fixture_sha256",
}
BASE_KEYS = {
    "schema_version",
    "run_id",
    "wall_time_ns",
    "monotonic_ns",
    "host",
    "pid",
    "stage",
    "action",
}
METRIC_KEYS = (
    "input_bytes",
    "input_tokens",
    "file_reads",
    "duplicate_file_reads",
    "svg_output_bytes",
    "svg_pages",
    "tool_turns",
    "rewrites",
)
OPTIONAL_KEYS = {"page", "outcome", "context", "end_context", "metrics"}
RUN_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,127}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class TelemetryError(ValueError):
    """Report invalid telemetry input or an invalid event log."""


def _hash_file(hasher: "hashlib._Hash", path: Path) -> None:
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            hasher.update(chunk)


def hash_path(path: Path) -> str:
    """Return a deterministic SHA-256 for one file or directory tree."""
    resolved = path.resolve()
    if not resolved.exists():
        raise TelemetryError(f"fixture does not exist: {path}")
    if resolved.is_symlink():
        raise TelemetryError(f"fixture symlinks are not supported: {path}")

    hasher = hashlib.sha256()
    if resolved.is_file():
        hasher.update(b"file\0")
        hasher.update(resolved.name.encode("utf-8"))
        hasher.update(b"\0")
        _hash_file(hasher, resolved)
        return hasher.hexdigest()

    hasher.update(b"directory\0")
    entries = sorted(resolved.rglob("*"), key=lambda item: item.relative_to(resolved).as_posix())
    for entry in entries:
        relative = entry.relative_to(resolved).as_posix().encode("utf-8")
        if entry.is_symlink():
            raise TelemetryError(f"fixture symlinks are not supported: {entry}")
        if entry.is_dir():
            hasher.update(b"dir\0" + relative + b"\0")
            continue
        if not entry.is_file():
            raise TelemetryError(f"unsupported fixture entry: {entry}")
        hasher.update(b"file\0" + relative + b"\0")
        _hash_file(hasher, entry)
    return hasher.hexdigest()


def _git_bytes(repo_root: Path, *args: str) -> bytes:
    command = ["git", "-C", str(repo_root), *args]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise TelemetryError(f"git command failed ({' '.join(command)}): {detail}")
    return result.stdout


def git_context(repo_root: Path) -> dict[str, object]:
    """Capture commit plus an exact hash of tracked diff and untracked content."""
    root = repo_root.resolve()
    commit = _git_bytes(root, "rev-parse", "HEAD").decode("ascii", errors="strict").strip()
    status = _git_bytes(root, "status", "--porcelain=v1", "--untracked-files=all")
    tracked_diff = _git_bytes(root, "diff", "--binary", "--no-ext-diff", "HEAD", "--", ".")
    untracked_raw = _git_bytes(root, "ls-files", "--others", "--exclude-standard", "-z")

    diff_hasher = hashlib.sha256()
    diff_hasher.update(b"tracked-diff\0")
    diff_hasher.update(tracked_diff)
    diff_hasher.update(b"\0untracked\0")
    untracked = sorted(item for item in untracked_raw.split(b"\0") if item)
    for raw_name in untracked:
        try:
            name = raw_name.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise TelemetryError("git returned a non-UTF-8 untracked path") from exc
        candidate = root / name
        if candidate.is_symlink():
            raise TelemetryError(f"untracked symlinks are not supported: {candidate}")
        if not candidate.is_file():
            raise TelemetryError(f"untracked source is not a regular file: {candidate}")
        diff_hasher.update(raw_name + b"\0")
        _hash_file(diff_hasher, candidate)
        diff_hasher.update(b"\0")
    diff_sha256 = diff_hasher.hexdigest()
    source_sha256 = hashlib.sha256(f"{commit}\0{diff_sha256}".encode("ascii")).hexdigest()
    return {
        "git_commit": commit,
        "git_dirty": bool(status.strip()),
        "git_diff_sha256": diff_sha256,
        "source_sha256": source_sha256,
    }


def _validate_context(context: object) -> None:
    if not isinstance(context, dict):
        raise TelemetryError("run/start context must be an object")
    if set(context) != CONTEXT_KEYS:
        missing = sorted(CONTEXT_KEYS - set(context))
        extra = sorted(set(context) - CONTEXT_KEYS)
        raise TelemetryError(f"invalid run/start context keys; missing={missing}, extra={extra}")
    if not isinstance(context["git_dirty"], bool):
        raise TelemetryError("context.git_dirty must be a boolean")
    commit = context["git_commit"]
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-fA-F]{40,64}", commit):
        raise TelemetryError("context.git_commit must be a Git object id")
    for key in ("git_diff_sha256", "source_sha256", "fixture_sha256"):
        value = context[key]
        if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
            raise TelemetryError(f"context.{key} must be a lowercase SHA-256")
    for key in ("fixture_id", "route"):
        value = context[key]
        if not isinstance(value, str) or not TOKEN_RE.fullmatch(value):
            raise TelemetryError(f"context.{key} has an invalid token")
    if context["cache_condition"] not in CACHE_CONDITIONS:
        raise TelemetryError(f"context.cache_condition must be one of {CACHE_CONDITIONS}")


def _validate_end_context(context: object) -> None:
    if not isinstance(context, dict):
        raise TelemetryError("run/end end_context must be an object")
    if set(context) != END_CONTEXT_KEYS:
        missing = sorted(END_CONTEXT_KEYS - set(context))
        extra = sorted(set(context) - END_CONTEXT_KEYS)
        raise TelemetryError(f"invalid run/end end_context keys; missing={missing}, extra={extra}")
    if not isinstance(context["git_dirty"], bool):
        raise TelemetryError("end_context.git_dirty must be a boolean")
    commit = context["git_commit"]
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-fA-F]{40,64}", commit):
        raise TelemetryError("end_context.git_commit must be a Git object id")
    for key in ("git_diff_sha256", "source_sha256", "fixture_sha256"):
        value = context[key]
        if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
            raise TelemetryError(f"end_context.{key} must be a lowercase SHA-256")


def validate_record(record: object) -> dict[str, object]:
    """Validate one decoded event and return it with a typed mapping shape."""
    if not isinstance(record, dict):
        raise TelemetryError("event must be a JSON object")
    unknown = set(record) - BASE_KEYS - OPTIONAL_KEYS
    missing = BASE_KEYS - set(record)
    if unknown or missing:
        raise TelemetryError(f"invalid event keys; missing={sorted(missing)}, extra={sorted(unknown)}")
    if record["schema_version"] != SCHEMA_VERSION:
        raise TelemetryError(f"unsupported schema_version: {record['schema_version']!r}")
    run_id = record["run_id"]
    if not isinstance(run_id, str) or not RUN_ID_RE.fullmatch(run_id):
        raise TelemetryError("run_id must match [A-Za-z0-9][A-Za-z0-9._-]{0,127}")
    stage = record["stage"]
    action = record["action"]
    if not isinstance(stage, str) or stage not in EVENT_PAIRS:
        raise TelemetryError(f"unknown stage: {stage!r}")
    if not isinstance(action, str) or action not in EVENT_PAIRS[stage]:
        raise TelemetryError(f"invalid stage/action pair: {stage!r}/{action!r}")
    for key in ("wall_time_ns", "monotonic_ns", "pid"):
        if not isinstance(record[key], int) or isinstance(record[key], bool) or record[key] < 0:
            raise TelemetryError(f"{key} must be a non-negative integer")
    host = record["host"]
    if not isinstance(host, str) or not host or len(host) > 255:
        raise TelemetryError("host must be a non-empty string of at most 255 characters")

    pair = (stage, action)
    if "page" in record:
        page = record["page"]
        if pair not in PAGE_EVENTS:
            raise TelemetryError(f"page is not allowed for {stage}/{action}")
        if not isinstance(page, int) or isinstance(page, bool) or page < 1:
            raise TelemetryError("page must be a positive integer")
    if pair == ("executor", "page_complete") and "page" not in record:
        raise TelemetryError("executor/page_complete requires page")

    if "outcome" in record and record["outcome"] not in OUTCOMES:
        raise TelemetryError(f"outcome must be one of {sorted(OUTCOMES)}")
    if pair == ("run", "end") and record.get("outcome") not in {"ok", "error", "aborted"}:
        raise TelemetryError("run/end requires outcome ok, error, or aborted")
    if pair == ("qc", "result") and record.get("outcome") not in {"pass", "fail", "error"}:
        raise TelemetryError("qc/result requires outcome pass, fail, or error")

    if pair == ("run", "start"):
        _validate_context(record.get("context"))
    elif "context" in record:
        raise TelemetryError("context is allowed only for run/start")
    if pair == ("run", "end"):
        _validate_end_context(record.get("end_context"))
    elif "end_context" in record:
        raise TelemetryError("end_context is allowed only for run/end")
    if pair == ("metrics", "snapshot"):
        metrics = record.get("metrics")
        if not isinstance(metrics, dict) or set(metrics) != set(METRIC_KEYS):
            missing_metrics = (
                sorted(set(METRIC_KEYS) - set(metrics or {}))
                if isinstance(metrics, dict)
                else list(METRIC_KEYS)
            )
            extra_metrics = sorted(set(metrics) - set(METRIC_KEYS)) if isinstance(metrics, dict) else []
            raise TelemetryError(
                f"metrics/snapshot requires the fixed run metric keys; "
                f"missing={missing_metrics}, extra={extra_metrics}"
            )
        for key in METRIC_KEYS:
            value = metrics[key]
            if value is not None and (
                not isinstance(value, int) or isinstance(value, bool) or value < 0
            ):
                raise TelemetryError(f"metrics.{key} must be a non-negative integer or null")
    elif "metrics" in record:
        raise TelemetryError("metrics is allowed only for metrics/snapshot")
    return record


def append_event(
    project: Path,
    *,
    run_id: str,
    stage: str,
    action: str,
    page: int | None = None,
    outcome: str | None = None,
    context: dict[str, object] | None = None,
    end_context: dict[str, object] | None = None,
    metrics: dict[str, int | None] | None = None,
) -> Path:
    """Append one bounded event record without reading or syncing the log."""
    record: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "wall_time_ns": time.time_ns(),
        "monotonic_ns": time.perf_counter_ns(),
        "host": HOST_NAME,
        "pid": os.getpid(),
        "stage": stage,
        "action": action,
    }
    if page is not None:
        record["page"] = page
    if outcome is not None:
        record["outcome"] = outcome
    if context is not None:
        record["context"] = context
    if end_context is not None:
        record["end_context"] = end_context
    if metrics is not None:
        record["metrics"] = metrics
    validate_record(record)
    encoded = (
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")
    if len(encoded) >= MAX_RECORD_BYTES:
        raise TelemetryError(f"event record must be smaller than {MAX_RECORD_BYTES} bytes")

    project_path = project.resolve()
    if not project_path.is_dir():
        raise TelemetryError(f"project is not a directory: {project}")
    analysis = project_path / "analysis"
    if analysis.exists() and (analysis.is_symlink() or not analysis.is_dir()):
        raise TelemetryError(f"analysis path is not a regular directory: {analysis}")
    analysis.mkdir(exist_ok=True)
    log_path = analysis / "run_events.jsonl"
    if log_path.exists() and log_path.is_symlink():
        raise TelemetryError(f"event log must not be a symlink: {log_path}")

    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND | getattr(os, "O_BINARY", 0)
    descriptor = os.open(log_path, flags, 0o644)
    try:
        written = os.write(descriptor, encoded)
    finally:
        os.close(descriptor)
    if written != len(encoded):
        raise TelemetryError(f"short append: wrote {written} of {len(encoded)} bytes")
    return log_path


def load_events(project: Path) -> list[dict[str, object]]:
    """Read and validate the complete JSONL log for reporting or validation."""
    log_path = project.resolve() / LOG_RELATIVE_PATH
    if not log_path.is_file():
        raise TelemetryError(f"event log does not exist: {log_path}")
    payload = log_path.read_bytes()
    if payload and not payload.endswith(b"\n"):
        raise TelemetryError("event log ends with a partial record")
    events: list[dict[str, object]] = []
    for line_number, raw_line in enumerate(payload.splitlines(keepends=True), start=1):
        if len(raw_line) >= MAX_RECORD_BYTES:
            raise TelemetryError(f"line {line_number} is not smaller than {MAX_RECORD_BYTES} bytes")
        try:
            decoded = json.loads(raw_line.decode("utf-8"))
            events.append(validate_record(decoded))
        except (UnicodeDecodeError, json.JSONDecodeError, TelemetryError) as exc:
            raise TelemetryError(f"invalid event at line {line_number}: {exc}") from exc
    return events


def validate_run(events: list[dict[str, object]], run_id: str) -> list[str]:
    """Return lifecycle problems for exactly one explicit run id."""
    selected = [event for event in events if event.get("run_id") == run_id]
    if not selected:
        return [f"run_id not found: {run_id}"]
    problems: list[str] = []
    starts = [event for event in selected if (event["stage"], event["action"]) == ("run", "start")]
    ends = [event for event in selected if (event["stage"], event["action"]) == ("run", "end")]
    if len(starts) != 1:
        problems.append(f"expected exactly one run/start; found {len(starts)}")
    if len(ends) != 1:
        problems.append(f"expected exactly one run/end; found {len(ends)}")
    if selected[0]["stage"] != "run" or selected[0]["action"] != "start":
        problems.append("run/start is not the first event for this run id")
    if selected[-1]["stage"] != "run" or selected[-1]["action"] != "end":
        problems.append("run/end is not the last event for this run id")

    hosts = {str(event["host"]) for event in selected}
    if len(hosts) != 1:
        problems.append(f"events span multiple hosts: {sorted(hosts)}")
    if starts and ends and int(ends[0]["monotonic_ns"]) < int(starts[0]["monotonic_ns"]):
        problems.append("run/end monotonic timestamp precedes run/start")
    if len(starts) == 1 and bool(starts[0]["context"]["git_dirty"]):
        problems.append("run source worktree was dirty at run/start")
    if len(ends) == 1 and bool(ends[0]["end_context"]["git_dirty"]):
        problems.append("run source worktree was dirty at run/end")
    if len(starts) == 1 and len(ends) == 1:
        start_context = starts[0]["context"]
        end_context = ends[0]["end_context"]
        for key in (
            "git_commit",
            "git_diff_sha256",
            "source_sha256",
            "fixture_sha256",
        ):
            if start_context[key] != end_context[key]:
                problems.append(f"run/start and run/end {key} differ")

    metric_snapshots = [
        event
        for event in selected
        if (event["stage"], event["action"]) == ("metrics", "snapshot")
    ]
    if len(metric_snapshots) != 1:
        problems.append(f"expected exactly one metrics/snapshot; found {len(metric_snapshots)}")

    lifecycles = {
        "confirm": ("ready", "complete"),
        "spec": ("start", "complete"),
        "images": ("submit", "complete"),
        "executor": ("start", "complete"),
        "qc": ("start", "result"),
        "postprocess": ("start", "complete"),
        "export": ("start", "complete"),
        "verify": ("start", "complete"),
    }
    for stage, (start_action, end_action) in lifecycles.items():
        open_event: dict[str, object] | None = None
        for event in selected:
            if event["stage"] != stage:
                continue
            if event["action"] == start_action:
                if open_event is not None:
                    problems.append(f"{stage}/{start_action} repeated before {stage}/{end_action}")
                open_event = event
            elif event["action"] == end_action:
                if open_event is None:
                    problems.append(f"{stage}/{end_action} has no preceding {stage}/{start_action}")
                else:
                    if int(event["monotonic_ns"]) < int(open_event["monotonic_ns"]):
                        problems.append(f"{stage} completion monotonic timestamp precedes its start")
                    open_event = None
        if open_event is not None:
            problems.append(f"{stage}/{start_action} has no matching {stage}/{end_action}")

    executor_positions = [
        index
        for index, event in enumerate(selected)
        if event["stage"] == "executor" and event["action"] in {"start", "complete"}
    ]
    for index, event in enumerate(selected):
        if event["stage"] == "executor" and event["action"] == "page_complete":
            if len(executor_positions) != 2 or not executor_positions[0] < index < executor_positions[1]:
                problems.append(f"executor/page_complete page {event['page']} is outside executor lifecycle")
    return problems


def _start_context(args: argparse.Namespace) -> dict[str, object]:
    context = git_context(Path(args.repo_root))
    fixture = Path(args.fixture)
    context.update(
        {
            "fixture_id": args.fixture_id or fixture.resolve().name,
            "fixture_sha256": hash_path(fixture),
            "route": args.route,
            "cache_condition": args.cache_condition,
        }
    )
    return context


def _end_context(args: argparse.Namespace) -> dict[str, object]:
    context = git_context(Path(args.repo_root))
    context["fixture_sha256"] = hash_path(Path(args.fixture))
    return {key: context[key] for key in END_CONTEXT_KEYS}


def _metric_cli_value(raw: str) -> int | None:
    if raw.lower() in {"unavailable", "null"}:
        return None
    try:
        value = int(raw)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("use a non-negative integer or 'unavailable'") from exc
    if value < 0:
        raise argparse.ArgumentTypeError("metric values cannot be negative")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Append or validate fixed-schema project run telemetry.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    start = subparsers.add_parser("start", help="append run/start with source and fixture context")
    start.add_argument("project", help="project directory")
    start.add_argument("--run-id", required=True, help="explicit run identifier")
    start.add_argument("--repo-root", required=True, help="Git worktree used for this run")
    start.add_argument("--fixture", required=True, help="file or directory used as the run fixture")
    start.add_argument("--fixture-id", help="stable fixture label; defaults to the fixture basename")
    start.add_argument("--route", required=True, help="exact workflow route label")
    start.add_argument("--cache-condition", required=True, choices=CACHE_CONDITIONS)

    event = subparsers.add_parser("event", help="append one fixed stage/action event")
    event.add_argument("project", help="project directory")
    event.add_argument("--run-id", required=True, help="explicit run identifier")
    event.add_argument("--stage", required=True, choices=tuple(EVENT_PAIRS))
    event.add_argument("--action", required=True, help="action allowed for the selected stage")
    event.add_argument("--page", type=int, help="page number for page-scoped events")
    event.add_argument("--outcome", choices=tuple(sorted(OUTCOMES)))

    metrics = subparsers.add_parser("metrics", help="append one fixed cumulative run-metric snapshot")
    metrics.add_argument("project", help="project directory")
    metrics.add_argument("--run-id", required=True, help="explicit run identifier")
    for key in METRIC_KEYS:
        metrics.add_argument(
            "--" + key.replace("_", "-"),
            dest=key,
            required=True,
            type=_metric_cli_value,
            help=f"non-negative cumulative {key.replace('_', ' ')} or 'unavailable'",
        )

    end = subparsers.add_parser("end", help="append the terminal run/end event")
    end.add_argument("project", help="project directory")
    end.add_argument("--run-id", required=True, help="explicit run identifier")
    end.add_argument("--outcome", required=True, choices=("ok", "error", "aborted"))
    end.add_argument("--repo-root", required=True, help="same Git worktree recorded at run/start")
    end.add_argument("--fixture", required=True, help="same fixture recorded at run/start")

    validate = subparsers.add_parser("validate", help="fully parse the log and validate one run")
    validate.add_argument("project", help="project directory")
    validate.add_argument("--run-id", required=True, help="explicit run identifier")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    configure_utf8_stdio()
    args = build_parser().parse_args(argv)
    try:
        project = Path(args.project)
        if args.command == "start":
            path = append_event(
                project,
                run_id=args.run_id,
                stage="run",
                action="start",
                context=_start_context(args),
            )
            print(path)
            return 0
        if args.command == "event":
            if args.stage in {"run", "metrics"}:
                raise TelemetryError(f"use the dedicated {args.stage} subcommand")
            path = append_event(
                project,
                run_id=args.run_id,
                stage=args.stage,
                action=args.action,
                page=args.page,
                outcome=args.outcome,
            )
            print(path)
            return 0
        if args.command == "end":
            path = append_event(
                project,
                run_id=args.run_id,
                stage="run",
                action="end",
                outcome=args.outcome,
                end_context=_end_context(args),
            )
            print(path)
            return 0
        if args.command == "metrics":
            path = append_event(
                project,
                run_id=args.run_id,
                stage="metrics",
                action="snapshot",
                metrics={key: getattr(args, key) for key in METRIC_KEYS},
            )
            print(path)
            return 0

        events = load_events(project)
        problems = validate_run(events, args.run_id)
        payload = {
            "run_id": args.run_id,
            "valid": not problems,
            "event_count": sum(event["run_id"] == args.run_id for event in events),
            "problems": problems,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if not problems else 2
    except (OSError, TelemetryError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
