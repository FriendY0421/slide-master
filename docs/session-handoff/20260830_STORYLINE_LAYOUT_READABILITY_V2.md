# Slide Master — Storyline + Layout Readability V2 Handoff

Date: 2026-08-30 22:14 KST
Base main before this change: `f5939c292a51b259283dd11b7d4e5913e9d233ca`
Working branch: `fix/ppt-layout-spacing-20260830`
Status: VALIDATED / IMPLEMENTED ON MAIN
Implementation commit: `fabf6b60afe99de9114ab8eecb718a4bdfe01438`

## Current authority
For new FriendY PPT decks, use this order:
`template -> preset -> research -> full slide-by-slide preview -> user edits -> explicit approval -> init/generation -> QA -> PPTX`

The preview must expose each slide's number, title, core message, main points, visual plan, and layout plan. The user may change individual slides or the total count, including 20/30+.

## Machine gates
- `.claude/skills/ppt-master/scripts/storyline_gate.py`
- `new_deck_init.py --storyline-approval-result ...` is mandatory for new-deck initialization.
- `storyline_approval.json` contains the approved snapshot + SHA-256.
- `validate_spec.py` compares generated §IX slide count/titles/core messages to the approved snapshot.
- `svg_to_pptx.py` blocks current gate-v3 export if storyline approval is missing.

## Readability defaults
- `text`: 28px (~21pt)
- `balanced`: 34px (~25.5pt)
- `presentation`: 40px (30pt)
- normal non-mirror emergency floor: 24px

Cards/panels: 24–32px H padding, 18–28px V padding; body line-height 1.35–1.5×; semantic gaps 10–22px. Normal content pages aim for intentional 72–88% content-area occupancy. Meaningful visuals usually receive 35–55% on split slides.

## Do not regress
- Do not author PPT slides before the user sees/edits/approves the current storyline.
- Do not treat a title-only list as sufficient preview.
- Do not use tiny fonts to satisfy a requested page count.
- Do not create filler to reach 20/30 slides.
- Do not use zero-padding cards or cram text inside a small box while leaving large unused outer space.
- Do not change the foreground Picker/Tunnel runtime model as part of this change.

## Verified tests
20-slide and 30-slide approvals PASS; missing approval blocks init/export; post-approval title drift is detected; static parses and preset HTML smoke PASS. GitHub Actions unused.
