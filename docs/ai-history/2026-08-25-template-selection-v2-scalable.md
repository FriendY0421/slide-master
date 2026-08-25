# Template Selection V2 — Scalable Two-Stage Flow

Updated: 2026-08-25 11:15 KST

## Why V2 was required

Repeated PPT requests exposed four separate defects:

1. The picker read only `decks_index.json`, so only 4 Decks appeared even though registered Layout templates also existed.
2. `up to 10 recommended` was incorrectly treated as if it satisfied the user's requirement to actually show 10 template candidates.
3. A static composite PNG was used in ChatGPT and incorrectly stood in for the earlier interactive gallery; it had no real card selection, detail drill-down, or confirm state.
4. Korean sample text rasterized on a headless environment without verified Korean fonts, producing broken glyphs.

## Durable architecture

V2 introduces an index-driven shared catalog:

- `template_catalog.py`
- Deck source: `templates/decks/decks_index.json`
- Layout source: `templates/layouts/layouts_index.json`

No current template ids are hard-coded. Adding future Deck/Layout entries to their normal indexes makes them discoverable automatically.

Selection keys are namespaced:

- `deck:<id>`
- `layout:<id>`

This prevents future id collisions.

## ChatGPT flow

1. `template_gallery_chat_manifest_v2.py` builds a context-ranked shortlist.
2. When 10+ registered templates exist, Stage 1 shows 10 real registered candidates. Free Design is separate.
3. Stage-1 choice is tentative only.
4. Stage 2 shows up to 6 real registered layouts from the tentative choice.
5. Only after final user confirmation may `record_template_choice_v2.py --confirmed` write selection evidence.
6. `new_deck_init.py`, `template_gate.py`, and guarded `svg_to_pptx.py` remain downstream fail-closed gates.

## Clickable UI

`template_gallery_unified.py` is the new canonical HTML/GUI picker for environments where actual clickable cards/buttons are desired. It uses the same unified catalog and the same detail-confirmation model.

The previous Deck-only HTML picker and V1 chat manifest are retained for rollback/compatibility only; they are not the canonical FriendY new-PPT path.

## Korean preview safety

Preview rendering must never display broken Korean glyphs. Browser mode uses an expanded Korean fallback stack. For headless rasterization, Korean sample text is used only when Korean font support is positively verified; otherwise English sample tokens are used inside the template preview and Korean labels remain outside the image.

## Current catalog facts

At the time of this correction the repository contains 4 registered Decks and 7 registered Layouts (11 selectable registered templates total). This number is not encoded into V2 logic and may grow without picker-code edits.

## Verification status

- GitHub source creation/update: completed.
- Canonical guard/workflow switched to V2: completed.
- FAH execution contract: intentionally unchanged, still v1.0 / runtime @45.
- GitHub Actions: not used.
- HOME-PC ping: successful.
- HOME-PC command-based runtime test: not claimed; terminal/file-search calls were intermittently unresponsive, so no destructive or repeated probing was performed.

The next actual PPT request is the practical end-to-end acceptance test: Stage 1 must show 10 registered candidates when 10+ exist, Stage 2 must show detail examples, and final evidence must not be written before explicit confirmation.
