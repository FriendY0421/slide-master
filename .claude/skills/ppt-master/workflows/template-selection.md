---
description: Mandatory scalable conversation-interactive template-selection gate for new Slide Master decks
---

# Template Selection Gate

Every new deck requires explicit template + production-preset selection before research. Project initialization, slide authoring, SVG work, or PPTX generation additionally requires explicit approval of the post-research storyline/content outline.
`PPT_REQUEST_GUARD.md` owns the fail-closed entry rule; this workflow owns execution details.

## Scope

Apply to new decks from topics, URLs, documents, spreadsheets, conversation content, or re-architectable PPTX source.

Exempt only documented direct-PPTX/resume routes:
- `ppt-template-fill`
- strict 1:1 `beautify-pptx`
- `native-enhance-pptx`
- resume of a project with already-confirmed template evidence

A user who directly specifies a valid registered template does not need the template picker, but still requires an explicit production preset (unless already supplied) and gate-v3 selection recording.

## Host preparation is not generation permission

A ChatGPT host may require `artifact_handoff` / presentation preparation before any other tool call. That call is preparation only. Immediately after it, enter this workflow. Do not research until valid template+preset evidence exists. Do not initialize, author slides, or export PPTX until the post-research storyline/content outline is explicitly approved.

## Runtime catalog — latest GitHub every request

Use `template_catalog.py`, which merges:
- Decks from `templates/decks/decks_index.json`
- Layouts from `templates/layouts/layouts_index.json`

Do not hard-code ids or counts. New/updated registered entries must appear automatically on the next PPT request.
Use collision-safe keys `deck:<id>` / `layout:<id>`.

For FriendY production PPT requests, refresh from GitHub `main` rather than silently relying on stale local state.

## Stage 1 — conversation-native interactive picker first

On ChatGPT/GPTS, if App Block / GenUI is available, it is mandatory as the first selection surface.

Use `template_gallery_chat_manifest_v2.py` as the live data contract for the picker:

`python .claude/skills/ppt-master/scripts/template_gallery_chat_manifest_v2.py --source github --purpose "<actual purpose>" --limit 10 --output <manifest.json>`

Render the shortlist into the host-native interactive UI. Do not first answer with a prose list of template ids.

The picker must:
- show 5–10 relevant real registered candidates when available;
- use actual registered representative previews;
- expose recommendation reasons;
- allow card/page navigation;
- preserve a tentative selected state;
- expose Free Design separately;
- permit return to other templates.

Default recommendation display target is 6; up to 10 candidates may be shown when useful.

## Stage 2 — selected-template detail

After a tentative card choice, show up to 6 real examples from that exact workspace:
- Cover
- TOC / Section
- Content
- Data / Chart
- Comparison / Before-After
- Ending

The Stage-1 choice is tentative. Do not write selection evidence yet.

## Stage 3 - mandatory presentation-production preset

Present 3-5 purpose-ranked production presets for every new deck unless the user already provided a valid preset id. Examples include Balanced Report, Executive Brief, Storytelling Proposal, Data Insight, Training & Guide, and Product/Service Showcase.

The template and preset are separate decisions. A recommended combination may be highlighted but never auto-confirmed. On developer-MCP fallback, use `production_preset_picker.py` or `ops/windows/Open_SlideMasterPreset_Fallback.bat`.

## Stage 4 — final confirmation

Display a final selection token such as:

`deck:mckinsey | preset:storytelling_proposal`

If the interactive UI's state is local to the app, instruct the user to return/confirm the template id in chat.
Only explicit user confirmation of both template and preset is final.

## Picker render evidence

After the visible picker renders, record its surface:

`python .claude/skills/ppt-master/scripts/picker_surface_gate.py record <picker.json> --surface app_block --purpose "<purpose>" --source-ref "github:main" --candidate-count <n> --detail-preview-max 6 --rendered`

For `genui`, use `--surface genui`.

If App Block / GenUI is unavailable, use the fallback hierarchy below. Every non-primary surface requires `--fallback-reason "<why primary could not be used>"`.

## Final selection evidence

Recommended-template flow:

`python .claude/skills/ppt-master/scripts/record_template_choice_v2.py <deck:id|layout:id|free> --preset <preset_id> --purpose "<purpose>" --picker-evidence <picker.json> --output <result.json> --confirmed`

Direct user-specified template flow:

`python .claude/skills/ppt-master/scripts/record_template_choice_v2.py <deck:id|layout:id|free> --preset <preset_id> --purpose "<purpose>" --direct-template --output <result.json> --confirmed`

Only after the gate-v3 template+preset record succeeds may research begin. After research, present a slide-by-slide storyline/content outline and wait for explicit approval. Only after that approval initialize through:

`python .claude/skills/ppt-master/scripts/new_deck_init.py <project_name> --format <format> --template-selection-result <result.json>`

Then continue generation.

## Fallback hierarchy

Use this exact order while preserving the same stage sequence:

1. conversation-native interactive App Block / GenUI;
2. on developer-MCP `FORBIDDEN`, Desktop Commander self-contained template HTML;
3. production preset HTML immediately after the template id;
4. another conversation-native real-preview visual/card surface when available;
5. stable GitHub-rendered visual catalog;
6. text-only ids as last resort.

A lower-priority path requires a recorded fallback reason. No fallback may bypass explicit template choice, preset choice, research/storyline review, or user approval.

## Self-contained HTML fallback contract

When the HTML fallback is needed, build:

`python .claude/skills/ppt-master/scripts/template_gallery_inline_html.py --source github --purpose "<actual purpose>" --page-size 12 --output <gallery.html>`

It must remain self-contained, embed real registered previews, provide search/filters/pagination, Free Design, card detail modal, up to 6 exact examples, and final selected-id display.

## Korean rendering

Never present broken glyph boxes as valid previews. Use a verified Korean-capable font stack or safe English sample tokens inside raster previews with Korean labels outside.

## Hard failures

Stop rather than proceed when any of these occurs:

- research starts before template+preset evidence;
- generation starts before storyline approval;
- a fixed/hard-coded template list replaces the current GitHub indexes;
- App Block / GenUI is available but the assistant answers with only names/ids;
- only names/numbers are shown and treated as a completed visual selection step;
- a static PNG is represented as interactive UI;
- real registered previews are missing;
- selected-template detail review is skipped for recommendation flows;
- picker evidence is missing for a recommended-template final record;
- a fallback is used without its reason;
- final evidence is written before explicit template + preset confirmation;
- broken Korean glyphs are visible;
- valid selection evidence is missing.

## Downstream enforcement

`picker_surface_gate.py`, `template_selection.json`, `template_gate.py`, `new_deck_init.py`, and guarded `svg_to_pptx.py` remain fail-closed. The UI change strengthens rather than weakens the FAH `TEMPLATE_SELECTION` contract.

## User-editable slide-by-slide preview gate ? 2026-08-30
Before any new-deck project initialization or slide authoring, present the **full proposed slide sequence** in chat (or an equivalent visible review surface). Every slide preview must show: slide number, title, core message, 2?5 main content points, and proposed visual/layout treatment. The user may delete, add, merge, split, reorder, retitle, rewrite, change visuals, or request a new total slide count (including 20/30+). Apply those edits to the preview and show the revised affected slides or full sequence as appropriate.

Generation permission requires the user to explicitly approve the **current revision**. Record that exact approved snapshot through `storyline_gate.py`; `new_deck_init.py` requires both `--template-selection-result` and `--storyline-approval-result`. If the storyline changes after approval, the old approval is stale and generation must stop until the revised preview is approved again. `validate_spec.py` checks the generated ?IX slide count/titles/core messages against the approved snapshot, and gate-v3 SVG export is blocked without storyline approval evidence.
