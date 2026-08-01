#!/usr/bin/env python3
"""
PPT Master - Runtime Contract Drift Check

Check a small set of stable cross-host workflow invariants without running the
presentation pipeline. This is a contributor diagnostic, not a runtime gate.

Usage:
    python3 scripts/check_runtime_contracts.py [--repo-root PATH]

Examples:
    python3 scripts/check_runtime_contracts.py
    python3 scripts/check_runtime_contracts.py --repo-root C:/work/slide-master

Dependencies:
    None (only uses standard library)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from console_encoding import configure_utf8_stdio


_REQUIRED_FILES = (
    "AGENTS.md",
    "CLAUDE.md",
    ".claude/skills/ppt-master/SKILL.md",
    ".claude/skills/ppt-master/workflows/routing.md",
    ".claude/skills/ppt-master/scripts/verify_deck.py",
)

_REQUIRED_ANCHORS = {
    "AGENTS.md": (
        "P01/P05/P09",
        "verify_deck.py <project_path>",
    ),
    "CLAUDE.md": (
        "finalize_svg.py <project_path>  # on-demand (deferred by default)",
        "verify_deck.py <project_path>",
    ),
    ".claude/skills/ppt-master/SKILL.md": (
        "**Step 7.2** — SVG post-processing",
        "on-demand, deferred by default",
        "Final deck verification (mandatory",
        "P01, P05, P09",
    ),
}

_FORBIDDEN_STALE_TEXT = {
    "docs/faq.md": (
        "finalize_svg.py remains a mandatory Step 7 operation",
    ),
    "docs/technical-design.md": (
        "Mandatory self-contained visual previews",
        "This mandatory output feeds IDE/browser preview",
    ),
    ".claude/skills/ppt-master/scripts/README.md": (
        "finalize_svg.py` remains mandatory",
    ),
    ".claude/skills/ppt-master/scripts/docs/svg-pipeline.md": (
        "mandatory `finalize_svg.py` step",
        "required Step 7.2 artifact",
        "always creates `svg_final/` before export",
    ),
    ".claude/skills/ppt-master/scripts/docs/troubleshooting.md": (
        "Keep all three steps",
        "mandatory `svg_final/` visual preview",
    ),
}


def check_contracts(repo_root: Path) -> list[str]:
    """Return stable contract drift findings for one repository root."""
    findings: list[str] = []
    texts: dict[str, str] = {}

    for relative in _REQUIRED_FILES:
        path = repo_root / relative
        if not path.is_file():
            findings.append(f"missing required contract file: {relative}")

    for relative, anchors in _REQUIRED_ANCHORS.items():
        path = repo_root / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        texts[relative] = text
        for anchor in anchors:
            if anchor not in text:
                findings.append(f"{relative}: missing stable anchor: {anchor}")

    for relative, stale_phrases in _FORBIDDEN_STALE_TEXT.items():
        path = repo_root / relative
        if not path.is_file():
            findings.append(f"missing consumer document: {relative}")
            continue
        text = texts.get(relative)
        if text is None:
            text = path.read_text(encoding="utf-8", errors="replace")
        for phrase in stale_phrases:
            if phrase in text:
                findings.append(f"{relative}: stale contract phrase: {phrase}")

    return findings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check stable cross-host PPT Master runtime contracts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[4],
        help="slide-master repository root (default: inferred from this script)",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    configure_utf8_stdio()
    args = build_parser().parse_args(argv)
    repo_root = args.repo_root.resolve()
    if not repo_root.is_dir():
        print(f"Error: not a directory: {repo_root}", file=sys.stderr)
        return 2

    findings = check_contracts(repo_root)
    if findings:
        print(f"[runtime-contracts] FAIL ({len(findings)} finding(s))", file=sys.stderr)
        for finding in findings:
            print(f"  - {finding}", file=sys.stderr)
        return 1

    print("[runtime-contracts] PASS — stable cross-host anchors are aligned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
