---
description: Mandatory template-selection gate for new Slide Master deck generation
---

# Template Selection Gate

This repository requires an explicit template choice before any **new deck generation** begins.
The user must see what is actually registered, inspect representative previews, and choose the
visual system before research, project initialization, SVG authoring, or PPTX generation continues.
[`../../../..//PPT_REQUEST_GUARD.md`](../../../../PPT_REQUEST_GUARD.md) is the short fail-closed
authority for this rule; this workflow owns the detailed picker behavior.

## Scope

Apply this gate to:
- topic-only decks that will enter `topic-research` and then the main SVG pipeline;
- decks generated from PDF, DOCX, URL, Markdown, spreadsheet, conversation text, or other source material;
- PPTX used as re-architectable source material when slide count/order may change.

Do **not** apply the visual picker to:
- `ppt-template-fill` (the supplied PPTX is already the template);
- strict 1:1 `beautify-pptx` (the source deck is the visual reference);
- `native-enhance-pptx` (content/layout remain stable);
- resume/continue operations for a project that already has a confirmed template decision.

Those exempt routes must still write a documented `template_selection.json` exemption when they
enter any shared generated-deck export path. The purpose is auditability and fail-closed enforcement,
not to force an irrelevant template choice onto a direct-PPTX workflow.

## Mandatory host-aware gallery behavior

1. If the user already named a valid registered deck id/workspace path, treat that as the explicit
   choice and continue without opening or rendering the gallery again. Record it with
   `record_template_choice.py` so the project can carry machine-readable selection evidence.
2. Otherwise determine the host surface **before research or project init**:
   - On ChatGPT or another conversational host capable of rendering images/cards/files in the current
     conversation, the **in-conversation gallery is mandatory and preferred**.
   - Only when the current host truly cannot render the real registered previews in conversation may
     the external/local HTML picker be used as fallback.
3. For the in-conversation path, obtain the current catalog, context ranking, exact workspace paths,
   and real representative SVG paths using:

```bash
python .claude/skills/ppt-master/scripts/template_gallery_chat_manifest.py \
  --source auto \
  --purpose "<the user's actual deck purpose/context>"
```

   A connected host that cannot run local Python may perform an equivalent read from the canonical
   `FriendY0421/slide-master` repository: read `decks_index.json`, the registered workspace, and the
   exact representative SVGs. The data source and ranking semantics must remain equivalent.
4. Render the **actual registered SVG previews directly in the current conversation**. Do not redraw,
   approximate, or substitute generic design samples. Show the complete live registered catalog plus
   `Free Design`, grouped by use category. The first view may emphasize the relevant recommendations,
   but the user must retain access to all selection-ready registered decks.
5. Mark only templates with genuine contextual relevance as `Recommended`, up to **10**. This is a
   ceiling, not a quota: one strong match may yield one recommendation; four relevant matches may
   yield four. Recommendations never auto-select. The user still chooses the final visual system.
6. Each registered deck uses its real representative SVG. Where the host can show multiple images or
   detail cards, expose up to **6 representative layout types** selected from the registered SVG roster
   (cover/title, agenda/section, content, data/KPI, comparison/visual, closing, with remaining slots
   filled by other distinct layouts). The user confirms only after being able to inspect the real design.
7. Hard stop until the user explicitly chooses in the current conversation. Do not continue merely
   because previews were shown, and never silently default to Free Design.
8. After a chat selection, record the explicit choice through `record_template_choice.py`:

```bash
python .claude/skills/ppt-master/scripts/record_template_choice.py <deck_id|free> \
  --purpose "<the user's actual deck purpose/context>" \
  --output <result.json>
```

   Then resume the same PPT request using the resulting selection evidence.
9. If the in-conversation visual surface is unavailable, use the existing HTML fallback:

```bash
python .claude/skills/ppt-master/scripts/template_gallery_context.py \
  --source auto \
  --lang <ko|en> \
  --purpose "<the user's actual deck purpose/context>"
```

   On Windows, use `python` when `python3` is unavailable. `--recommend` is optional and may add
   already-known registered ids, but automatic context ranking is the default and total recommended
   items remain capped at 10. The HTML picker refreshes `origin/main` through the existing gallery core
   without checking it out or modifying the working tree. When GitHub is unavailable, `--source auto`
   falls back to the local checkout and labels the fallback visibly.
10. For the HTML fallback, hard stop until the picker returns `TEMPLATE_SELECTED=...`. Do not continue
    because the browser was merely opened. **The caller must keep the current agent task/turn alive
    while the gallery is open.** If the command host returns control while the gallery child process is
    still running, immediately wait on that process or poll the result file; do not end the assistant
    response with a message telling the user to select and come back later.
11. As soon as selection evidence exists, initialize a new main-SVG deck with:

```bash
python .claude/skills/ppt-master/scripts/new_deck_init.py <project_name> \
  --format <format> \
  --template-selection-result <result.json>
```

    Do not use a bare `project_manager.py init` for a new deck. The resulting project must contain
    `template_selection.json` before downstream work begins.
12. After a registered deck id is selected, resolve its returned `workspace` to the exact registered
    workspace path and hand that user-confirmed path to main Step 3. This must not trigger a second
    template question.
13. `Free Design` is allowed only when the user explicitly chooses it. The result is recorded exactly
    like a registered selection, with `template: free` and no workspace.

## Catalog taxonomy and context matching

The catalog is **not hard-coded**. `templates/decks/decks_index.json` is the discovery source of truth.
Every selection-ready deck should declare:

- `primary_category`: its main gallery section;
- `categories`: additional valid use categories;
- `keywords`: user-language terms that identify suitable requests;
- normal display fields such as `display_name`, `summary`, `primary_color`, and `page_count`.

Current stable category ids are `report`, `education`, `notice`, `presentation`, `proposal`, `data`,
`brand_story`, `product`, and `general`. Newly registered templates automatically participate in
context ranking and categorized display when these fields are present. Do not edit picker code for
each new template.

## Preview contract for newly registered templates

A library deck is not selection-ready until:
- it is present in `decks_index.json`;
- `<workspace>/templates/design_spec.md` exists and declares `kind: deck`;
- `<workspace>/templates/` contains at least one SVG;
- the lexicographically first SVG is a representative, self-contained preview shell (normally
  `01_title.svg` or `01_cover.svg`) with normal `{{TOKEN}}` placeholders where sample text is needed.

Both the chat manifest and HTML gallery use the same registered SVG roster. The first representative
SVG is the summary-card thumbnail and up to six representative SVGs are selected for detail view.
Selection is semantic by filename and falls back to other available SVGs, so newly registered
company/user templates automatically gain the same multi-layout preview without host-specific picker
code changes. No separate PNG/JPEG thumbnail is required.

## Fast validation / diagnostics

Before release or while diagnosing catalog problems, run context examples without opening a browser:

```bash
python .claude/skills/ppt-master/scripts/template_gallery_chat_manifest.py \
  --source local --purpose "경영진 개선 보고"

python .claude/skills/ppt-master/scripts/template_gallery_chat_manifest.py \
  --source local --purpose "신입사원 AI 교육"

python .claude/skills/ppt-master/scripts/template_gallery_chat_manifest.py \
  --source local --purpose "전 직원 안전 공지"
```

The legacy context picker can still be checked headlessly with `template_gallery_context.py --list`.
Also validate the fail-closed evidence independently:

```bash
python .claude/skills/ppt-master/scripts/template_gate.py validate <project_path>
```

## Fallback order

Use this exact order:

1. **Conversation-inline visual gallery** using the live registered templates and real SVG previews.
2. **External/local HTML/GUI gallery** only when the current host cannot render the real previews in chat.
3. **Plain text catalog** only when neither visual surface is technically possible.

The fallback changes only the presentation surface. It never changes the explicit-selection requirement,
`template_selection.json` evidence, Free Design opt-in rule, or downstream fail-closed gate.