#!/usr/bin/env python3
"""Validate that a registered template is recommended for intended prompts."""
from __future__ import annotations

import argparse
import json

import template_catalog as catalog_core
import template_gallery as legacy
import template_gallery_context as context


def _rank(catalog: dict[str, dict], prompt: str) -> tuple[list[dict], list[str]]:
    inferred = context.infer_categories(prompt)
    return catalog_core.shortlist(catalog, prompt, inferred, max(len(catalog), 1))


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Slide Master template recommendation fit")
    parser.add_argument("--template", required=True, help="deck:<id>, layout:<id>, or unambiguous bare id")
    parser.add_argument("--source", choices=("auto", "github", "local"), default="local")
    parser.add_argument("--prompt", action="append", default=[], help="Positive-fit prompt; repeat as needed")
    parser.add_argument("--avoid-prompt", action="append", default=[], help="Prompt where the template should not be recommended")
    parser.add_argument("--top-n", type=int, default=3)
    args = parser.parse_args()

    ref, source_label = legacy._resolve_source(args.source)
    catalog = catalog_core.selectable_catalog(catalog_core.load_catalog(ref))
    target = catalog_core.resolve_choice(args.template, catalog)
    if not target:
        print(json.dumps({"ok": False, "error": "template_not_selectable", "template": args.template}, ensure_ascii=False))
        return 2

    target_key = target["key"]
    failures: list[dict] = []
    checks: list[dict] = []
    top_n = max(1, args.top_n)

    for prompt in args.prompt:
        ranked, recommended = _rank(catalog, prompt)
        keys = [entry["key"] for entry in ranked]
        rank = keys.index(target_key) + 1 if target_key in keys else None
        passed = rank is not None and rank <= top_n and target_key in recommended
        row = {"type": "positive", "prompt": prompt, "rank": rank, "recommended": target_key in recommended, "pass": passed}
        checks.append(row)
        if not passed:
            failures.append(row)

    for prompt in args.avoid_prompt:
        ranked, recommended = _rank(catalog, prompt)
        keys = [entry["key"] for entry in ranked]
        rank = keys.index(target_key) + 1 if target_key in keys else None
        passed = target_key not in recommended
        row = {"type": "negative", "prompt": prompt, "rank": rank, "recommended": target_key in recommended, "pass": passed}
        checks.append(row)
        if not passed:
            failures.append(row)

    result = {
        "ok": not failures,
        "source": source_label,
        "template": target_key,
        "top_n": top_n,
        "checks": checks,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
