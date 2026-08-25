---
description: Mandatory scalable two-stage template-selection gate for new Slide Master decks
---

# Template Selection Gate

Every new deck requires explicit template selection before research, project initialization, SVG authoring, or PPTX generation.
`PPT_REQUEST_GUARD.md` owns the fail-closed entry rule; this workflow owns execution details.

## Scope

Apply to new decks from topics, URLs, documents, spreadsheets, conversation content, or re-architectable PPTX source.

Exempt only the documented direct-PPTX/resume routes:
- `ppt-template-fill`
- strict 1:1 `beautify-pptx`
- `native-enhance-pptx`
- resume of a project with already-confirmed template evidence

## Runtime catalog

Use the unified index-driven catalog:

`template_catalog.py`

It merges registered:
- Decks from `templates/decks/decks_index.json`
- Layouts from `templates/layouts/layouts_index.json`

Do not hard-code template ids. New registered entries must appear automatically.
Use collision-safe keys `deck:<id>` / `layout:<id>`.

## ChatGPT / conversational host flow

### Stage 1 — shortlist

Run or reproduce the semantics of:

`python .claude/skills/ppt-master/scripts/template_gallery_chat_manifest_v2.py --source auto --purpose "<actual purpose>" --limit 10`

Rules:
- If 10+ registered templates exist, render 10 actual registered template previews.
- If fewer than 10 exist, render all and state the actual count.
- Free Design is separate.
- Use exact registered SVG source, not recreated approximations.
- Recommendations are contextual, never auto-selected.
- A user's Stage-1 choice is **tentative**, not final evidence.

### Stage 2 — selected-template details

After the tentative choice:
- Resolve the exact workspace through the unified catalog.
- Render up to 6 real registered examples from that workspace.
- Prefer cover/title, agenda/section, content, data/KPI, comparison/visual, closing where available.
- Ask for final confirmation only after these detail previews are visible.

If a host cannot guarantee Korean glyph rendering while rasterizing previews, use English sample tokens inside the SVG preview and Korean labels outside the image. Never display broken glyphs as a valid preview.

### Stage 3 — final selection evidence

Only after final user confirmation, record:

`python .claude/skills/ppt-master/scripts/record_template_choice_v2.py <deck:id|layout:id|free> --purpose "<purpose>" --output <result.json> --confirmed`

Then initialize:

`python .claude/skills/ppt-master/scripts/new_deck_init.py <project_name> --format <format> --template-selection-result <result.json>`

A Stage-1 number/name alone must never be recorded as final selection evidence.

## Clickable HTML/GUI path

When clickable cards/buttons are explicitly desired, or reliable in-chat visual rendering is unavailable, use:

`python .claude/skills/ppt-master/scripts/template_gallery_unified.py --source auto --lang ko --purpose "<actual purpose>" --limit 10`

This is the canonical clickable fallback. It uses the same unified catalog, shows up to 10 shortlist candidates, exposes the full registered library, opens up to 6 real detail examples, and records final confirmation.

The legacy Deck-only gallery is retained only for compatibility/rollback and is not the canonical new-PPT path.

## Hard failures

Stop rather than proceed when any of these occurs:
- 10+ templates exist but fewer than 10 are shown without explicit user request;
- only names/numbers are shown;
- preview is recreated instead of sourced from registered SVG;
- static image is represented as clickable UI;
- Stage-2 detail examples are skipped;
- final evidence is written before Stage-2 confirmation;
- broken Korean glyphs are visible;
- valid selection evidence is missing.

## Downstream enforcement

`template_selection.json`, `template_gate.py`, `new_deck_init.py`, and guarded `svg_to_pptx.py` remain fail-closed. The selection surface changes do not weaken the FAH `TEMPLATE_SELECTION` contract.
