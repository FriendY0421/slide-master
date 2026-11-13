# Stable PPT Project

This directory documents the host-independent PPT production path.

## Current standalone status

- [Private 0.4.16 photo overlay update](PHOTO_COMPARISON_20261113.md) covers
  publication, the installed guidebook checks and 0.4.17 recovery to 0.4.14.
- [Private 0.4.14 photo reconstruction update](PHOTO_PLUGIN_UPDATE_0.4.14.md)
  covers official publication, local loading, synthetic validation and
  guarded 0.4.15 recovery to 0.4.12 content.

- [Private 0.4.12 release and recovery](PUBLIC_PRESENTATION_RELEASE_0.4.12.md)
  covers the saved release, verified local package and guarded 0.4.13 restore.
- [Dense sample acceptance](DENSE_SAMPLE_ACCEPTANCE_0.4.12.md) covers
  PowerPoint rendering, editability and private delivery. The recipient opened
  both slides on their phone. New cloud production from mobile is tracked
  separately and paused in this workstream at the user's request.
- [ChatGPT and DOTS handoff](CHATGPT_DOTS_HANDOFF.md) and
  [missing-file recovery](RESET_RECOVERY_POLICY.md) cover continuation.

## Core files

- [PPT Request Guard](../../PPT_REQUEST_GUARD.md) — fail-closed entry authority.
- [Stable Visual Template Gallery](../template-gallery/README.md) — actual registered template previews and selection IDs.
- [State Machine](state_machine.json) — allowed states, transitions, and hard stops.
- [Project Instructions](PROJECT_INSTRUCTIONS.md) — operating procedure for a dedicated PPT workflow.

## Default path

`PPT request -> live template picker -> explicit template id -> production preset picker -> explicit preset id -> lock -> research/verification -> slide-by-slide storyline -> explicit approval -> generation -> QA -> delivery`

The preferred UI is a verified conversation-native picker when the host supports it. If the host rejects developer MCPs, use the Desktop Commander template HTML followed by preset HTML. The surface may change; the stage order and fail-closed checkpoints do not.
