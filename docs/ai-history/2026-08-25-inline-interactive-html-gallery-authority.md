# Inline Interactive HTML Gallery Authority

Updated: 2026-08-25 17:13 KST

FriendY supplied the previously working `preview(1).html` and confirmed that this exact interaction model is the desired normal PPT template-selection experience inside the ChatGPT conversation.

## Approved UI contract

Primary ChatGPT surface:

`self-contained HTML artifact rendered interactively inside the conversation`

Required interaction:

`gallery cards → card click → in-page detail dialog → up to six real registered examples → 이 템플릿 선택 → selected name/id displayed`

The gallery also shows purpose-aware recommendations and Free Design.

## Live GitHub catalog

The HTML must not embed a permanent historical template list. Every new PPT request rebuilds the artifact from the latest `FriendY0421/slide-master` GitHub `main` indexes:

- `templates/decks/decks_index.json`
- `templates/layouts/layouts_index.json`
- unified through `template_catalog.py`

Future registered templates automatically enter the next gallery. Updating/removing registered templates likewise changes the next gallery without picker-code edits.

Production generation uses `--source github` so a refresh failure fails closed instead of silently presenting stale local choices.

## Large catalog UX

The primary inline HTML supports:

- recommended templates at the top;
- complete current registered library;
- text search;
- Deck/Layout filters;
- automatic pagination, default 12 cards per page;
- modal detail preview with up to six real registered layouts;
- Free Design as a separate explicit option.

The visual styling may improve over time, but this interaction contract remains fixed.

## Self-contained artifact

`template_gallery_inline_html.py` embeds registered SVG previews and package-local assets as data URIs. The primary ChatGPT experience therefore does not depend on a localhost server or separate browser window.

## Host preparation boundary

A host-required `artifact_handoff` / presentation-preparation call is preparation only. It does not satisfy `TEMPLATE_SELECTION` and never authorizes PPT generation.

No PPT research, project initialization, slide authoring, or PPTX output may begin until the user selects through the inline gallery, returns the selected id in chat, and valid template selection evidence is recorded.

## Fallback order

1. Self-contained interactive HTML inside ChatGPT conversation — primary.
2. Conversation-native visual two-stage gallery — secondary only if inline HTML cannot render interactively.
3. External/local browser HTML server — auxiliary last fallback only.

GitHub Actions were not used and the accepted FAH execution contract/runtime remain unchanged.
