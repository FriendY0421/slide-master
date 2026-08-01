#!/usr/bin/env python3
"""
PPT Master - Run Timing Report

Report one explicit telemetry run, or show legacy artifact mtimes as a clearly
non-comparable diagnostic when no run id is supplied.

Usage:
    python3 scripts/measure_run.py <project_path> [--run-id ID] [--json]

Examples:
    python3 scripts/measure_run.py projects/demo
    python3 scripts/measure_run.py projects/demo --run-id ab-20260801 --json

Dependencies:
    None (only uses standard library)
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from console_encoding import configure_utf8_stdio
from run_telemetry import METRIC_KEYS, TelemetryError, load_events, validate_run

# (marker key, human label, evidence description)
STAGE_ORDER = [
    ("project_created", "Project created", "project_meta.json birth"),
    ("sources_ready", "Sources ready", "newest file under sources/"),
    ("recommendations_written", "Confirm recommendations written", "confirm_ui/recommendations.json"),
    ("user_confirmed", "User confirmed", "confirm_ui/result.json confirmed_at"),
    ("spec_written", "Spec written", "design_spec.md / spec_lock.md"),
    ("images_done", "Images acquired", "newest file under images/"),
    ("first_page", "First SVG page", "oldest svg_output/*.svg"),
    ("last_page", "Last SVG page", "newest svg_output/*.svg"),
    ("finalize_done", "SVG finalized", "newest file under svg_final/"),
    ("export_done", "PPTX exported", "newest exports/*.pptx"),
    ("render_done", "Verify render", "newest file under _pptx_render/"),
]

EVENT_SPANS = [
    ("confirm", "ready", "complete"),
    ("spec", "start", "complete"),
    ("images", "submit", "complete"),
    ("executor", "start", "complete"),
    ("qc", "start", "result"),
    ("postprocess", "start", "complete"),
    ("export", "start", "complete"),
    ("verify", "start", "complete"),
]

LEGACY_WARNING = (
    "Artifact mtimes can move after edits, copies, or re-exports. This output is diagnostic only "
    "and must not be used for A/B comparison."
)


def _newest_mtime(root: Path, pattern: str = "**/*") -> Optional[float]:
    """Return the newest file mtime under root matching pattern, or None."""
    times = [path.stat().st_mtime for path in root.glob(pattern) if path.is_file()]
    return max(times) if times else None


def _oldest_mtime(root: Path, pattern: str = "**/*") -> Optional[float]:
    times = [path.stat().st_mtime for path in root.glob(pattern) if path.is_file()]
    return min(times) if times else None


def _result_confirmed_at(project: Path) -> Optional[float]:
    """Prefer result.json's confirmed_at field; fall back to file mtime."""
    result_path = project / "confirm_ui" / "result.json"
    if not result_path.is_file():
        return None
    try:
        data = json.loads(result_path.read_text(encoding="utf-8"))
        stamp = data.get("confirmed_at", "")
        if stamp:
            return datetime.fromisoformat(stamp).timestamp()
    except (ValueError, OSError, json.JSONDecodeError):
        pass
    return result_path.stat().st_mtime


def collect_markers(project: Path) -> dict[str, float]:
    """Gather legacy stage-boundary timestamps from project artifacts."""
    markers: dict[str, Optional[float]] = {}
    meta = project / "project_meta.json"
    if meta.is_file():
        stat = meta.stat()
        markers["project_created"] = min(stat.st_ctime, stat.st_mtime)
    markers["sources_ready"] = _newest_mtime(project / "sources") if (project / "sources").is_dir() else None
    recommendations = project / "confirm_ui" / "recommendations.json"
    markers["recommendations_written"] = (
        recommendations.stat().st_mtime if recommendations.is_file() else None
    )
    markers["user_confirmed"] = _result_confirmed_at(project)
    spec_times = [
        path.stat().st_mtime
        for path in (project / "design_spec.md", project / "spec_lock.md")
        if path.is_file()
    ]
    markers["spec_written"] = max(spec_times) if spec_times else None
    markers["images_done"] = _newest_mtime(project / "images") if (project / "images").is_dir() else None
    svg_dir = project / "svg_output"
    if svg_dir.is_dir():
        markers["first_page"] = _oldest_mtime(svg_dir, "*.svg")
        markers["last_page"] = _newest_mtime(svg_dir, "*.svg")
    markers["finalize_done"] = (
        _newest_mtime(project / "svg_final") if (project / "svg_final").is_dir() else None
    )
    markers["export_done"] = (
        _newest_mtime(project / "exports", "*.pptx") if (project / "exports").is_dir() else None
    )
    markers["render_done"] = (
        _newest_mtime(project / "_pptx_render") if (project / "_pptx_render").is_dir() else None
    )
    return {key: timestamp for key, timestamp in markers.items() if timestamp is not None}


def page_cadence(project: Path) -> dict[str, object]:
    """Return legacy page mtime sequence and interval statistics."""
    svg_dir = project / "svg_output"
    if not svg_dir.is_dir():
        return {}
    pages = sorted(
        ((path.stat().st_mtime, path.name) for path in svg_dir.glob("*.svg")),
        key=lambda item: item[0],
    )
    intervals = [later[0] - earlier[0] for earlier, later in zip(pages, pages[1:])]
    stats: dict[str, float] = {}
    if intervals:
        stats = {
            "min_s": round(min(intervals), 1),
            "median_s": round(statistics.median(intervals), 1),
            "max_s": round(max(intervals), 1),
            "mean_s": round(statistics.mean(intervals), 1),
        }
    return {
        "pages": [{"name": name, "mtime": timestamp} for timestamp, name in pages],
        "interval_stats": stats,
    }


def build_legacy_report(project: Path) -> dict[str, object]:
    """Build the retained non-comparable mtime diagnostic payload."""
    markers = collect_markers(project)
    return {
        "project": str(project),
        "source": "artifact_mtime",
        "diagnostic_only": True,
        "comparable": False,
        "warning": LEGACY_WARNING,
        "markers": {
            key: {"ts": timestamp, "iso": datetime.fromtimestamp(timestamp).isoformat()}
            for key, timestamp in markers.items()
        },
        "cadence": page_cadence(project),
    }


def _pair_spans(events: list[dict[str, object]]) -> list[dict[str, object]]:
    spans: list[dict[str, object]] = []
    for stage, start_action, end_action in EVENT_SPANS:
        opened: dict[str, object] | None = None
        occurrence = 0
        for event in events:
            if event["stage"] != stage:
                continue
            if event["action"] == start_action:
                opened = event
            elif event["action"] == end_action and opened is not None:
                occurrence += 1
                duration_ns = int(event["monotonic_ns"]) - int(opened["monotonic_ns"])
                spans.append(
                    {
                        "stage": stage,
                        "occurrence": occurrence,
                        "duration_ms": round(duration_ns / 1_000_000, 3),
                        "start_wall_time_ns": opened["wall_time_ns"],
                        "end_wall_time_ns": event["wall_time_ns"],
                    }
                )
                opened = None
    return spans


def _event_page_cadence(events: list[dict[str, object]]) -> dict[str, object]:
    pages = [
        event
        for event in events
        if event["stage"] == "executor" and event["action"] == "page_complete"
    ]
    intervals = [
        (int(later["monotonic_ns"]) - int(earlier["monotonic_ns"])) / 1_000_000
        for earlier, later in zip(pages, pages[1:])
    ]
    stats: dict[str, float] = {}
    if intervals:
        stats = {
            "min_ms": round(min(intervals), 3),
            "median_ms": round(statistics.median(intervals), 3),
            "mean_ms": round(statistics.mean(intervals), 3),
            "max_ms": round(max(intervals), 3),
        }
    return {
        "pages": [
            {"page": event["page"], "wall_time_ns": event["wall_time_ns"]}
            for event in pages
        ],
        "interval_stats": stats,
    }


def build_event_report(project: Path, run_id: str) -> dict[str, object]:
    """Build an event-based report for exactly one requested run id."""
    all_events = load_events(project)
    events = [event for event in all_events if event["run_id"] == run_id]
    problems = validate_run(all_events, run_id)
    if events:
        terminal = [
            event
            for event in events
            if event["stage"] == "run" and event["action"] == "end"
        ]
        if terminal and terminal[-1].get("outcome") != "ok":
            problems.append(f"run ended with outcome={terminal[-1].get('outcome')}")
        failed_qc = [
            event
            for event in events
            if event["stage"] == "qc"
            and event["action"] == "result"
            and event.get("outcome") != "pass"
        ]
        if failed_qc:
            problems.append(f"{len(failed_qc)} qc result event(s) did not pass")

    starts = [
        event
        for event in events
        if event["stage"] == "run" and event["action"] == "start"
    ]
    ends = [
        event
        for event in events
        if event["stage"] == "run" and event["action"] == "end"
    ]
    total_ms: float | None = None
    if len(starts) == 1 and len(ends) == 1:
        total_ms = round(
            (int(ends[0]["monotonic_ns"]) - int(starts[0]["monotonic_ns"])) / 1_000_000,
            3,
        )
    cache_counts = {
        action: sum(event["stage"] == "cache" and event["action"] == action for event in events)
        for action in ("hit", "miss")
    }
    metric_snapshots = [
        event["metrics"]
        for event in events
        if event["stage"] == "metrics" and event["action"] == "snapshot"
    ]
    metrics = metric_snapshots[0] if len(metric_snapshots) == 1 else None
    metric_availability = {
        "snapshot_present": metrics is not None,
        "available": [],
        "unavailable": list(METRIC_KEYS),
    }
    if metrics is not None:
        metric_availability = {
            "snapshot_present": True,
            "available": [key for key in METRIC_KEYS if metrics[key] is not None],
            "unavailable": [key for key in METRIC_KEYS if metrics[key] is None],
        }
    return {
        "project": str(project),
        "source": "run_events",
        "run_id": run_id,
        "diagnostic_only": False,
        "comparable": not problems,
        "problems": problems,
        "event_count": len(events),
        "context": starts[0].get("context") if len(starts) == 1 else None,
        "end_context": ends[0].get("end_context") if len(ends) == 1 else None,
        "total_ms": total_ms,
        "spans": _pair_spans(events),
        "page_cadence": _event_page_cadence(events),
        "cache_counts": cache_counts,
        "metrics": metrics,
        "metric_availability": metric_availability,
    }


def _fmt_ts(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).strftime("%m-%d %H:%M:%S")


def _fmt_wall_ns(timestamp_ns: int) -> str:
    value = datetime.fromtimestamp(timestamp_ns / 1_000_000_000, tz=timezone.utc)
    return value.isoformat().replace("+00:00", "Z")


def _fmt_dur(seconds: float) -> str:
    minutes, secs = divmod(int(round(seconds)), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h{minutes:02d}m{secs:02d}s"
    if minutes:
        return f"{minutes}m{secs:02d}s"
    return f"{secs}s"


def print_legacy_report(report: dict[str, object]) -> None:
    """Print the legacy diagnostic with an unavoidable comparability warning."""
    print(f"Legacy mtime diagnostic — {report['project']}")
    print("Comparable: NO (diagnostic only)")
    print(f"Warning: {report['warning']}")
    print()
    markers = {
        key: float(value["ts"])
        for key, value in dict(report["markers"]).items()
    }
    present = [(key, label) for key, label, _description in STAGE_ORDER if key in markers]
    if not present:
        print("No stage markers found (is this a project directory?)")
        return
    print(f"{'Stage':<34}{'At':<18}{'Δ from previous':<16}")
    previous: Optional[float] = None
    for key, label in present:
        timestamp = markers[key]
        delta = _fmt_dur(timestamp - previous) if previous is not None and timestamp >= previous else "-"
        print(f"{label:<34}{_fmt_ts(timestamp):<18}{delta:<16}")
        previous = timestamp

    cadence = dict(report["cadence"])
    pages = list(cadence.get("pages") or [])
    stats = dict(cadence.get("interval_stats") or {})
    if pages:
        print()
        print(f"SVG page cadence — {len(pages)} pages (mtime diagnostic)")
        if stats:
            print(
                "  interval min/median/mean/max: "
                f"{_fmt_dur(stats['min_s'])} / {_fmt_dur(stats['median_s'])} / "
                f"{_fmt_dur(stats['mean_s'])} / {_fmt_dur(stats['max_s'])}"
            )


def print_event_report(report: dict[str, object]) -> None:
    """Print an explicit-run event report."""
    print(f"Run event report — {report['project']}")
    print(f"Run id: {report['run_id']}")
    print(f"Comparable: {'YES' if report['comparable'] else 'NO'}")
    if report["problems"]:
        for problem in report["problems"]:
            print(f"  problem: {problem}")
    context = report.get("context")
    if context:
        print(
            f"Source: {context['git_commit']} dirty={context['git_dirty']} "
            f"fixture={context['fixture_id']} route={context['route']} "
            f"cache={context['cache_condition']}"
        )
    end_context = report.get("end_context")
    if end_context:
        print(
            f"End source: {end_context['git_commit']} dirty={end_context['git_dirty']} "
            f"fixture_sha256={end_context['fixture_sha256']}"
        )
    if report["total_ms"] is not None:
        print(f"Total: {report['total_ms']:.3f} ms")
    spans = list(report["spans"])
    if spans:
        print()
        print(f"{'Stage':<22}{'Occurrence':<12}{'Duration':<16}{'Started (UTC)'}")
        for span in spans:
            print(
                f"{span['stage']:<22}{span['occurrence']:<12}"
                f"{span['duration_ms']:.3f} ms{'':<7}"
                f"{_fmt_wall_ns(int(span['start_wall_time_ns']))}"
            )
    cache = report["cache_counts"]
    print(f"Cache events: hit={cache['hit']} miss={cache['miss']}")
    metrics = report.get("metrics")
    if metrics:
        print("Run metrics:")
        for key in METRIC_KEYS:
            value = metrics[key] if metrics[key] is not None else "unavailable"
            print(f"  {key}: {value}")
    else:
        print("Run metrics: unavailable (no metrics/snapshot event)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Report one explicit telemetry run; without --run-id, emit only a "
            "non-comparable legacy mtime diagnostic."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("project", help="path to projects/<project_name>")
    parser.add_argument("--run-id", help="explicit telemetry run id; never inferred")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    configure_utf8_stdio()
    args = build_parser().parse_args(argv)
    project = Path(args.project)
    if not project.is_dir():
        print(f"Error: not a directory: {project}", file=sys.stderr)
        return 1
    try:
        report = build_event_report(project, args.run_id) if args.run_id else build_legacy_report(project)
    except (OSError, TelemetryError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.run_id:
        print_event_report(report)
    else:
        print_legacy_report(report)
    return 0 if report["comparable"] or not args.run_id else 2


if __name__ == "__main__":
    raise SystemExit(main())
