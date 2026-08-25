# Latest project handoff

Updated checkpoint: 2026-08-25 10:31 KST

## NEWEST CHECKPOINT — CHAT-INLINE TEMPLATE GALLERY HARDENED

A new PPT request correctly reached the FAH `TEMPLATE_SELECTION` gate but did not show the chooser inside ChatGPT. Investigation confirmed that FAH runtime @45 and the execution contract were healthy. The root cause was the lower-level Slide Master presentation-surface policy: `template-selection.md`, `AGENTS.md`, and `CLAUDE.md` still treated the external/local HTML gallery as the normal path and chat as fallback.

The durable correction is now complete:

- ChatGPT and other conversational hosts with visual-rendering capability use the **current conversation as the canonical template-selection surface**;
- the host retrieves the live registered Slide Master catalog and the exact registered SVG previews, then renders those real previews directly in the conversation;
- `.claude/skills/ppt-master/scripts/template_gallery_chat_manifest.py` was added to expose context ranking, exact workspace paths, representative SVG paths, and up to six real layout previews without opening a browser;
- recommendations remain contextual and capped at 10 without filling a quota;
- recommendations never auto-select and `Free Design` remains explicit opt-in;
- after an in-chat user choice, `record_template_choice.py` records the normal machine-readable selection result and `new_deck_init.py` creates `template_selection.json` evidence;
- external/local `template_gallery_context.py` HTML/GUI is now **fallback only** when the current host cannot render the real previews inline;
- a plain text catalog is last resort only when neither visual surface is technically possible;
- `template_gate.py`, `new_deck_init.py`, and guarded `svg_to_pptx.py` continue to fail closed exactly as before.

The accepted `.fah/execution-contract.json` was intentionally **not changed**. Its v1.0 blob SHA remains `d8c24c26460cded0fe947df75b2e278488fd7641`, preserving FAH runtime @45 `CONTRACT_CURRENT` identity. No GitHub Actions were used and no FAH deployment/runtime version was created for this correction.

Validation:

- new chat-manifest helper Python syntax: PASS;
- template-selection evidence contract: unchanged;
- final export fail-closed guard: unchanged;
- FAH execution contract version/SHA: unchanged;
- GitHub Actions: not used.

Durable history: `docs/ai-history/2026-08-25-chat-inline-template-gallery.md`

Expected user-visible flow:

`PPT request → FriendY0421/slide-master lock → FAH contract evaluation → live registered template previews inside the same ChatGPT conversation → relevant recommendations → user explicit selection → template_selection.json evidence → content analysis/research → deck generation → quality verification → PPTX handoff`

---

## PREVIOUS CHECKPOINT — PPT ENTRY ROUTING HARDENED

A ChatGPT presentation request previously entered upstream `byungjunjang/slide-master` before FriendY's FAH/Slide Master gate was evaluated. The existing FAH runtime @45 Execution Contract and local Slide Master fail-closed guards were healthy; the defect was at the earlier project/repository entry-routing layer.

The durable correction remains active:

- every FriendY new-PPT/presentation/slides request binds first to project `SLIDE_MASTER` and canonical repository `FriendY0421/slide-master`;
- upstream `byungjunjang/slide-master` must not be used as FriendY's execution authority;
- generic/host-native presentation generation must not bypass the canonical repository lock or FAH contract;
- FAH Execution Contract evaluation occurs before presentation research/generation;
- `CREATE_PRESENTATION` still requires the blocking `TEMPLATE_SELECTION` user-interaction gate;
- only after explicit selection may research, project initialization, SVG authoring, and PPTX generation proceed;
- existing `template_gate.py`, `new_deck_init.py`, and guarded `svg_to_pptx.py` remain the final local fail-closed layer.

Durable history: `docs/ai-history/2026-08-25-ppt-entry-routing-hardening.md`

---

## Current authority

- project: `SLIDE_MASTER`
- repository: `FriendY0421/slide-master`
- management type: `GITHUB_CONTEXT`
- capabilities: `GITHUB_MONITOR, DURABLE_AUTHORITY, EXECUTION_CONTRACT`
- execution contract: `.fah/execution-contract.json` v1.0
- contract blob SHA: `d8c24c26460cded0fe947df75b2e278488fd7641`
- FAH central runtime: `@45`
- FAH deployed source: `584412f8307cd9675a78f384684bee1152a5c1fe`
- deployment capability for Slide Master: none
- auto deploy: `N`

## Final production acceptance

FAH natural monitor `DEPLOY_LOG` row 754 at `2026-08-24 23:33:32 KST` returned:

- `HEALTHY`
- `ACCEPTED_AUTHORITY_CURRENT`
- `alertWorthy=false`
- capability `EXECUTION_CONTRACT` present
- execution contract `available=true`, `valid=true`, `declared=true`
- contract status `CONTRACT_CURRENT`
- contract SHA/version exactly match durable `AI_STATE.json`
- `requiresReconciliation=false`

The Slide Master Execution Contract rollout is therefore accepted in the FAH control plane. The 2026-08-25 chat-inline correction changes only the host-specific selection surface and does not change that contract identity.

## Execution safety model

Layer A is the FAH central execution contract gate. `CREATE_PRESENTATION` cannot proceed before `TEMPLATE_SELECTION`; valid evidence permits `ALLOW`, missing user interaction returns `WAIT_USER_ACTION`, and invalid evidence returns `BLOCK`. `BEAUTIFY_PRESENTATION` remains an explicit `EXEMPT` route.

Layer B is the existing Slide Master local fail-closed guard. `template_gate.py`, `new_deck_init.py`, and guarded `svg_to_pptx.py` remain authoritative for final local enforcement and were not replaced.

Layer 0 is the canonical presentation-entry lock: any FriendY new-deck request first resolves to `FriendY0421/slide-master` and then evaluates FAH. The host-aware UI rule now defines the conversation-inline visual gallery as the preferred selection surface on ChatGPT and similar conversational hosts.

## Validation completed

- FAH execution-contract logic tests: PASS.
- Issue #42 durable-authority and comparator regression tests: PASS.
- missing template selection at export: `EXPORT BLOCKED` PASS.
- `beautify-pptx` exemption record/validation: PASS.
- project without a declared contract remains legacy-compatible.
- FAH @45 source HEAD readback: PASS.
- existing FAH Deployment @45 readback: PASS.
- natural FAH monitor contract-health acceptance: PASS.
- canonical repository entry rule: documented and durable.
- chat-first template-selection surface: documented and durable.
- `template_gallery_chat_manifest.py` syntax: PASS.

## Non-blocking optional follow-up

The owner-only Web POST smoke route is deployed. Direct credential-bearing HTTP execution is blocked by the current remote-tool security layer, so that transport smoke test is not claimed. Do not weaken credential security or create another runtime version solely for this tooling limitation. It may be tested later through an authorized non-secret-leaking transport.

## GitHub Actions policy

GitHub Actions are default-off to conserve usage. They may be used when the current user explicitly requests emergency deployment or explicitly requests GitHub Actions.

## Durable history

Newest:
- `docs/ai-history/2026-08-25-chat-inline-template-gallery.md`
- `docs/ai-history/2026-08-25-ppt-entry-routing-hardening.md`

Previous accepted contract rollout:
- `docs/ai-history/2026-08-25-execution-contract-runtime45-accepted.md`

No blocking runtime rollout action remains.