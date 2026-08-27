# AI Context

This repository participates in FriendY Automation Hub (FAH) control-plane continuity.

- Project ID: `SLIDE_MASTER`
- Repository: `FriendY0421/slide-master`
- FAH capabilities: `GITHUB_MONITOR, DURABLE_AUTHORITY, EXECUTION_CONTRACT`
- Technical source of truth remains this repository.
- `AI_STATE.json` is the machine-readable durable authority used by FAH monitoring.
- Project execution contract: `.fah/execution-contract.json`
- Before meaningful execution, clients must evaluate the declared execution contract through FAH when available, or read the same GitHub contract as fallback.
- A decision other than `ALLOW` or `EXEMPT` must not proceed.
- Existing project-local fail-closed guards remain mandatory as the final enforcement layer.
- GitHub Actions are not implied or enabled by FAH onboarding or contract enforcement.

## Global PPT request entry rule

Whenever FriendY asks to create a new PPT/presentation/slides deck, even without mentioning Slide Master or FAH explicitly, the execution entrypoint is always project `SLIDE_MASTER` in canonical repository `FriendY0421/slide-master`.

A host-required `artifact_handoff` / presentation-preparation call may occur first, but it is **preparation only**. It never authorizes PPT generation and never replaces the FAH `TEMPLATE_SELECTION` gate.

Required order:

`PPT request → host preparation if required → canonical SLIDE_MASTER lock → FAH TEMPLATE_SELECTION → latest GitHub catalog → conversation-native interactive picker → user final selection → picker/selection evidence → research/generation → local fail-closed validation → PPTX`

## Canonical ChatGPT/GPTS template-selection UI

The primary selection UI is the **conversation-native interactive picker (App Block / GenUI) when the current host supports it**.

Rules:

- Every new PPT request refreshes from current GitHub `main` Deck/Layout indexes.
- Discovery is index-driven through `template_catalog.py`; never hard-code current ids/counts.
- `template_gallery_chat_manifest_v2.py` is the live data contract for host-native interactive rendering.
- When suitable templates exist, show 5–10 real registered recommendation cards (default target 6, up to 10).
- Card interaction must lead to up to 6 real detail examples from the exact workspace.
- Free Design remains separate.
- When useful, presentation-production presets are shown as a second interactive selection stage.
- Recommendation or card click never auto-confirms.
- The final selected id must return/be explicitly confirmed in chat unless the host supplies a verifiable equivalent selection event.
- Recommended-template records require picker-surface evidence before `record_template_choice_v2.py --confirmed` may succeed.
- A directly user-specified valid registered template uses `--direct-template` and does not require picker rendering.
- Missing valid evidence is `WAIT_USER_ACTION`; no research/generation may start.
- If App Block / GenUI cannot be used, record why and fall back in order: native visual cards → inline self-contained HTML → GitHub visual catalog → external/local recovery → text last resort.
- Markdown `<img>` lists and static PNGs must not be represented as interactive UI.
- Broken Korean glyphs are never acceptable.

`PPT_REQUEST_GUARD.md` is the first-read fail-closed authority for presentation generation.
