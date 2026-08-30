# Slide Master Picker — Operational Baseline Handoff

Date: 2026-08-30 KST
Repository: `FriendY0421/slide-master`
Branch: `feat/apps-sdk-template-picker-20260827`
Status: `OPERATING BASELINE ACCEPTED / FULL PPT E2E PENDING`

## Start here next time

Do not repeat the old CSP/template/port/tunnel/startup-race investigation. Read:
1. `docs/ai-history/2026-08-30-picker-operational-baseline-final.md`
2. this handoff
3. `docs/session-handoff/LATEST.md`
4. `AI_STATE.json`

## Current accepted facts

- Windows reboot cold-start: PASS.
- `MCP_READY PASS`; full MCP/UI/resource/validation smoke: PASS.
- Startup ordering and payload-buffer defects are fixed.
- General ChatGPT host flow is user-observed operating normally; full PPT file completion was not yet confirmed.
- PPT-project conversation Developer MCP `FORBIDDEN` was a conversation capability issue.
- User chose the existing two-visible-CMD-window operating model; no background-service conversion.
- Keep Picker server (3000) and Secure MCP Tunnel (8080) running while using the Picker/PPT workflow.
- PR #6 stays Draft until real selection return and full downstream PPT path are accepted.
- GitHub Actions remain prohibited unless explicitly requested.

## Future modification rule

Any later agent must compare current code/state against this checkpoint first. Only investigate or modify the failing stage supported by new evidence; do not re-run already-closed root-cause work by default. Update this repository's history/state/handoff after every meaningful change.
