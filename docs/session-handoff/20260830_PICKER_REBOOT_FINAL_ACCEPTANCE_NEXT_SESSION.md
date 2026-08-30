# Slide Master Picker — Next Session Handoff

Date: 2026-08-30 19:51 KST
Repository: `FriendY0421/slide-master`
Runtime branch: `feat/apps-sdk-template-picker-20260827`
Current HEAD: `cc9cbdd7261443fcb2899e1deb024a2cc81ee673`
PR: #6 (Draft)

## Why this handoff exists

The conversation became long during diagnosis of the post-Windows-reboot Picker failure. Continue from this checkpoint instead of re-investigating CSP, template data, or tunnel basics from the beginning.

## User-visible incident

After shutting down and restarting Windows, a ChatGPT Picker request showed repeated:
- `Failed to fetch template`
- initial 404
- later 429 after repeated retries

The attached/desktop launcher also showed an error. PPT generation correctly remained blocked at `TEMPLATE_SELECTION`.

## Confirmed diagnosis

1. Reboot startup has a readiness race between the local Picker, Secure MCP Tunnel, and the first ChatGPT app request.
2. An open port or `/readyz=ready` alone is not sufficient proof of full MCP usability.
3. Repeated ChatGPT retries before stable readiness can produce misleading 404/429 sequences.
4. Automatic process termination is prohibited because unrelated concurrent work may be using the same machine.
5. The prior launcher working copy had been truncated; the repository launcher has now been hardened.
## Hardened runtime now in GitHub

`ops/windows/Start_SlideMasterPicker.bat` is fail-closed and non-destructive.

Required READY verification:
- TCP 3000 reachable
- TCP 8080 reachable
- `/healthz = live`
- `/readyz = ready`
- continuous stable-health window
- real MCP protocol smoke PASS
- expected tools/picker/resource/UI/final-validation markers
- final post-smoke health check

If 3000 or 8080 is occupied while verification fails, return `ACTION REQUIRED`; do not kill processes automatically.

Detailed history:
`docs/ai-history/2026-08-30-reboot-startup-readiness-hardening.md`

## Exact remaining work

Do NOT restart the investigation from scratch. The next task is the final cold-start acceptance test of the hardened launcher:

`restart Windows -> run Desktop Start_SlideMasterPicker.bat -> wait until [READY] -> send exactly one ChatGPT Picker request`

Do not repeatedly press Retry before `[READY]`.

If the hardened launcher itself fails, capture its exact console output plus the latest Picker/Tunnel logs before changing code. Diagnose the failed READY condition specifically.

If `[READY]` passes but ChatGPT still shows `Failed to fetch template`, then inspect the Secure MCP Tunnel remote path / host-side app delivery. Do not classify it as a local port/CSP/template problem without evidence.

PR #6 must remain Draft until real ChatGPT cards/images render and final selection returns through the app.
GitHub Actions must not be used unless the user explicitly requests them.

## Next-session first action

Read this file and `docs/ai-history/2026-08-30-reboot-startup-readiness-hardening.md`, verify current HEAD/status, then continue only from `POST-REBOOT ACCEPTANCE PENDING`.
