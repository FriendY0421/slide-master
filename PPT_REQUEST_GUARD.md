# PPT Request Guard — Mandatory New-Deck Entry Gate

This file is the fail-closed authority for every **new presentation deck** request.

## Canonical entry routing

For every FriendY new PPT/presentation/slides request:

1. Bind first to project `SLIDE_MASTER` and repository `FriendY0421/slide-master`.
2. Evaluate the FAH Execution Contract before research, project initialization, SVG authoring, or PPTX export.
3. Only `ALLOW` or a documented route `EXEMPT` may proceed. Missing `TEMPLATE_SELECTION` evidence is `WAIT_USER_ACTION` and must stop execution.
4. Upstream `byungjunjang/slide-master`, generic slide generators, and host-native artifact shortcuts must not bypass this gate.

## Scalable template catalog — no fixed template ids

Template discovery must be **index-driven**, never hard-coded to today's template names or counts.

Canonical runtime catalog:

- `.claude/skills/ppt-master/templates/decks/decks_index.json`
- `.claude/skills/ppt-master/templates/layouts/layouts_index.json`
- unified by `.claude/skills/ppt-master/scripts/template_catalog.py`

Adding a new registered Deck or Layout to its normal index must make it discoverable automatically without editing picker code.

Selection keys are namespaced to avoid future collisions:

- `deck:<id>`
- `layout:<id>`

Existing bare Deck ids remain backward-compatible only when they resolve unambiguously.

## ChatGPT canonical flow — TWO STAGES

On ChatGPT and other conversational hosts, do **not** pretend a static image is a clickable picker.

Use this deterministic flow:

### Stage 1 — shortlist

1. Read the unified live catalog using `template_gallery_chat_manifest_v2.py` or equivalent connected-GitHub reads.
2. Rank templates by the user's actual PPT purpose.
3. When at least 10 registered templates exist, visibly render **10 real registered template previews** in the conversation. When fewer than 10 exist, render all and state the actual count.
4. `Free Design` is separate from the 10 registered-template shortlist.
5. Mark genuinely relevant items as recommended, but never auto-select.
6. Receive only a **tentative** user choice at this stage.

### Stage 2 — detail review

1. For the tentative choice, render up to **6 actual registered layout examples** from that exact workspace: cover/title, agenda/section, content, data/KPI, comparison/visual, closing where available.
2. The user must be able to inspect those real examples before final confirmation.
3. Ask for final confirmation such as `이걸로 진행`.
4. Do not create template-selection evidence merely because the Stage-1 number/name was chosen.

### Stage 3 — evidence

After final confirmation only, record the choice with:

`record_template_choice_v2.py <deck:id|layout:id|free> --confirmed ...`

Then initialize through `new_deck_init.py --template-selection-result <result.json>`.

## Visual-render enforcement — FAIL CLOSED

The following are explicit failures:

- template names/numbers without real visual previews;
- fewer than 10 registered candidates when 10+ are available, unless the user explicitly asks for fewer;
- recreated/approximate thumbnails instead of the registered SVG source;
- treating a static PNG as a clickable selection widget;
- skipping the selected template's detail examples;
- recording the selection before final Stage-2 confirmation;
- showing broken Korean glyphs.

For raster/headless rendering, Korean preview text may be used only when a Korean-capable font is positively available. Otherwise use safe English sample tokens **inside the template preview** and keep Korean names/explanations outside the image. Never show missing-glyph boxes as a valid preview.

## HTML/GUI mode

When the user wants clickable cards/check states/buttons, or when reliable in-chat visual rendering is unavailable, use:

`template_gallery_unified.py`

This unified HTML picker uses the same Deck+Layout catalog, shows the context-ranked shortlist, allows access to the full registered library, opens up to six real detail previews, and records the final confirmed selection.

Do not use the legacy Deck-only HTML picker as the canonical path. Legacy scripts may remain temporarily for rollback/compatibility but are not execution authority for FriendY new-PPT requests.

## Fail-closed evidence

No valid `template_selection.json` (selected or documented exemption) means the new-deck gate did not pass. `template_gate.py`, `new_deck_init.py`, and guarded `svg_to_pptx.py` remain the downstream enforcement layer.
