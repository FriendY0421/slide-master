# Chat-first Template Gallery Root Correction

Updated: 2026-08-25 10:31 KST

## Problem

A new PPT request correctly reached the FAH `TEMPLATE_SELECTION` gate but stopped at `WAIT_USER_ACTION` without showing the template chooser inside ChatGPT. The detailed Slide Master workflow treated the external/local HTML gallery as the default surface and chat as fallback, which contradicted FriendY's previously working in-conversation selection experience.

## Root cause

The FAH execution contract correctly required explicit `TEMPLATE_SELECTION`; the defect was not the gate. The defect was the presentation surface priority below the gate:

`HTML/GUI first -> chat fallback`

This allowed a conversational host to interpret `Launch the HTML/GUI Template Gallery` as a separate PC/browser window even when the conversation itself could present the selection UI.

## Durable correction

The canonical surface order is now:

1. conversation-inline visual gallery using real registered Slide Master previews;
2. external/local HTML/GUI only when inline visual rendering is unavailable;
3. plain text catalog only when neither visual surface is technically possible.

The user must still explicitly choose. Recommendations never auto-select and Free Design remains explicit opt-in.

## Implementation

- `PPT_REQUEST_GUARD.md`: ChatGPT/current-conversation gallery is now canonical.
- `.claude/skills/ppt-master/workflows/template-selection.md`: host-aware flow changed to conversation-inline first.
- `AGENTS.md`: Codex/agent entry procedure aligned with the same rule.
- `.claude/skills/ppt-master/scripts/template_gallery_chat_manifest.py`: added a no-browser manifest helper that returns the live catalog, context ranking, exact registered workspace, representative SVG path, and up to six real preview SVG paths.
- Existing `record_template_choice.py`, `new_deck_init.py`, `template_gate.py`, and guarded `svg_to_pptx.py` remain unchanged.

## FAH contract compatibility

`.fah/execution-contract.json` v1.0 is intentionally unchanged. Its accepted blob SHA remains `d8c24c26460cded0fe947df75b2e278488fd7641`, so FAH runtime @45 remains `CONTRACT_CURRENT`.

The contract phrase `HTML/GUI Template Gallery` is treated as host-agnostic UI intent. `PPT_REQUEST_GUARD.md` now owns the host-specific interpretation: on ChatGPT, an available in-conversation visual gallery is the GUI surface; external HTML is fallback.

## Validation

- New helper Python syntax: PASS (`py_compile`).
- Existing template-selection evidence contract: unchanged.
- Existing FAH contract SHA/version: unchanged.
- GitHub Actions: not used.
- No PPT generation/export path was modified.

## Expected user-visible flow

`PPT request -> FriendY0421/slide-master -> FAH gate -> live template previews inside the same ChatGPT conversation -> user selects -> template_selection.json evidence -> research/generation -> QA -> PPTX`
