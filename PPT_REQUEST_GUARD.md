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

## Canonical template-selection surface — CHAT FIRST

For conversational hosts such as ChatGPT, the **current conversation is the canonical template-selection surface**. The user must see the actual live registered templates and representative previews directly in the conversation and make the explicit choice there.

The phrase `HTML/GUI Template Gallery` in the unchanged FAH Execution Contract is host-agnostic. On ChatGPT it means **host-native in-conversation GUI/preview rendering first**. It does **not** mean opening a separate PC/browser window when the current host can render the gallery in chat.

External/local HTML or browser GUI is a fallback only when the current host truly cannot render real template previews inside the conversation. A plain text-only template-name list is a last-resort fallback and must never replace available visual previews merely for convenience.

## Visual-render enforcement — FAIL CLOSED

For ChatGPT and other conversational hosts that can render images/files in the conversation, the template-selection step is **not considered displayed** unless at least one real visual preview is rendered for every selectable registered template presented to the user.

The following are explicit failures and must not be treated as a completed template-selection prompt:

- showing only template names/numbers;
- showing only prose descriptions;
- saying that previews are available without actually rendering them;
- linking to an external gallery when in-conversation rendering is available;
- inventing or recreating approximate thumbnails instead of using registered template SVGs;
- asking the user to provide a template number before real previews were rendered.

If visual rendering fails unexpectedly, do not fall through silently to a text list. Report the rendering failure, retry the inline render once using the exact registered SVG source, and only then use the documented fallback path if the host is genuinely unable to render visuals.

## Non-negotiable entry sequence

1. Read `workflows/routing.md` and this guard before any new-deck research, project initialization, SVG authoring, or PPTX export.
2. If the user already explicitly chose a valid registered deck id/workspace, record that choice through `record_template_choice.py`.
3. Otherwise, on a conversational host, obtain the live catalog and exact registered preview paths through `template_gallery_chat_manifest.py` (or an equivalent connected-GitHub read of the same `decks_index.json` + registered SVGs), then render the real representative template previews **inside the current conversation**.
4. Show the complete live registered catalog plus Free Design, grouped by use category. The first view may emphasize context-relevant recommendations, but the user must retain access to every selection-ready registered deck.
5. For each registered template offered for selection, render at least one actual registered SVG preview in the conversation. When the host supports multiple images/cards, show representative cover plus useful layout previews; when space is constrained, show the representative preview first and expose additional real layouts on request/selection detail.
6. Recommend only templates that genuinely fit the user's purpose and context, **up to 10**. Do not fill a quota. Use relative relevance so weak secondary matches are not recommended merely because they share a broad category.
7. Do not silently choose a recommended template. Wait for the user's explicit selection in the conversation. Free Design is valid only when the user explicitly chooses it.
8. After the user chooses in chat, record the choice through `record_template_choice.py` and create the normal `template_selection.json` evidence. The selection surface may differ, but the evidence contract does not.
9. If and only if the current host cannot render actual registered previews in conversation after one retry, fall back to `template_gallery_context.py` HTML/GUI mode with the user's actual purpose/context and keep the task alive until it returns `TEMPLATE_SELECTED`.
10. New-deck project initialization must use `new_deck_init.py` with template-selection evidence. Missing selection evidence is a hard failure.
11. `svg_to_pptx.py` validates the project gate again before export. A missing or invalid gate blocks PPTX generation even if an earlier conversational step was skipped.

## Context-aware catalog

Template metadata in `templates/decks/decks_index.json` owns discovery fields:
- `primary_category`: main display group
- `categories`: additional use groups
- `keywords`: purpose/context matching terms

Stable category ids include `report`, `education`, `notice`, `presentation`, `proposal`, `data`, `brand_story`, `product`, and `general`. The gallery may add more categories later without changing this gate, but every new registered deck should declare a sensible primary category and matching keywords.

## Fail-closed rule

No `template_selection.json` (selected or approved route exemption) means the project did not pass the entry gate.

For ChatGPT and other conversational hosts, do not substitute an external browser window for an available in-conversation gallery. Do not substitute a plain text list for available visual previews. Do not silently select a recommended template on the user's behalf.