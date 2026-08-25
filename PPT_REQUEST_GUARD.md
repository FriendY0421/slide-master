# PPT Request Guard — Mandatory New-Deck Entry Gate

This file is the fail-closed authority for every **new presentation deck** request.

## Canonical entry routing

For every FriendY new PPT/presentation/slides request:

1. Bind first to project `SLIDE_MASTER` and repository `FriendY0421/slide-master`.
2. A host-required `artifact_handoff` / presentation-preparation call may occur first because the ChatGPT host requires it, but that call is **preparation only**. It is not template selection, not FAH `ALLOW`, and never permission to create a PPTX.
3. Evaluate the FAH Execution Contract before research, project initialization, SVG authoring, or PPTX export.
4. Missing `TEMPLATE_SELECTION` evidence is `WAIT_USER_ACTION` and must stop generation.
5. Upstream `byungjunjang/slide-master`, generic slide generators, host-native artifact shortcuts, or a successful `artifact_handoff` call must not bypass this gate.

**Hard interpretation:** `artifact_handoff = prepare`; valid `template_selection.json = permission to generate`.

## Scalable live template catalog — never hard-code ids or counts

Template discovery is **GitHub-index-driven**. The production gallery must be rebuilt for every new PPT request from the latest `FriendY0421/slide-master` `main` state.

Canonical catalog sources:

- `.claude/skills/ppt-master/templates/decks/decks_index.json`
- `.claude/skills/ppt-master/templates/layouts/layouts_index.json`
- unified by `.claude/skills/ppt-master/scripts/template_catalog.py`

Adding, updating, or removing a registered Deck/Layout in the normal GitHub indexes must automatically change the next generated gallery without picker-code edits.

Selection keys are collision-safe:

- `deck:<id>`
- `layout:<id>`

Existing bare Deck ids remain backward-compatible only when unambiguous.

## ChatGPT canonical surface — INLINE SELF-CONTAINED INTERACTIVE HTML

For ChatGPT, the **primary/canonical template-selection surface is the self-contained interactive HTML artifact rendered inside the conversation body**, matching the user-approved `preview(1).html` interaction pattern.

Generate it with:

`template_gallery_inline_html.py --source github --purpose "<actual purpose>" --page-size 12 --output <gallery.html>`

`--source github` is the production default so GitHub refresh failure stops the normal path rather than silently showing a stale local catalog.

The inline HTML must be self-contained: registered SVG previews and package-local assets are embedded as data URIs; no localhost server or external browser is required for the primary path.

### Required visible behavior

The inline gallery must provide all of the following in one interactive surface:

1. Purpose-aware **recommended templates** at the top. Recommendation never auto-selects.
2. **All currently registered GitHub templates**, not a fixed historical list.
3. Search across template name, summary and selection id.
4. Deck/Layout filters.
5. Automatic pagination when the catalog is large; default is **12 cards per page** and may adapt for usability.
6. Free Design as a separate explicit option.
7. Each template card shows a real registered representative preview.
8. Clicking a card opens an in-page dialog/modal with up to **6 real registered examples** from that exact workspace.
9. The modal contains **`이 템플릿 선택`** and **`다른 템플릿 보기`** controls.
10. Final selection displays the selected name/id in the HTML. The user then sends that id back to the chat, which is the explicit handoff for evidence recording.

This UI contract is modeled on the user-approved `preview(1).html`: card grid → card click → detail dialog → up to six example layouts → `이 템플릿 선택` → selected id displayed.

## Selection evidence and generation permission

A card click is not enough. The HTML's **`이 템플릿 선택`** action is the final UI confirmation. After the selected id is returned in chat, record it through:

`record_template_choice_v2.py <deck:id|layout:id|free> --confirmed --purpose "<purpose>" --output <result.json>`

Then initialize only through:

`new_deck_init.py <project_name> --template-selection-result <result.json>`

Only after this evidence exists may content research/generation begin.

## Fail-closed UI rules

The following are explicit failures and must stop the new-deck pipeline:

- generating PPTX immediately after `artifact_handoff`;
- showing only template names/numbers;
- showing a static PNG while calling it an interactive gallery;
- using Markdown `<img>` links as a substitute for the approved gallery;
- using a fixed/hard-coded template list that ignores current GitHub indexes;
- omitting real registered previews;
- skipping the selected template's detail examples;
- recording selection before the final HTML selection action is returned to chat;
- broken Korean glyphs;
- creating/researching the deck while the user is still choosing a template.

## Fallback hierarchy

Use these surfaces in this order:

1. **Primary:** self-contained interactive HTML rendered inside the ChatGPT conversation (`template_gallery_inline_html.py`).
2. **Secondary:** conversation-native visual two-stage gallery only when the host cannot render the inline HTML artifact.
3. **Auxiliary last fallback:** external/local browser HTML server (`template_gallery_unified.py`) only when the internal conversation surfaces are technically unavailable or a recovery case specifically requires it.

External HTML/GUI must never become the normal first-choice route merely because it offers richer browser controls.

## Fail-closed evidence

No valid `template_selection.json` (selected or documented exemption) means the new-deck gate did not pass. `template_gate.py`, `new_deck_init.py`, and guarded `svg_to_pptx.py` remain the downstream enforcement layer.
