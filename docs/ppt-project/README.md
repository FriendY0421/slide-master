# Stable PPT Project

This directory documents the host-independent PPT production path.

## Core files

- [PPT Request Guard](../../PPT_REQUEST_GUARD.md) — fail-closed entry authority.
- [Stable Visual Template Gallery](../template-gallery/README.md) — actual registered template previews and selection IDs.
- [State Machine](state_machine.json) — allowed states, transitions, and hard stops.
- [Project Instructions](PROJECT_INSTRUCTIONS.md) — operating procedure for a dedicated PPT workflow.

## Default path

`PPT request → live catalog → stable visual gallery → explicit user selection → selection evidence → deck generation → QA → delivery`

The flow must not depend on inline HTML rendering. Rich pickers may be used only as optional convenience layers when their visible output is positively verified.
