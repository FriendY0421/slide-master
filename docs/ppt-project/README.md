# Stable PPT Project

This directory documents the host-independent PPT production path.

For short builtin/custom requests and current cloud connectivity, see
[the Korean cloud guide](SIMPLE_CLOUD_WORKFLOW.md). It is a PR review candidate,
not a claim that the connected plugin or main has been updated.

## Core files

- [PPT Request Guard](../../PPT_REQUEST_GUARD.md) — fail-closed entry authority.
- [Stable Visual Template Gallery](../template-gallery/README.md) — actual registered template previews and selection IDs.
- [State Machine](state_machine.json) — allowed states, transitions, and hard stops.
- [Project Instructions](PROJECT_INSTRUCTIONS.md) — operating procedure for a dedicated PPT workflow.

## Default path

`PPT request -> live template picker -> explicit template id -> production preset picker -> explicit preset id -> lock -> research/verification -> slide-by-slide storyline -> explicit approval -> generation -> QA -> delivery`

The preferred UI is a verified conversation-native picker when the host supports it. If the host rejects developer MCPs, use the Desktop Commander template HTML followed by preset HTML. The surface may change; the stage order and fail-closed checkpoints do not.

For the pinned synthetic portability audit and supplied-runtime startup commands, see
[the reproducible cloud start guide](CLOUD_REPRODUCIBLE_START.md).
