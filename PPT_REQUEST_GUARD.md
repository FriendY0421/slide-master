# PPT Request Guard — Mandatory New-Deck Entry Gate

This file is the shortest fail-closed authority for every **new presentation deck** request. It exists so template selection does not depend on model memory or conversational recall.

## Non-negotiable entry sequence

1. Read `workflows/routing.md` and this guard before any new-deck research, project initialization, SVG authoring, or PPTX export.
2. If the user already explicitly chose a valid registered deck id/workspace, record that choice through the template selection utility.
3. Otherwise launch `template_gallery.py` in HTML/GUI mode and keep the task alive until it returns `TEMPLATE_SELECTED`.
4. The HTML gallery shows the complete live registered catalog plus Free Design, grouped by use category.
5. Recommend only templates that genuinely fit the user's purpose and context, **up to 10**. Do not fill a quota.
6. Free Design is valid only when the user explicitly chooses it.
7. New-deck project initialization must carry template-selection evidence. Missing selection evidence is a hard failure.

## Context-aware catalog

Template metadata in `templates/decks/decks_index.json` owns discovery fields:
- `primary_category`: main display group
- `categories`: additional use groups
- `keywords`: purpose/context matching terms

Stable category ids include `report`, `education`, `notice`, `presentation`, `proposal`, `data`, `brand_story`, `product`, and `general`. The gallery may add more categories later without changing this gate, but every new registered deck should declare a sensible primary category and matching keywords.

## Fail-closed rule

No `template_selection.json` (selected or approved route exemption) means the project did not pass the entry gate.

Do not replace the HTML/GUI picker with a plain text list unless the picker truly cannot run in the host environment. Do not silently select a recommended template on the user's behalf.
