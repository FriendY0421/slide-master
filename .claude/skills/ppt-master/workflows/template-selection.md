---
description: Mandatory scalable inline-interactive template-selection gate for new Slide Master decks
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

## Host preparation is not generation permission

A ChatGPT host may require `artifact_handoff` / presentation preparation before any other tool call. That call is **preparation only**. Immediately after it, enter this template-selection workflow. Do not research, initialize a project, author slides, or export PPTX until valid template-selection evidence exists.

## Runtime catalog — latest GitHub every request

Use the unified index-driven catalog:

`template_catalog.py`

It merges registered:
- Decks from `templates/decks/decks_index.json`
- Layouts from `templates/layouts/layouts_index.json`

Do not hard-code template ids or counts. New/updated registered entries must appear automatically on the next PPT request.
Use collision-safe keys `deck:<id>` / `layout:<id>`.

For FriendY production PPT requests, refresh from GitHub `main` rather than silently relying on a stale local catalog.

## ChatGPT primary flow — SELF-CONTAINED INTERACTIVE HTML IN THE CONVERSATION

The canonical selection surface is the **self-contained HTML gallery rendered interactively inside the ChatGPT conversation body**, matching the user-approved `preview(1).html` UX.

Build it with:

`python .claude/skills/ppt-master/scripts/template_gallery_inline_html.py --source github --purpose "<actual purpose>" --page-size 12 --output <gallery.html>`

Then surface that HTML artifact in the same conversation. **Stop there.** Do not continue presentation generation until the user completes selection in the gallery and returns the selected id in chat.

### Inline HTML UI contract

The generated gallery must:

- be self-contained; no localhost server dependency;
- embed real registered SVG previews and package-local assets as data URIs;
- show purpose-aware recommendations without auto-selecting;
- expose the complete current GitHub registered catalog;
- provide search by name/summary/id;
- provide Deck/Layout filters;
- paginate automatically when many templates exist (default 12 cards/page; presentation may adapt for usability);
- provide Free Design separately;
- open a clicked card in an in-page modal/dialog;
- show up to 6 real examples from the exact selected workspace;
- include `다른 템플릿 보기` and `이 템플릿 선택` controls;
- display the final selected name/id at the top after confirmation;
- tell the user to send the selected id back into chat.

The UI pattern is fixed semantically, not visually: `gallery cards → click → detail modal → up to six real examples → 이 템플릿 선택 → selected id shown`. Styling may evolve as long as this interaction remains clear and polished.

## Selection evidence

The HTML button `이 템플릿 선택` is the final UI confirmation. When the user sends the selected id back in chat, record:

`python .claude/skills/ppt-master/scripts/record_template_choice_v2.py <deck:id|layout:id|free> --purpose "<purpose>" --output <result.json> --confirmed`

Then initialize:

`python .claude/skills/ppt-master/scripts/new_deck_init.py <project_name> --format <format> --template-selection-result <result.json>`

Only after this succeeds may research/generation continue.

## Korean rendering

The inline HTML should preserve Korean text whenever the browser artifact can render the declared Korean-capable font stack. Never present broken glyph boxes as valid previews. Registered SVG content remains the design source; do not recreate approximate thumbnails.

## Fallback hierarchy

Use this exact order:

1. **Primary:** self-contained interactive HTML artifact inside the current ChatGPT conversation (`template_gallery_inline_html.py`).
2. **Secondary:** conversation-native static/visual two-stage gallery only if the host cannot render the HTML artifact interactively.
3. **Auxiliary last fallback:** external/local browser server (`template_gallery_unified.py`) only when both internal conversation surfaces are unavailable or recovery explicitly requires it.

The external browser path must never become the default merely because its controls are richer.

## Hard failures

Stop rather than proceed when any of these occurs:

- PPT generation starts after `artifact_handoff` but before template evidence;
- a fixed/hard-coded template list is used instead of current GitHub indexes;
- only names/numbers are shown;
- Markdown `<img>` links are used as a substitute for the approved interactive gallery;
- a static PNG is represented as interactive UI;
- real registered previews are missing;
- selected-template detail examples are skipped;
- final evidence is written before the gallery's final selection is returned in chat;
- broken Korean glyphs are visible;
- valid selection evidence is missing.

## Downstream enforcement

`template_selection.json`, `template_gate.py`, `new_deck_init.py`, and guarded `svg_to_pptx.py` remain fail-closed. The selection-surface changes do not weaken the FAH `TEMPLATE_SELECTION` contract.
