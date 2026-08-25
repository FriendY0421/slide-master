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

Do not begin from upstream `byungjunjang/slide-master`, a generic presentation repository, a host-native slide generator, or an artifact-generation shortcut. Those must not precede or bypass the FriendY FAH Execution Contract.

Required order:

`PPT request → canonical SLIDE_MASTER repository lock → FAH Execution Contract evaluation → required TEMPLATE_SELECTION handshake → user explicit template choice → content research/generation → local fail-closed validation → PPTX`

For a new deck, template selection is a blocking user-interaction gate. Missing selection evidence means execution must stop at `WAIT_USER_ACTION`/blocked state. On ChatGPT and other conversational hosts that can render visuals, show the live registered templates and their actual representative previews **inside the current conversation first**, wait for the user's explicit choice, and record that choice as normal gate evidence. External/local HTML/GUI is fallback only when the current host cannot render the actual previews inline; plain text is last resort only when neither visual surface is technically possible. Only the documented existing-PPT beautification route may use its contract exemption.

Read `PPT_REQUEST_GUARD.md` before any presentation research or generation work.