# PPT Request Guard — Mandatory New-Deck Entry Gate

This file is the shortest fail-closed authority for every **new presentation deck** request. It exists so template selection does not depend on model memory or conversational recall.

## Non-negotiable entry sequence

1. Read `workflows/routing.md` and this guard before any new-deck research, project initialization, SVG authoring, or PPTX export.
2. If the user already explicitly chose a valid registered deck id/workspace, record that choice through `record_template_choice.py`.
3. Otherwise launch `template_gallery_context.py` in HTML/GUI mode with the user's actual purpose/context text and keep the task alive until it returns `TEMPLATE_SELECTED`. If local/remote desktop execution is available, actually execute the launcher; do not substitute a prose list. On Windows or any host where non-ASCII CLI text may be damaged, write the purpose to a UTF-8 file and pass `--purpose-file <path>`.
4. The HTML gallery shows the complete live registered catalog plus Free Design, grouped by use category. The normal selection-ready catalog target is at least 10 registered templates so the user can compare roughly ten real designs with previews.
5. Recommend only templates that genuinely fit the user's purpose and context, **up to 10**. Do not fill a quota. Use relative relevance so weak secondary matches are not recommended merely because they share a broad category.
6. Free Design is valid only when the user explicitly chooses it.
7. New-deck project initialization must use `new_deck_init.py` with template-selection evidence. Missing selection evidence is a hard failure.
8. `svg_to_pptx.py` validates the project gate again before export. A missing or invalid gate blocks PPTX generation even if an earlier conversational step was skipped.

## Context-aware catalog

Template metadata in `templates/decks/decks_index.json` owns discovery fields:
- `primary_category`: main display group
- `categories`: additional use groups
- `keywords`: purpose/context matching terms

Stable category ids include `report`, `education`, `notice`, `presentation`, `proposal`, `data`, `brand_story`, `product`, and `general`. The gallery may add more categories later without changing this gate, but every new registered deck should declare a sensible primary category and matching keywords.

## Fail-closed rule

No `template_selection.json` (selected or approved route exemption) means the project did not pass the entry gate.

Do not replace the HTML/GUI picker with a plain text list unless the picker truly cannot run in the host environment. Do not silently select a recommended template on the user's behalf.
