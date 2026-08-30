# Picker feature-runtime cross-branch pointer

Date: 2026-08-30 KST
Main authority: `FriendY0421/slide-master` `main`
Picker runtime branch: `feat/apps-sdk-template-picker-20260827`
Verified Picker runtime HEAD: `2efa7c6338137ed0c788e6abe803e3ca1a6bb167`

## Why this pointer exists

`main` contains the latest standard staged PPT workflow, expanded template catalog, and Developer-MCP fallback work. The active Secure MCP Picker runtime hardening is still intentionally isolated on PR #6 / the feature branch until full real PPT end-to-end acceptance is complete.

Future agents must not assume that main-only history contains the latest Picker runtime fixes. Before changing Picker startup, Secure Tunnel, local MCP readiness, host-call handling, or the Windows launcher, read the feature branch files:

- `docs/ai-history/2026-08-30-picker-operational-baseline-final.md`
- `docs/session-handoff/20260830_PICKER_OPERATIONAL_BASELINE_FINAL.md`
- `docs/session-handoff/LATEST.md`
- `AI_STATE.json`

## Current accepted runtime facts

- Real Windows reboot cold-start: PASS.
- Picker MCP readiness and full tools/UI/resource/validation smoke: PASS.
- Startup-order race and Node child-process payload-buffer truncation are fixed on the feature branch.
- User reports the Picker flow in a normal ChatGPT conversation is progressing normally; final PPT file E2E completion had not yet been confirmed at this checkpoint.
- User chose to keep the existing foreground runtime: Picker server CMD (TCP 3000) + Secure MCP Tunnel CMD (TCP 8080) stay running/minimized while the workflow is in use.
- Do not convert to a background service unless the user explicitly asks later.
- Do not repeat CSP/template/port/tunnel/startup-order/default-buffer diagnosis without fresh evidence.
- PR #6 remains Draft; this pointer does not merge the feature code into main.
- GitHub Actions remain opt-in only.

## Modification rule

For future work, first compare current `main`, current feature-branch HEAD, and the operational handoff above. Preserve newer mainline workflow/catalog changes while applying only the additional Picker-runtime change required by new evidence.
