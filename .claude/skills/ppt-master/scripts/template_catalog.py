#!/usr/bin/env python3
"""Unified discovery and preview helpers for Slide Master selectable templates.

The catalog is index-driven. Adding a new deck/layout entry to its normal index
makes it discoverable without editing picker code. Selection keys are namespaced
(`deck:<id>`, `layout:<id>`) to remain collision-safe as the library grows.
"""

from __future__ import annotations

import html
import json
import posixpath
import re
from pathlib import Path

import template_gallery as legacy

LAYOUTS_PREFIX = ".claude/skills/ppt-master/templates/layouts"
CATALOG_SOURCES = (
    ("deck", legacy.DECKS_PREFIX, f"{legacy.DECKS_PREFIX}/decks_index.json"),
    ("layout", LAYOUTS_PREFIX, f"{LAYOUTS_PREFIX}/layouts_index.json"),
)
SAFE_ID = re.compile(r"^[A-Za-z0-9_.-]+$")
ACTIVE_STATUS = "ACTIVE"


def selection_key(kind: str, template_id: str) -> str:
    return f"{kind}:{template_id}"


def load_catalog(ref: str | None) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for kind, prefix, index_path in CATALOG_SOURCES:
        raw = json.loads(legacy._read_text(index_path, ref))
        if not isinstance(raw, dict):
            raise ValueError(f"{index_path} must contain an object")
        for template_id, meta in raw.items():
            if not SAFE_ID.fullmatch(str(template_id)) or not isinstance(meta, dict):
                continue
            key = selection_key(kind, template_id)
            out[key] = {
                "key": key,
                "template_kind": kind,
                "template_id": template_id,
                "workspace": f"{prefix}/{template_id}",
                "display_name": meta.get("display_name") or template_id.replace("_", " ").title(),
                "summary": meta.get("summary", ""),
                "canvas_format": meta.get("canvas_format", "ppt169"),
                "page_count": meta.get("page_count"),
                "primary_color": meta.get("primary_color", "#64748b" if kind == "layout" else "#e2e8f0"),
                "primary_category": meta.get("primary_category", "general"),
                "categories": meta.get("categories", []),
                "keywords": meta.get("keywords", []),
                "page_types": meta.get("page_types", []),
                "status": str(meta.get("status", ACTIVE_STATUS) or ACTIVE_STATUS).upper(),
                "version": str(meta.get("version", "1.0")),
                "visibility": meta.get("visibility", "public"),
                "source_type": meta.get("source_type", "native"),
                "fidelity": meta.get("fidelity", "native"),
                "aliases": meta.get("aliases", []),
                "audience": meta.get("audience", []),
                "purpose": meta.get("purpose", []),
                "organization": meta.get("organization"),
                "brand_terms": meta.get("brand_terms", []),
                "document_types": meta.get("document_types", []),
                "tone": meta.get("tone", []),
                "avoid_for": meta.get("avoid_for", []),
                "defaults": meta.get("defaults", {}),
                "quality_score": meta.get("quality_score"),
                "raw_meta": meta,
            }
    return out


def is_selectable(entry: dict) -> bool:
    return str(entry.get("status", ACTIVE_STATUS) or ACTIVE_STATUS).upper() == ACTIVE_STATUS


def selectable_catalog(catalog: dict[str, dict]) -> dict[str, dict]:
    return {key: entry for key, entry in catalog.items() if is_selectable(entry)}


def resolve_choice(choice: str, catalog: dict[str, dict]) -> dict | None:
    choice = str(choice or "").strip()
    if choice in catalog:
        return catalog[choice]
    # Backward compatibility: bare ids are accepted only when unambiguous.
    matches = [entry for entry in catalog.values() if entry["template_id"] == choice]
    if len(matches) == 1:
        return matches[0]
    return None


def all_preview_files(entry: dict, ref: str | None) -> list[str]:
    prefix = f"{entry['workspace']}/templates"
    return sorted(
        path for path in legacy._list_repo_files(prefix, ref)
        if path.lower().endswith(".svg")
    )


def preview_items(entry: dict, ref: str | None, limit: int = 6) -> list[tuple[str, str]]:
    svgs = all_preview_files(entry, ref)
    chosen: list[tuple[str, str]] = []
    used: set[str] = set()
    for _group_label, words in legacy._PREVIEW_GROUPS:
        match = next(
            (path for path in svgs if path not in used and any(word in Path(path).stem.lower() for word in words)),
            None,
        )
        if match:
            chosen.append((match, legacy._preview_label(match)))
            used.add(match)
        if len(chosen) >= limit:
            return chosen[:limit]
    for path in svgs:
        if path in used:
            continue
        chosen.append((path, legacy._preview_label(path)))
        if len(chosen) >= limit:
            break
    return chosen


def preview_svg(entry: dict, svg_path: str, lang: str, ref: str | None) -> str:
    raw = legacy._read_text(svg_path, ref)
    raw = legacy.TOKEN_RE.sub(lambda m: html.escape(legacy._token_value(m.group(1), lang)), raw)
    # Improve Korean fallback on headless/browser hosts without changing the stored template.
    if lang == "ko":
        raw = raw.replace(
            "'Malgun Gothic', sans-serif",
            "'Malgun Gothic', 'Noto Sans CJK KR', 'Noto Sans KR', 'NanumGothic', sans-serif",
        )
        raw = raw.replace(
            '"Malgun Gothic",Arial,sans-serif',
            '"Malgun Gothic","Noto Sans CJK KR","Noto Sans KR","NanumGothic",Arial,sans-serif',
        )
    workspace = entry["workspace"].rstrip("/") + "/"
    base = posixpath.dirname(svg_path)

    def rewrite(match: re.Match) -> str:
        value = match.group(3)
        if value.startswith(("data:", "http://", "https://", "#")):
            return match.group(0)
        resolved = posixpath.normpath(posixpath.join(base, value))
        if not resolved.startswith(workspace):
            return match.group(0)
        url = "/asset?path=" + __import__("urllib.parse", fromlist=["quote"]).quote(resolved, safe="")
        return f"{match.group(1)}{match.group(2)}{url}{match.group(2)}"

    return legacy.HREF_RE.sub(rewrite, raw)


def _norm_text(value: object) -> str:
    return re.sub(r"\s+", "", str(value or "").lower())


def _term_hits(terms: list, purpose: str, weight: int) -> int:
    text = _norm_text(purpose)
    score = 0
    for term in terms or []:
        norm = _norm_text(term)
        if len(norm) >= 2 and norm in text:
            score += weight
    return score


def score_entry(entry: dict, purpose: str, inferred_categories: list[str] | None = None) -> int:
    text = _norm_text(purpose)
    inferred = inferred_categories or []
    score = 0
    primary = str(entry.get("primary_category") or "general")
    categories = [str(x) for x in entry.get("categories", [])]
    if inferred:
        if primary == inferred[0]:
            score += 10
        for idx, category in enumerate(inferred):
            if category in categories:
                score += max(2, 7 - idx)

    # High-value semantic fields. Brand/org matches are strong, but only when
    # the user's request actually contains them.
    score += _term_hits(entry.get("brand_terms", []), purpose, 8)
    organization = entry.get("organization")
    if organization and len(_norm_text(organization)) >= 2 and _norm_text(organization) in text:
        score += 8
    score += _term_hits(entry.get("document_types", []), purpose, 5)
    score += _term_hits(entry.get("purpose", []), purpose, 5)
    score += _term_hits(entry.get("audience", []), purpose, 4)
    score += _term_hits(entry.get("aliases", []), purpose, 4)
    score += _term_hits(entry.get("tone", []), purpose, 2)
    score += _term_hits(entry.get("keywords", []), purpose, 3)

    searchable = " ".join([
        entry.get("template_id", ""), entry.get("display_name", ""),
        entry.get("summary", ""), " ".join(str(x) for x in entry.get("page_types", [])),
    ]).lower()
    compact_searchable = _norm_text(searchable)
    for token in [x for x in re.split(r"[\s,/·]+", str(purpose or "")) if len(x) >= 2]:
        if _norm_text(token) in compact_searchable:
            score += 2

    # Explicit negative-fit terms prevent a branded template from being
    # recommended just because it has high general quality.
    if _term_hits(entry.get("avoid_for", []), purpose, 1):
        return -1000
    return score


def shortlist(catalog: dict[str, dict], purpose: str, inferred_categories: list[str] | None = None, limit: int = 10) -> tuple[list[dict], list[str]]:
    ranked = []
    for key, entry in selectable_catalog(catalog).items():
        score = score_entry(entry, purpose, inferred_categories)
        quality = entry.get("quality_score")
        try:
            quality_value = float(quality) if quality is not None else 0.0
        except (TypeError, ValueError):
            quality_value = 0.0
        ranked.append((score, quality_value, 1 if entry["template_kind"] == "deck" else 0, key, entry))
    ranked.sort(key=lambda x: (-x[0], -x[1], -x[2], x[3]))
    selected = [entry for _score, _quality, _deck_bonus, _key, entry in ranked[: max(1, limit)]]
    positive = [(score, entry["key"]) for score, _q, _b, _k, entry in ranked if score > 0]
    if positive:
        top = positive[0][0]
        cutoff = max(3, int(top * 0.30 + 0.999))
        recommended = [key for score, key in positive if score >= cutoff][:10]
    else:
        recommended = []
    return selected, recommended
