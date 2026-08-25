# Latest project handoff

Updated checkpoint: 2026-08-25 10:56 KST

## NEWEST CHECKPOINT — CHAT TEMPLATE VISUAL RENDER FAIL-CLOSED

The previous chat-first correction was directionally correct but still incomplete: a host could satisfy the policy in prose by listing template names/numbers without actually rendering the registered template visuals. That reproduced the user's original inconsistency.

The new durable rule is stricter:

- on ChatGPT and any conversational host capable of visual rendering, the template-selection prompt is **not considered displayed** unless at least one actual registered SVG preview is rendered for every selectable registered template presented to the user;
- template names/numbers alone are an explicit failure;
- prose descriptions alone are an explicit failure;
- asking the user to choose a number before real previews appear is an explicit failure;
- external browser/gallery links are not allowed while in-conversation rendering is available;
- approximated/recreated thumbnails are forbidden; use exact registered Slide Master SVGs;
- on unexpected render failure, retry inline rendering once from the exact registered SVG source before using the documented external HTML fallback;
- selection evidence, `template_selection.json`, `new_deck_init.py`, `template_gate.py`, and guarded `svg_to_pptx.py` remain unchanged and fail closed.

`PPT_REQUEST_GUARD.md` now owns this visual-render fail-closed rule. This closes the gap between 'chat-first policy' and actual visible user experience.

The accepted `.fah/execution-contract.json` v1.0 remains intentionally unchanged; blob SHA is still `d8c24c26460cded0fe947df75b2e278488fd7641`, preserving FAH runtime @45 `CONTRACT_CURRENT` identity. No GitHub Actions were used.

Expected user-visible flow:

`PPT request → FAH gate → actual registered template images/cards visibly rendered in this conversation → explicit user choice → selection evidence → PPT generation`

---

## PREVIOUS CHECKPOINT — CHAT-INLINE TEMPLATE GALLERY HARDENED

A new PPT request correctly reached the FAH `TEMPLATE_SELECTION` gate but did not show the chooser inside ChatGPT. Investigation confirmed that FAH runtime @45 and the execution contract were healthy. The root cause was the lower-level Slide Master presentation-surface policy: `template-selection.md`, `AGENTS.md`, and `CLAUDE.md` still treated the external/local HTML gallery as the normal path and chat as fallback.

The durable correction remains active:

- ChatGPT and other conversational hosts with visual-rendering capability use the **current conversation as the canonical template-selection surface**;
- the host retrieves the live registered Slide Master catalog and the exact registered SVG previews, then renders those real previews directly in the conversation;
- `.claude/skills/ppt-master/scripts/template_gallery_chat_manifest.py` exposes context ranking, exact workspace paths, representative SVG paths, and up to six real layout previews without opening a browser;
- recommendations remain contextual and capped at 10 without filling a quota;
- recommendations never auto-select and `Free Design` remains explicit opt-in;
- after an in-chat user choice, `record_template_choice.py` records the normal machine-readable selection result and `new_deck_init.py` creates `template_selection.json` evidence;
- external/local `template_gallery_context.py` HTML/GUI is fallback only when the current host cannot render the real previews inline;
- a plain text catalog is last resort only when neither visual surface is technically possible.

Durable history: `docs/ai-history/2026-08-25-chat-inline-template-gallery.md`

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

## GitHub Actions policy

GitHub Actions are default-off to conserve usage. They may be used only when the current user explicitly requests emergency deployment or explicitly requests GitHub Actions.