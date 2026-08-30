# Slide Master PPT Typography Readability Handoff

Date: 2026-08-30 KST
Status: MODERN READABILITY DEFAULTS IMPLEMENTED / STATIC SMOKE PASS

## Resume rule

For future complaints that generated PPT text is generally too small, read this handoff before changing typography again. Do not restore the old generic 20/24/32px delivery-purpose defaults unless the user explicitly asks to revert.

## Current generic PPT defaults

- read-close `text`: body 24px
- business `balanced`: body 30px
- projected `presentation`: body 36px
- standard non-mirror PPT body hard floor: 24px

The intent is larger readable type plus more whitespace and lower per-slide information density, not simply enlarging text inside unchanged small containers.

## Overflow policy

Prefer, in order: shorten/restructure slide copy without losing meaning, redistribute content across more pages where the plan allows, widen/reflow containers, then use only bounded local body reduction. Never shrink a standard non-mirror PPT body block below 24px.

Mirror/source-faithful templates retain their explicit source typography contract.
## Preset-aware typography

Production presets now carry `delivery_purpose`, `body_px`, and `typography_profile=modern_readable`. This makes the second picker stage contribute to the actual typography plan instead of being only a content-density label.

Presentation-first presets (`executive_brief`, `product_showcase`) seed 36px. General business/report/analysis/training presets seed 30px.

## Verification completed

- `PRODUCTION_PRESETS.json`: parse PASS
- Confirm UI `catalogs.json`: parse PASS
- Confirm UI `app.js`: syntax PASS
- production preset picker: Python compile PASS
- selection recorder: Python compile PASS
- preset HTML smoke: PASS, including `body 36px`
- `git diff --check`: PASS

## Next acceptance

The next generated real PPT is the visual acceptance. Inspect body readability, title hierarchy, whitespace, and any new overflow. If a problem appears, adjust only the evidenced role/template/layout; do not globally lower typography to recover density.

GitHub Actions remain unused and opt-in only.