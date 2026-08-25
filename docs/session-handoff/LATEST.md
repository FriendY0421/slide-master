# Latest project handoff

Updated checkpoint: 2026-08-25 12:19 KST

## NEWEST CHECKPOINT — TEMPLATE SELECTION V2 E2E VALIDATED

The scalable Template Selection V2 path has now been **executed end to end on HOME-PC**, not merely documented.

- local clone was clean and safely fast-forwarded to current `origin/main`;
- Python syntax checks passed for all new V2 runtime scripts;
- live unified catalog detected 11 currently registered templates from Deck + Layout indexes;
- Stage 1 generated exactly 10 candidates and every candidate had a real registered preview;
- Layout templates were verified as first-class selectable candidates;
- Stage-1-only selection could not create evidence without `--confirmed`;
- confirmed `layout:ai_ops` selection recorded the correct namespaced key and workspace;
- `new_deck_init.py` consumed that V2 selection record successfully;
- `template_gate.py validated passed on the resulting project;
- unified HTML mode reported 11 registered / 10 shortlisted and started successfully;
- HTTP checks returned `200` for the gallery page, a Deck preview, and a Layout preview;
- the accepted FAH execution contract remains unchanged at runtime @45 / SHA `d8c24c26460cded0fe947df75b2e278488fd7641`;
- no GitHub Actions were used.

Durable history: `docs/ai-history/2026-08-25-template-selection-v2-e2e-validated.md`

Expected production flow remains:

`PPT request → FAH gate → index-driven Deck+Layout catalog → 10 real Stage-1 previews when available → tentative choice → up to 6 real detail previews → final confirmation → selection evidence → new_deck_init → template gate → generation/QA/PPTX`

---

## NEWEST CHECKPOINT — TEMPLATE SELECTION V2 SCALABLE

The prior chat-first/visual-render corrections identified the right UX goal but still left structural gaps: the picker remained Deck-only, `up to 10 recommendations` was confused with actually showing 10 candidates, a static PNG was incorrectly used as a substitute for clickable selection UI, selected-template detail review was not enforced, and Korean raster previews could break when the rendering host lacked Korean fonts.

V2 is now the canonical FriendY new-PPT template-selection architecture.

### Scalable catalog

- `.claude/skills/ppt-master/scripts/template_catalog.py` merges registered Deck and Layout indexes.
- Deck source: `.claude/skills/ppt-master/templates/decks/decks_index.json`
- Layout source: `.claude/skills/ppt-master/templates/layouts/layouts_index.json`
- No current template ids/counts are hard-coded into discovery logic.
- New Deck/Layout registrations automatically become discoverable through their normal index.
- Collision-safe keys use `deck:<id>` / `layout:<id>`.
- At this checkpoint the repository happens to contain 4 Decks + 7 Layouts = 11 registered selectable templates, but that count is informational only and is not encoded into V2 behavior.

### ChatGPT two-stage flow

1. `template_gallery_chat_manifest_v2.py` builds the live context-ranked catalog.
2. When 10+ registered templates exist, Stage 1 must visibly show 10 real registered candidates. Free Design is separate.
3. The Stage-1 choice is tentative only.
4. Stage 2 must show up to 6 real examples from the tentative template workspace.
5. Only after the user sees those examples and explicitly confirms may `record_template_choice_v2.py --confirmed` write selection evidence.
6. Then `new_deck_init.py`, `template_gate.py`, and guarded `svg_to_pptx.py` continue the normal fail-closed pipeline.

### Clickable UI

- `.claude/skills/ppt-master/scripts/template_gallery_unified.py` is the canonical HTML/GUI picker when actual clickable cards/buttons are wanted or reliable chat rendering is unavailable.
- It uses the same unified Deck+Layout catalog, shows the 10-candidate shortlist, allows access to the full registered library, opens up to 6 real detail previews, and records final confirmation.
- A static image must never be described or treated as clickable UI.
- Legacy Deck-only HTML/chat V1 paths remain rollback/compatibility paths only and are not FriendY new-PPT execution authority.

### Korean preview safety

- Broken Korean glyphs are an invalid preview.
- Browser mode uses a Korean fallback font stack.
- For headless rasterization, Korean sample text may be used only when Korean font support is positively verified.
- Otherwise, use safe English sample tokens inside the actual template preview and keep Korean template names/explanations outside the image.

### Control-plane status

- `PPT_REQUEST_GUARD.md` and `workflows/template-selection.md` now point to V2.
- `AI_CONTEXT.md` and `AI_STATE.json` record V2 as the current authority.
- The accepted `.fah/execution-contract.json` remains intentionally unchanged: v1.0 / blob SHA `d8c24c26460cded0fe947df75b2e278488fd7641` / FAH runtime @45 `CONTRACT_CURRENT`.
- GitHub Actions were not used.
- HOME-PC ping passed; command-based runtime execution is not claimed because subsequent terminal/file-search calls were intermittently unresponsive and were not repeatedly forced.

Durable history: `docs/ai-history/2026-08-25-template-selection-v2-scalable.md`

Expected user-visible flow:

`PPT request → FAH gate → unified live Deck+Layout catalog → 10 real Stage-1 previews when available → tentative choice → up to 6 real detail examples → final confirmation → template_selection.json → research/generation → QA → PPTX`

---

## PREVIOUS CHECKPOINT — CHAT TEMPLATE VISUAL RENDER FAIL-CLOSED

The previous chat-first correction was directionally correct but still incomplete: a host could satisfy the policy in prose by listing template names/numbers without actually rendering the registered template visuals. That reproduced the user's original inconsistency.

The durable rule remains active:

- on ChatGPT and any conversational host capable of visual rendering, the template-selection prompt is **not considered displayed** unless actual registered previews are rendered for selectable templates presented to the user;
- template names/numbers alone are an explicit failure;
- prose descriptions alone are an explicit failure;
- asking for a choice before real previews appear is an explicit failure;
- approximated/recreated thumbnails are forbidden;
- selection evidence and downstream fail-closed guards remain mandatory.

This checkpoint is extended/superseded by V2 where it conflicts with Deck-only discovery or single-stage selection.

---

## PREVIOUS CHECKPOINT — CHAT-INLINE TEMPLATE GALLERY HARDENED

A new PPT request correctly reached the FAH `TEMPLATE_SELECTION` gate but did not show the chooser inside ChatGPT. Investigation confirmed that FAH runtime @45 and the execution contract were healthy. The defect was the host-specific selection surface.

The durable intent remains active: ChatGPT uses the conversation as the first visual surface, while true clickable card/button UI uses the unified HTML/GUI path when required. Legacy V1 helper names from this checkpoint are superseded by V2 for new FriendY PPT requests.

---

## Current authority

- project: `SLIDE_MASTER`
- repository: `FriendY0421/slide-master`
- management type: `GITHUB_CONTEXT`
- capabilities: `GITHUB_MONITOR, DURABLE_AUTHORITY, EXECUTION_CONTRACT`
- execution contract: `.fah/execution-contract.json` v1.0
- contract blob SHA: `d8c24c26460cded0fe947df75b2e278488fd7641`
- FAH central runtime: `@45`
- deployment capability for Slide Master: none
- auto deploy: `N`
- canonical template catalog: `template_catalog.py`
- canonical chat manifest: `template_gallery_chat_manifest_v2.py`
- canonical final recorder: `record_template_choice_v2.py`
- canonical clickable picker: `template_gallery_unified.py`

## GitHub Actions policy

GitHub Actions are default-off to conserve usage. They may be used only when the current user explicitly requests emergency deployment or explicitly requests GitHub Actions.
