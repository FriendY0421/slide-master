# CLAUDE.md

This file is the project entry point for Claude Code. The ppt-master skill lives at `.claude/skills/ppt-master/` and is auto-discovered by Claude Code.

> **Cross-harness (dual-host)**: [`AGENTS.md`](AGENTS.md) is the Codex-side execution-rules layer — it references this file as SSOT and only adds enforcement, so content edits here do not need mirroring there. `.codex/skills/` holds **generated** Codex discovery stubs: after editing any `.claude/skills/<name>/SKILL.md` frontmatter, run `python3 .claude/skills/ppt-master/scripts/sync_codex_stubs.py` (never hand-edit stubs; `preflight.py` fails while they are stale). Skill content itself lives only in `.claude/skills/`.

## PPT Request Guard — mandatory first read

For **every presentation request**, read [`PPT_REQUEST_GUARD.md`](PPT_REQUEST_GUARD.md) before routing.
For a new deck, the guard is fail-closed. The canonical sequence is:

`PPT request -> live template picker -> explicit template id -> production preset picker -> explicit preset id -> lock template+preset -> latest evidence/research -> slide-by-slide storyline proposal -> explicit storyline approval -> generation -> QA -> PPTX`

Do not begin research until both template and production preset are explicit and recorded. Do not initialize the project, author slides, or export PPTX until the post-research storyline/content outline has been explicitly approved. On a conversational host, a verified in-conversation picker is primary; if the host returns developer-MCP `FORBIDDEN`, use the documented Desktop Commander template HTML followed by preset HTML. The UI surface may change, but the stage order must not. New records are `template_selection.json` gate v3 and include `production_preset`; legacy gate v1/v2 remains readable for resume compatibility.

Recommendations never auto-select, and neither template nor preset may be silently changed after lock. `svg_to_pptx.py` and downstream owner gates remain fail-closed.

**Route before full-load (mandatory)**: after the PPT Request Guard, read
[`.claude/skills/ppt-master/workflows/routing.md`](.claude/skills/ppt-master/workflows/routing.md).
Select the route there, then read only the selected execution owner(s) in full.
Do not preload the main SVG skill for a direct-PPTX route. For a repository edit,
read the owner of the contract being changed; the main skill is authoritative only
for the main SVG family and the shared SVG steps that explicitly invoke it.

## Project Overview

PPT Master is a presentation workflow package with SVG-authoring and direct-PPTX
route families. The main SVG family uses Strategist → Image_Generator → Executor
to convert source documents into editable DrawingML. Direct-PPTX routes preserve
an existing PowerPoint package and use their own execution gates.

**Main SVG Pipeline**: `Source Document → Create Project → [Template] → Strategist confirmation stage → [Image_Generator] → Executor Live Preview → Quality Check → Post-processing → Export PPTX`

**Route selection authority**:
[`.claude/skills/ppt-master/workflows/routing.md`](.claude/skills/ppt-master/workflows/routing.md)
owns the complete matrix and wins over every route summary below. The repository-level
[`PPT_REQUEST_GUARD.md`](PPT_REQUEST_GUARD.md) owns the pre-route new-deck entry requirement.

| Selected family | Full execution owner(s) |
|---|---|
| New SVG-authored deck or PPTX re-architecture | [Main `ppt-master/SKILL.md`](.claude/skills/ppt-master/SKILL.md) |
| Existing PPTX, strict 1:1 wording/page preservation with visual redesign | [`beautify-pptx.md`](.claude/skills/ppt-master/workflows/beautify-pptx.md), then the main skill only at its explicit shared-SVG handoff |
| Raw PPTX template plus new material/topic | [`ppt-template-fill/SKILL.md`](.claude/skills/ppt-template-fill/SKILL.md) only |
| Finished PPTX, stable visible content/layout, add notes/audio/timing/transitions | [`native-enhance-pptx/SKILL.md`](.claude/skills/native-enhance-pptx/SKILL.md), then its required execution workflow |
| Reusable template creation or another standalone workflow | The selected workflow; load another owner only at an explicit handoff |

An ambiguous PPTX optimization request stays in the router until its one
discriminator question resolves whether the deck is 1:1 beautify or
re-architectable source. Do not load either full owner before that answer.

## Execution Ownership

- The repository-level PPT Request Guard owns only the pre-route new-deck selection evidence and the
  final generated-deck export check. The selected skill or workflow owns its normal confirmations,
  preflight, validation, recovery, export behavior, and completion gates.
- Direct-PPTX routes do not inherit an irrelevant template picker; when they enter a shared generated-deck
  export path, they record a documented gate exemption instead.
- Shared scripts do not transfer other gate ownership between SVG and direct-PPTX families.
- Topic research, template creation, and post-route workflows load the next owner only when their own
  procedure declares a handoff.

## Font Policy (install-local, standing preference)

- Every SVG-authored deck uses **Pretendard** as the fixed font family — do not propose or pick other families unless the user explicitly asks in the current conversation. Hierarchy comes from weight/size, not family switching. Direct-PPTX routes preserve source fonts unless their selected owner says otherwise. Full contract: [`strategist.md §g` install-local font lock](.claude/skills/ppt-master/references/strategist.md).
- Stack: `Pretendard, "Malgun Gothic", sans-serif`; intermediate weights use installed family names (`"Pretendard Medium"`, `"Pretendard SemiBold"`, etc.).
- Font files are bundled at [`.claude/skills/ppt-master/assets/fonts/Pretendard/`](.claude/skills/ppt-master/assets/fonts/Pretendard/) (SIL OFL) and installed user-level on this machine. PPTX does not embed fonts — decks shared to other machines need Pretendard installed there.

## Required Conventions

- **Repo-wide style rules** — when editing prompt files under [`.claude/skills/ppt-master/references/`](.claude/skills/ppt-master/references/), Python under [`.claude/skills/ppt-master/scripts/`](.claude/skills/ppt-master/scripts/), or any other code/prose in the repo, follow the matching style rule in [`docs/rules/`](docs/rules/).
- **Markdown language consistency** — Markdown files under `.claude/skills/ppt-master/workflows/`, `.claude/skills/ppt-master/references/`, and `docs/` are currently single-language per directory. New files mirror the language of their siblings; do not mix English scaffolding with Chinese paragraphs (or vice versa) inside one file. Chat replies are unaffected.

## Compatibility Boundary

- This repository is a workflow/skill package, not an app or service scaffold.
- Do NOT assume generic-project conventions like `.worktrees/`, `tests/`, or mandatory branch setup unless the user explicitly requests them.
- On conflict with a generic coding skill, prioritize the selected repo-local
  execution owner. The main [`ppt-master/SKILL.md`](.claude/skills/ppt-master/SKILL.md)
  has that role only when routing selected the main SVG family or an explicit
  shared-SVG handoff. The repository entry guard remains active for new-deck evidence.

## Execution Pointers

Commands and defaults belong to the selected owner; use these pointers instead
of treating a root-level command list as a gate checklist.

| Work | Runtime authority |
|---|---|
| New-deck entry / template-selection evidence | [`PPT_REQUEST_GUARD.md`](PPT_REQUEST_GUARD.md) + [`template-selection.md`](.claude/skills/ppt-master/workflows/template-selection.md) |
| Route selection | [`routing.md`](.claude/skills/ppt-master/workflows/routing.md) |
| Main SVG generation and re-architecture | [`ppt-master/SKILL.md`](.claude/skills/ppt-master/SKILL.md) |
| Strict 1:1 SVG beautify | [`beautify-pptx.md`](.claude/skills/ppt-master/workflows/beautify-pptx.md) and only the shared main steps it invokes |
| Raw template fill | [`ppt-template-fill/SKILL.md`](.claude/skills/ppt-template-fill/SKILL.md) |
| Finished-PPTX native enhancement | [`native-enhance-pptx/SKILL.md`](.claude/skills/native-enhance-pptx/SKILL.md) |
| Standalone workflow inventory | [`workflows/index.md`](.claude/skills/ppt-master/workflows/index.md) |

## Core Directories

- `PPT_REQUEST_GUARD.md` — fail-closed new-deck entry authority independent of model memory.
- `.claude/skills/ppt-master/SKILL.md` — main SVG workflow authority.
- `.claude/skills/ppt-template-fill/SKILL.md` — raw-template direct-PPTX authority.
- `.claude/skills/native-enhance-pptx/SKILL.md` — finished-PPTX enhancement entry owner.
- `.claude/skills/ppt-master/references/` — role definitions and technical specifications.
- `.claude/skills/ppt-master/scripts/` — runnable tool scripts.
- `.claude/skills/ppt-master/scripts/docs/` — topic-focused script docs.
- `.claude/skills/ppt-master/templates/` — layout templates, chart templates, icon library, brand presets.
- `.claude/skills/ppt-master/workflows/` — standalone workflow files.
- `docs/` — user-facing documentation (FAQ, installation, technical design, templates guide, audio narration).
- `docs/rules/` — repo-wide style rules.
- `projects/` — user project workspace.