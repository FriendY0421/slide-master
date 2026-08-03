#!/usr/bin/env python3
"""
PPT Master - Runtime Contract Drift Check

Check active cross-host workflow invariants without running the presentation
pipeline. This is a contributor diagnostic, not a runtime gate.

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
import re
import sys
from pathlib import Path
from typing import Optional

from console_encoding import configure_utf8_stdio


_ACTIVE_CONTRACT_FILES = (
    "AGENTS.md",
    "CLAUDE.md",
    "docs/faq.md",
    "docs/roadmap.md",
    "docs/technical-design.md",
    ".claude/skills/ppt-master/SKILL.md",
    ".claude/skills/ppt-master/references/artifact-ownership.md",
    ".claude/skills/ppt-master/references/executor-base.md",
    ".claude/skills/ppt-master/references/executor-cheatcard.md",
    ".claude/skills/ppt-master/references/svg-image-embedding.md",
    ".claude/skills/ppt-master/scripts/README.md",
    ".claude/skills/ppt-master/scripts/docs/svg-pipeline.md",
    ".claude/skills/ppt-master/scripts/docs/troubleshooting.md",
    ".claude/skills/ppt-master/scripts/check_runtime_contracts.py",
    ".claude/skills/ppt-master/scripts/verify_deck.py",
    ".claude/skills/ppt-master/workflows/beautify-pptx.md",
    ".claude/skills/ppt-master/workflows/live-preview.md",
    ".claude/skills/ppt-master/workflows/resume-execute.md",
    ".claude/skills/ppt-master/workflows/routing.md",
    ".claude/skills/ppt-master/workflows/verify-charts.md",
    ".claude/skills/ppt-master/workflows/verify-pptx-export.md",
    ".claude/skills/ppt-master/workflows/visual-review.md",
)

_ACTIVE_MARKDOWN_GLOBS = (
    "docs/*.md",
    ".claude/skills/ppt-master/references/**/*.md",
    ".claude/skills/ppt-master/scripts/docs/*.md",
    ".claude/skills/ppt-master/workflows/*.md",
)

_SEMANTIC_REQUIREMENTS = {
    "AGENTS.md": (
        (
            "milestone spec_lock cadence",
            r"spec_lock.{0,240}P01\W*P05\W*P09.{0,160}context compaction",
        ),
        (
            "rendering completion command",
            r"verify_deck\.py\s+<project(?:_path)?>`?(?!\s*--no-render)",
        ),
        (
            "no-render iteration-only escape hatch",
            r"--no-render[^\n]{0,120}iterat|iterat[^\n]{0,120}--no-render",
        ),
    ),
    ".claude/skills/ppt-master/SKILL.md": (
        (
            "milestone spec_lock cadence",
            r"SPEC_LOCK MILESTONE RE-READ.{0,300}P01\W*P05\W*P09"
            r".{0,300}context compaction",
        ),
        (
            "on-demand deferred Step 7.2",
            r"Step 7\.2.{0,300}on-demand,\s*deferred by default",
        ),
        (
            "mandatory final verification",
            r"Final deck verification\s*\(mandatory",
        ),
        (
            "rendering completion command",
            r"verify_deck\.py\s+<project(?:_path)?>`?(?!\s*--no-render)",
        ),
        (
            "no-render iteration-only escape hatch",
            r"--no-render[^\n]{0,120}iterat|iterat[^\n]{0,120}--no-render",
        ),
    ),
    ".claude/skills/ppt-master/references/artifact-ownership.md": (
        (
            "milestone spec_lock cadence",
            r"spec_lock\.md.{0,500}P01\W*P05\W*P09.{0,200}context compaction",
        ),
    ),
    ".claude/skills/ppt-master/references/executor-base.md": (
        (
            "on-demand svg_final preview",
            r"svg_final/.{0,120}(?:only on demand|on-demand)",
        ),
    ),
    ".claude/skills/ppt-master/references/svg-image-embedding.md": (
        (
            "direct native export boundary",
            r"Native PPTX export reads.{0,120}svg_output/",
        ),
        (
            "on-demand finalize boundary",
            r"on-demand.{0,120}finalize_svg\.py|finalize_svg\.py.{0,120}on demand",
        ),
    ),
    ".claude/skills/ppt-master/workflows/resume-execute.md": (
        (
            "milestone spec_lock cadence",
            r"P01\W*P05\W*P09.{0,160}context compaction",
        ),
        (
            "conditional finalize boundary",
            r"finalize_svg.{0,160}only when",
        ),
    ),
    "docs/technical-design.md": (
        (
            "milestone spec_lock cadence",
            r"spec_lock\.md.{0,300}P01\W*P05\W*P09.{0,180}context compaction",
        ),
        (
            "on-demand svg_final architecture",
            r"svg_final/.{0,160}on-demand",
        ),
    ),
    ".claude/skills/ppt-master/scripts/verify_deck.py": (
        (
            "no-render parser flag",
            r"add_argument\(\s*[\"']--no-render[\"'].{0,160}action=[\"']store_true",
        ),
        (
            "no-render runtime behavior",
            r"officecli_checks\(project,\s*render=not args\.no_render\)",
        ),
    ),
}

_STALE_PATTERNS = (
    (
        "per-page spec_lock read",
        r"(?:per[- ]page\s+`?spec_lock(?:\.md)?`?\s+re-?read|"
        r"spec_lock(?:\.md)?[^\n]{0,100}re-?reads?[^\n]{0,60}"
        r"(?:every|each)\s+page|spec_lock(?:\.md)?[^\n]{0,100}"
        r"before\s+(?:every|each)\s+page|reads?\s+it\s+per\s+page)",
    ),
    (
        "mandatory svg_final/finalize",
        r"(?:(?:mandatory|always|required (?:step|artifact|operation|preview))"
        r"[^\n]{0,100}(?:svg_final|finalize_svg)|"
        r"(?:svg_final|finalize_svg)[^\n]{0,40}(?:is mandatory|"
        r"is required|remains mandatory)|"
        r"(?:svg_final|finalize_svg)[^\n]{0,100}(?:mandatory "
        r"(?:self-contained )?(?:visual )?(?:step|artifact|preview)|"
        r"required (?:step|artifact|operation|preview)|"
        r"always (?:runs|creates|generated)|every standard deck))",
    ),
)

_ROUTINE_FINALIZE_COMMAND_FILES = (
    ".claude/skills/ppt-master/references/svg-image-embedding.md",
    ".claude/skills/ppt-master/workflows/beautify-pptx.md",
    ".claude/skills/ppt-master/workflows/live-preview.md",
    ".claude/skills/ppt-master/workflows/verify-charts.md",
    ".claude/skills/ppt-master/workflows/visual-review.md",
)

# The completion run renders one contact sheet. `--no-render` survives only as
# the iteration escape hatch, so any doc line pairing it with a verify command
# must say so on that line (usage synopses listing the flag are exempt).
_ITERATION_ONLY = re.compile(
    r"iterat|re-?export|repeated|skip only|\[--no-render\]",
    re.IGNORECASE,
)

_CONDITIONAL_FINALIZE = re.compile(
    r"(?:only\s+when|on[- ]demand|if\s+.*(?:exists|requested)|"
    r"when\s+.*(?:exists|requested))",
    re.IGNORECASE,
)


def _read_contracts(repo_root: Path, findings: list[str]) -> dict[str, str]:
    """Read active contract files once and report missing inputs."""
    texts: dict[str, str] = {}
    for relative in _ACTIVE_CONTRACT_FILES:
        path = repo_root / relative
        if not path.is_file():
            findings.append(f"missing active contract file: {relative}")
            continue
        texts[relative] = path.read_text(encoding="utf-8", errors="replace")
    for pattern in _ACTIVE_MARKDOWN_GLOBS:
        for path in sorted(repo_root.glob(pattern)):
            if not path.is_file():
                continue
            relative = path.relative_to(repo_root).as_posix()
            if relative not in texts:
                texts[relative] = path.read_text(
                    encoding="utf-8", errors="replace"
                )
    return texts


def _check_semantic_requirements(
        texts: dict[str, str], findings: list[str]) -> None:
    """Check meaning-bearing patterns without pinning prose formatting."""
    for relative, requirements in _SEMANTIC_REQUIREMENTS.items():
        text = texts.get(relative)
        if text is None:
            continue
        for label, pattern in requirements:
            if re.search(pattern, text, re.IGNORECASE | re.DOTALL) is None:
                findings.append(f"{relative}: missing semantic contract: {label}")


def _check_stale_contracts(
        texts: dict[str, str], findings: list[str]) -> None:
    """Reject known semantic forms of superseded runtime contracts."""
    for relative, text in texts.items():
        if relative.endswith("check_runtime_contracts.py"):
            continue
        for label, pattern in _STALE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE) is not None:
                findings.append(f"{relative}: stale runtime contract: {label}")

        for line_number, line in enumerate(text.splitlines(), start=1):
            lowered = line.lower()
            has_sequence = re.search(
                r"finalize_svg(?:\.py)?[^\n]{0,100}"
                r"(?:→|\+|\bthen\b|\bbefore\b)[^\n]{0,100}svg_to_pptx",
                line,
                re.IGNORECASE,
            )
            if has_sequence is not None:
                if _CONDITIONAL_FINALIZE.search(line) is None:
                    findings.append(
                        f"{relative}:{line_number}: unconditional finalize/export chain"
                    )
            if "verify_deck.py" in lowered and "<project" in lowered:
                if ("--no-render" in lowered
                        and _ITERATION_ONLY.search(line) is None):
                    findings.append(
                        f"{relative}:{line_number}: --no-render is the iteration "
                        f"escape hatch only; the completion run renders"
                    )


def _check_finalize_commands(
        texts: dict[str, str], findings: list[str]) -> None:
    """Require explicit conditions on finalize commands in routine workflows."""
    for relative in _ROUTINE_FINALIZE_COMMAND_FILES:
        text = texts.get(relative)
        if text is None:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            if ("finalize_svg.py" in line and "<project" in line
                    and _CONDITIONAL_FINALIZE.search(line) is None):
                findings.append(
                    f"{relative}:{line_number}: finalize command lacks on-demand condition"
                )


def _check_verify_remediation(
        texts: dict[str, str], findings: list[str]) -> None:
    """A stale export requires re-export, not the unrelated preview step."""
    relative = ".claude/skills/ppt-master/scripts/verify_deck.py"
    text = texts.get(relative)
    if text is None:
        return
    match = re.search(
        r"exports/\{newest\.name\} is older than svg_output/.{0,180}",
        text,
        re.DOTALL,
    )
    if match is None:
        findings.append(f"{relative}: missing stale-export remediation")
        return
    remediation = match.group(0)
    if "re-run svg_to_pptx.py" not in remediation:
        findings.append(f"{relative}: stale export must request svg_to_pptx.py")
    if "finalize_svg.py" in remediation:
        findings.append(f"{relative}: stale export must not require finalize_svg.py")


def check_contracts(repo_root: Path) -> list[str]:
    """Return stable contract drift findings for one repository root."""
    findings: list[str] = []
    texts = _read_contracts(repo_root, findings)
    _check_semantic_requirements(texts, findings)
    _check_stale_contracts(texts, findings)
    _check_finalize_commands(texts, findings)
    _check_verify_remediation(texts, findings)
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

    print("[runtime-contracts] PASS — active runtime contracts are aligned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
