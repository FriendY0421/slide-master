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

`PPT request -> host preparation if required -> canonical SLIDE_MASTER lock -> template picker -> explicit template id -> production preset picker -> explicit preset id -> lock template+preset -> latest evidence/research -> slide-by-slide storyline proposal -> explicit storyline approval -> generation -> QA -> PPTX`

## Canonical ChatGPT/GPTS template-selection UI

The primary selection UI is the **conversation-native interactive picker (App Block / GenUI) when the current host supports it**.

Rules:

- Every new PPT request refreshes from current GitHub `main` Deck/Layout indexes.
- Discovery is index-driven through `template_catalog.py`; never hard-code current ids/counts.
- `template_gallery_chat_manifest_v2.py` is the live data contract for host-native interactive rendering.
- When suitable templates exist, show 5–10 real registered recommendation cards (default target 6, up to 10).
- Card interaction must lead to up to 6 real detail examples from the exact workspace.
- Free Design remains separate.
- Production presets are a mandatory second selection stage for every new deck unless the user already supplied a valid preset id.
- Recommendation or card click never auto-confirms; template and preset must both be explicit before the selection is locked.
- The final selected id must return/be explicitly confirmed in chat unless the host supplies a verifiable equivalent selection event.
- Recommended-template records require picker-surface evidence plus `--preset <preset_id>` before `record_template_choice_v2.py --confirmed` may succeed.
- A directly user-specified valid registered template uses `--direct-template` and skips only template rendering; a valid production preset is still mandatory unless already supplied.
- Missing template or preset evidence is `WAIT_USER_ACTION`; research starts only after both are locked.
- After research, present a slide-by-slide storyline/content outline and wait for explicit approval before slide authoring or PPTX generation.
- If App Block / GenUI cannot be used, record why and fall back in order: Desktop Commander template HTML -> preset HTML -> native visual cards -> GitHub visual catalog -> text last resort.
- Markdown `<img>` lists and static PNGs must not be represented as interactive UI.
- Broken Korean glyphs are never acceptable.

`PPT_REQUEST_GUARD.md` is the first-read fail-closed authority for presentation generation.

## User-editable slide-by-slide preview gate ? 2026-08-30
Before any new-deck project initialization or slide authoring, present the **full proposed slide sequence** in chat (or an equivalent visible review surface). Every slide preview must show: slide number, title, core message, 2?5 main content points, and proposed visual/layout treatment. The user may delete, add, merge, split, reorder, retitle, rewrite, change visuals, or request a new total slide count (including 20/30+). Apply those edits to the preview and show the revised affected slides or full sequence as appropriate.

Generation permission requires the user to explicitly approve the **current revision**. Record that exact approved snapshot through `storyline_gate.py`; `new_deck_init.py` requires both `--template-selection-result` and `--storyline-approval-result`. If the storyline changes after approval, the old approval is stale and generation must stop until the revised preview is approved again. `validate_spec.py` checks the generated ?IX slide count/titles/core messages against the approved snapshot, and gate-v3 SVG export is blocked without storyline approval evidence.
