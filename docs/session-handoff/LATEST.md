# Latest project handoff

Updated checkpoint: 2026-08-30 KST

## NEWEST CHECKPOINT — PICKER OPERATING BASELINE ACCEPTED

Cold-start after Windows reboot now passes. Local MCP readiness and full tools/picker/UI/resource/selection-validation smoke pass, and the user reports the Picker flow in a new normal ChatGPT conversation is operating normally. Full PPT file end-to-end completion is not yet claimed.

The user explicitly chose to keep the current foreground runtime model: keep both the Picker server CMD window (TCP 3000) and Secure MCP Tunnel CMD window (TCP 8080) running/minimized while the Picker/PPT workflow is in use. Do not convert to a background service unless requested later.

Do not repeat closed CSP/template/port/tunnel/startup-order/default-buffer diagnosis without new evidence. Classify any new failure by the stage that actually fails.

Durable operational history: `docs/ai-history/2026-08-30-picker-operational-baseline-final.md`

Durable handoff: `docs/session-handoff/20260830_PICKER_OPERATIONAL_BASELINE_FINAL.md`

GitHub Actions remain opt-in only. PR #6 remains Draft pending confirmed selection return and full PPT path.

---


Updated checkpoint: 2026-08-30 19:51 KST

## NEWEST CHECKPOINT — PICKER REBOOT FINAL ACCEPTANCE NEXT SESSION

Reboot-readiness hardening is committed on `feat/apps-sdk-template-picker-20260827` at `cc9cbdd7261443fcb2899e1deb024a2cc81ee673`. The remaining task is not another broad diagnosis; it is the final cold-start acceptance of the hardened fail-closed launcher.

Required next flow:
`restart Windows -> run Desktop Start_SlideMasterPicker.bat -> wait for [READY] -> issue exactly one ChatGPT Picker request`

Do not repeatedly retry before `[READY]`. If the launcher fails, capture its exact output/logs and diagnose the failed READY condition. If `[READY]` passes but ChatGPT still fails, move investigation to the Secure MCP Tunnel remote/host delivery path rather than restarting CSP/template/local-port analysis.

Durable handoff: `docs/session-handoff/20260830_PICKER_REBOOT_FINAL_ACCEPTANCE_NEXT_SESSION.md`

Detailed history: `docs/ai-history/2026-08-30-reboot-startup-readiness-hardening.md`

---

Updated checkpoint: 2026-08-30 KST

## NEWEST CHECKPOINT — REBOOT STARTUP READINESS HARDENED

A real Windows reboot reproduced `Failed to fetch template` during runtime warm-up, with repeated retries later surfacing 404/429 behavior. The launcher is now fail-closed and non-destructive: it never terminates an existing process, verifies an existing runtime first, starts new components only when ports 3000/8080 are free, and requires continuous stable health plus a real MCP smoke before `[READY]`.

Final cold-start acceptance is intentionally pending a user-controlled Windows restart after unrelated work is finished. Do not restart or terminate processes automatically.

Durable handoff: `docs/session-handoff/20260830_PICKER_REBOOT_READINESS_CHECKPOINT.md`

Detailed history: `docs/ai-history/2026-08-30-reboot-startup-readiness-hardening.md`

---
Updated checkpoint: 2026-08-30 KST

## NEWEST CHECKPOINT — PICKER CSP / HOST RENDER HARDENED

Local MCP + Secure Tunnel regression PASS after CSP/host-render hardening. Payload preparation and visible host UI are now separate states; stale port-3000 runtime detection is a mandatory first diagnostic. PR #6 remains Draft pending real ChatGPT visible-card/image + final app.sendMessage acceptance.

Durable handoff: docs/session-handoff/20260830_PICKER_CSP_HOST_RENDER_CHECKPOINT.md

Detailed history: docs/ai-history/2026-08-30-picker-csp-host-render-hardening.md

---

Updated checkpoint: 2026-08-27T20:33:59+09:00 KST

## NEWEST CHECKPOINT — MCP APPS PICKER LOCAL PROTOCOL VALIDATED

PR #6 (`feat/apps-sdk-template-picker-20260827`) implements the real conversation-native Slide Master picker. Local and GitHub-source MCP protocol smoke tests now pass.

Current state: `AWAITING_SECURE_TUNNEL_CREDENTIALS`.

Validated: build/check, payload, `/mcp` initialize, tools/list, picker call, `ui://slide-master/template-picker-v1.html`, server-side final selection validation, picker evidence, production preset persistence, direct-template compatibility. GitHub Actions were not used.

Remaining before merge: provision OpenAI Secure MCP Tunnel `CONTROL_PLANE_API_KEY` + `CONTROL_PLANE_TUNNEL_ID`, connect the MCP endpoint to ChatGPT Developer Mode, then verify the actual interactive UI plus `app.sendMessage` selection return. HOME-PC has no tunnel-client installed and the MCP server is stopped; no public endpoint was opened.

Durable history: `docs/ai-history/2026-08-27-apps-sdk-template-picker.md`

---

Updated checkpoint: 2026-08-27 KST

## NEWEST CHECKPOINT — COMPANY TEMPLATE LIFECYCLE VALIDATED

Company/user PPT/POTX/PDF/image/photo onboarding is now governed as `CANDIDATE → preview approval → ACTIVE`. Normal picker/recommendation inventory includes ACTIVE templates only; legacy entries without status remain ACTIVE for backward compatibility. Confidential company source files stay out of the public repository.

Validation: metadata passthrough PASS, ACTIVE/CANDIDATE filtering PASS, current catalog 11 total / 11 selectable / 0 inactive / shortlist 10, GitHub Actions not used.

Durable history: `docs/ai-history/2026-08-27-company-template-lifecycle.md`

---

Updated checkpoint: 2026-08-27 KST

## NEWEST CHECKPOINT — GPTS APP BLOCK PICKER FAIL-CLOSED

A real GPTS PPT request exposed a regression: it returned a prose template list instead of the approved interactive picker.

Current canonical rule: **App Block / GenUI first when available; never prose-first.**

Required flow:
`PPT request → artifact preparation if required → FAH → latest GitHub catalog → App Block/GenUI picker → real detail previews → user final selection → picker evidence → template_selection.json → generation/QA/PPTX`

Machine hardening:
- new `picker_surface_gate.py` records visible picker-surface evidence;
- recommendation flows require `record_template_choice_v2.py --picker-evidence`;
- direct user-specified templates use `--direct-template`;
- gate v1 remains valid for legacy/resume compatibility;
- non-primary picker surfaces require a fallback reason;
- FAH execution contract remains v1.0 / unchanged;
- GitHub Actions were not used.

Durable history: `docs/ai-history/2026-08-27-gpts-app-block-picker-fail-closed.md`

---

Updated checkpoint: 2026-08-25 17:13 KST

## NEWEST CHECKPOINT — INLINE INTERACTIVE HTML GALLERY CANONICAL

FriendY supplied the previously working `preview(1).html` and confirmed that this interaction model is the exact desired normal PPT template-selection experience.

The canonical ChatGPT selection surface is now:

**self-contained interactive HTML artifact rendered inside the current conversation**

Required user-visible flow:

`PPT request → artifact_handoff preparation if host-required → FAH WAIT_USER_ACTION → latest GitHub catalog → inline HTML gallery → card click → up to 6 real detail examples → 이 템플릿 선택 → selected id shown → user returns id in chat → template_selection.json → generation/QA/PPTX`

Durable rules:

- `artifact_handoff` is preparation only and never generation permission.
- `.claude/skills/ppt-master/scripts/template_gallery_inline_html.py` is the canonical primary picker for ChatGPT.
- Production gallery builds use `--source github`; every new PPT request refreshes from current `FriendY0421/slide-master` `main`.
- Deck/Layout discovery remains index-driven through `template_catalog.py`; no current ids/counts are hard-coded.
- New, updated, or removed registered templates automatically change the next generated gallery.
- The self-contained HTML embeds real registered SVG previews and package-local assets as data URIs; no localhost server is required.
- Recommended templates are shown separately but never auto-selected.
- The complete current registered library remains accessible.
- Large libraries use search + Deck/Layout filters + pagination; default is 12 cards/page.
- Card click opens an in-page dialog with up to 6 real registered examples from the exact workspace.
- The final UI action is `이 템플릿 선택`; the selected name/id is shown and returned to chat by the user.
- Only after that id returns may `record_template_choice_v2.py --confirmed` create evidence and `new_deck_init.py` proceed.
- External/local browser HTML (`template_gallery_unified.py`) is auxiliary last fallback only.
- Conversation-native static/visual two-stage display is secondary fallback only when the inline HTML artifact cannot render interactively.
- Markdown `<img>` lists and static PNGs are invalid substitutes for the approved gallery.

Durable history: `docs/ai-history/2026-08-25-inline-interactive-html-gallery-authority.md`

---

## PREVIOUS CHECKPOINT — INTERNAL CARD GALLERY PRIMARY

- ChatGPT internal card-style template gallery is the **primary and canonical** selection surface.
- External/local HTML/GUI gallery is **auxiliary fallback only** and must not become the normal first-choice path merely because it has richer click controls.
- Use HTML only when internal gallery rendering is unavailable/unreliable or a recovery case specifically requires it.
- Template Selection V2 E2E validation remains valid: unified Deck+Layout discovery, 10-candidate Stage 1, up to 6 detail previews, final confirmation, and downstream fail-closed gates are unchanged.
- Future template growth remains index-driven.

Durable history: `docs/ai-history/2026-08-25-internal-card-gallery-primary.md`

---

## PREVIOUS CHECKPOINT — TEMPLATE SELECTION V2 E2E VALIDATED

The scalable Template Selection V2 path has now been **executed end to end on HOME-PC**, not merely documented.

- local clone was clean and safely fast-forwarded to current `origin/main`;
- Python syntax checks passed for all new V2 runtime scripts;
- live unified catalog detected 11 currently registered templates from Deck + Layout indexes;
- Stage 1 generated exactly 10 candidates and every candidate had a real registered preview;
- Layout templates were verified as first-class selectable candidates;
- Stage-1-only selection could not create evidence without `--confirmed`;
- confirmed `layout:ai_ops` selection recorded the correct namespaced key and workspace;
- `new_deck_init.py` consumed that V2 selection record successfully;
- `template_gate.py validate` passed on the resulting project;
- unified HTML mode reported 11 registered / 10 shortlisted and started successfully;
- HTTP checks returned `200` for the gallery page, a Deck preview, and a Layout preview;
- the accepted FAH execution contract remains unchanged at runtime @45 / SHA `d8c24c26460cded0fe947df75b2e278488fd7641`;
- no GitHub Actions were used.

Durable history: `docs/ai-history/2026-08-25-template-selection-v2-e2e-validated.md`

Expected production flow remains:

`PPT request → FAH gate → index-driven Deck+Layout catalog → 10 real Stage-1 previews when available → tentative choice → up to 6 real detail previews → final confirmation → selection evidence → new_deck_init → template gate → generation/QA/PPTX`

---

## PREVIOUS CHECKPOINT — TEMPLATE SELECTION V2 SCALABLE

The prior chat-first/visual-render corrections identified the right UX goal but still left structural gaps: the picker remained Deck-only, `up to 10 recommendations` was confused with actually showing 10 candidates, a static PNG was incorrectly used as a substitute for clickable selection UI, selected-template detail review was not enforced, and Korean raster previews could break when the rendering host lacked Korean fonts.

V2 is now the canonical FriendY new-PPT template-selection architecture.

### Scalable catalog

- `.claude/skills/ppt-master/scripts/template_catalog.py` merges registered Deck and Layout indexes.
- Deck source: `.claude/skills/ppt-master/templates/decks/decks_index.json`
- Layout source: `.claude/skills/ppt-master/templates/layouts/layouts_index.json`
- No current template ids/counts are hard-coded into discovery logic.
- New Deck/Layout registrations automatically become discoverable through their normal index.
- Collision-safe keys use `deck:<id>` / `layout:<id>`.
- At this checkpoint the repository happened to contain 4 Decks + 7 Layouts = 11 registered selectable templates, but that count was informational only and is not encoded into V2 behavior.

### ChatGPT two-stage flow

1. `template_gallery_chat_manifest_v2.py` builds the live context-ranked catalog.
2. When 10+ registered templates exist, Stage 1 must visibly show 10 real registered candidates. Free Design is separate.
3. The Stage-1 choice is tentative only.
4. Stage 2 must show up to 6 real examples from the tentative template workspace.
5. Only after the user sees those examples and explicitly confirms may `record_template_choice_v2.py --confirmed` write selection evidence.
6. Then `new_deck_init.py`, `template_gate.py`, and guarded `svg_to_pptx.py` continue the normal fail-closed pipeline.

This previous conversational two-stage flow is now the **secondary fallback** when the canonical inline interactive HTML artifact cannot render.

### Clickable UI

- `.claude/skills/ppt-master/scripts/template_gallery_unified.py` remains the external/local browser picker for recovery/fallback.
- It uses the same unified Deck+Layout catalog, exposes the registered library, opens up to 6 real detail examples, and records final confirmation.
- A static image must never be described or treated as clickable UI.
- Legacy Deck-only HTML/chat V1 paths remain rollback/compatibility paths only and are not FriendY new-PPT execution authority.

### Korean preview safety

- Broken Korean glyphs are an invalid preview.
- Browser mode uses a Korean fallback font stack.
- For headless rasterization, Korean sample text may be used only when Korean font support is positively verified.
- Otherwise, use safe English sample tokens inside the actual template preview and keep Korean template names/explanations outside the image.

### Control-plane status

- `PPT_REQUEST_GUARD.md` and `workflows/template-selection.md` now point to the current selection authority.
- `AI_CONTEXT.md` records the current authority.
- The accepted `.fah/execution-contract.json` remains intentionally unchanged: v1.0 / blob SHA `d8c24c26460cded0fe947df75b2e278488fd7641` / FAH runtime @45 `CONTRACT_CURRENT`.
- GitHub Actions were not used.

Durable history: `docs/ai-history/2026-08-25-template-selection-v2-scalable.md`

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

This checkpoint is extended/superseded by the current inline interactive HTML authority where it conflicts.

---

## PREVIOUS CHECKPOINT — CHAT-INLINE TEMPLATE GALLERY HARDENED

A new PPT request correctly reached the FAH `TEMPLATE_SELECTION` gate but did not show the chooser inside ChatGPT. Investigation confirmed that FAH runtime @45 and the execution contract were healthy. The defect was the host-specific selection surface.

The durable intent remains active: ChatGPT uses the conversation as the first selection surface. The current implementation of that intent is the self-contained inline interactive HTML artifact.

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
- canonical ChatGPT interactive picker: `template_gallery_inline_html.py`
- canonical final recorder: `record_template_choice_v2.py`
- secondary conversational fallback: `template_gallery_chat_manifest_v2.py`
- auxiliary external/local browser fallback: `template_gallery_unified.py`

## GitHub Actions policy

GitHub Actions are default-off to conserve usage. They may be used only when the current user explicitly requests emergency deployment or explicitly requests GitHub Actions.

Implementation commit: `b0234dd281dd733a5bdbc05a3106e4ddf74df4eb`
