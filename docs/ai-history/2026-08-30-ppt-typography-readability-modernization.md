# PPT typography readability modernization

Date: 2026-08-30 KST
Project: `FriendY0421/slide-master`
Branch: `fix/ppt-typography-readability-20260830`

## User-visible problem

A newly generated PPT was structurally correct but its text felt too small overall and less polished than desired.

## Root cause

The generic PPT delivery-purpose defaults were `text=20px`, `balanced=24px`, `presentation=32px`. Because export displays roughly `px * 0.75` in PowerPoint points, the default balanced body was about 18pt — effectively a minimum readability level rather than a premium business-presentation baseline.

The old values were duplicated in Strategist guidance, Confirm UI runtime defaults, docs, spec references, and chat fallback guidance. Production presets also did not explicitly seed typography intent.

## Accepted modernization

Generic PPT defaults are raised to:
- `text`: 24px (about 18pt)
- `balanced`: 30px (about 22.5pt)
- `presentation`: 36px (about 27pt)

These are defaults, not a ban on explicit user overrides or source-faithful template contracts.
## Design rules

- Standard non-mirror PPT body text has a 24px hard floor.
- Overflow is solved by less copy per slide, more pages when needed, or geometry reflow before type reduction.
- Title, subtitle, lead, annotation, and footnote roles remain deck-wide locked roles rather than page-by-page ad hoc sizes.
- The modern balanced reference is body 30 / title 52 / subtitle 40 / lead 36 / annotation 22 / footnote 16px.
- Layout archetype hardcoded sizes remain geometry placeholders; executors must apply `spec_lock` typography and reflow.
- Mirror/source-faithful templates remain exceptions and preserve their explicit typography contract.

## Production preset seeds

- `balanced_report`: balanced / 30px
- `executive_brief`: presentation / 36px
- `storytelling_proposal`: balanced / 30px
- `data_insight`: balanced / 30px
- `training_guide`: balanced / 30px
- `product_showcase`: presentation / 36px

Each preset records `typography_profile: modern_readable`.

## Validation

JSON parse, Confirm UI JavaScript syntax, Python compile, preset picker smoke, and `git diff --check` passed. A smoke purpose matching Samsung Electronics Service future strategy ranked Executive Brief first and rendered `presentation | body 36px`. GitHub Actions were not used.