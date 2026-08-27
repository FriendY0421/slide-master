# 2026-08-27 — Company template lifecycle and recommendation governance

## Problem
The GPTS contract said newly ACTIVE company/user templates join future recommendations, but the repository lacked a complete canonical onboarding document and machine filtering for CANDIDATE/DEPRECATED/DISABLED states.

## Changes
- Added `docs/gpts/COMPANY_TEMPLATE_REGISTRATION.md`.
- Added `docs/gpts/PRODUCTION_PRESETS.json`.
- Added `docs/gpts/TEMPLATE_METADATA_SCHEMA.json`.
- `register_template.py` now passes optional catalog metadata from `design_spec.md` frontmatter into Deck/Layout/Brand index entries.
- `template_catalog.py` reads status/version/source/fidelity/visibility and related metadata.
- Missing legacy status remains backward-compatible as `ACTIVE`.
- Normal picker/recommendation inventory uses only `ACTIVE` entries.
- Chat manifest reports total/selectable/inactive counts.
- Inline HTML picker also uses only selectable templates.

## Security
Confidential company source files must not be committed to public `FriendY0421/slide-master`. Private originals and sanitized derived templates remain separate.

## Validation
- Python compile: PASS.
- Synthetic ACTIVE/CANDIDATE shortlist filtering: PASS.
- Synthetic company frontmatter metadata passthrough: PASS without installing PyYAML.
- Current live local catalog: 11 total / 11 selectable / 0 inactive / shortlist 10.
- `git diff --check`: PASS.
- GitHub Actions: not used.
