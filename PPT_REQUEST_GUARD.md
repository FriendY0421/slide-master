# PPT Request Guard — Mandatory New-Deck Entry Gate

This file is the shortest fail-closed authority for every **new presentation deck** request. It exists so template selection does not depend on model memory or conversational recall.

## Canonical entry routing — FIRST GATE

For every FriendY presentation creation request, including generic phrases such as `PPT 만들어줘`, `ppt로 만들어줘`, `프레젠테이션 만들어줘`, `슬라이드 만들어줘`, or a request to turn a URL/document/topic into a deck:

1. Bind the task to project `SLIDE_MASTER` and canonical repository `FriendY0421/slide-master` **before** any presentation research, SVG generation, project initialization, or PPTX export.
2. Do **not** use the upstream `byungjunjang/slide-master` repository as FriendY's execution authority. It may be treated only as external/upstream reference when explicitly needed.
3. Evaluate the FAH Execution Contract before presentation execution when FAH is available. If FAH evaluation is unavailable, read `.fah/execution-contract.json` directly as the durable fallback.
4. Only `ALLOW` or the route-specific documented `EXEMPT` decision may proceed. `WAIT_USER_ACTION`, `BLOCK`, missing evaluation, or missing required evidence must stop execution.
5. A host-native slide/PPT skill, artifact handoff, generic presentation generator, or earlier conversational shortcut must **not** bypass this canonical repository lock or the FAH gate.

This routing rule exists specifically to prevent a new PPT request from entering an upstream/generic generation path before FriendY's FAH-controlled template-selection handshake.

## Non-negotiable entry sequence

1. Read `workflows/routing.md` and this guard before any new-deck research, project initialization, SVG authoring, or PPTX export.
2. If the user already explicitly chose a valid registered deck id/workspace, record that choice through `record_template_choice.py`.
3. Otherwise launch `template_gallery_context.py` in HTML/GUI mode with the user's actual purpose/context text and keep the task alive until it returns `TEMPLATE_SELECTED`.
4. The HTML gallery shows the complete live registered catalog plus Free Design, grouped by use category.
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
