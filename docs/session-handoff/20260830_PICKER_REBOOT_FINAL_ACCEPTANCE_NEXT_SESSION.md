# Slide Master Picker — Next Session Handoff

Date: 2026-08-30 20:35 KST
Repository: `FriendY0421/slide-master`
Runtime branch: `feat/apps-sdk-template-picker-20260827`
Baseline HEAD before acceptance fix: `1146659d9db845f2a256f5e4096b9f7e97cd4f71`
PR: #6 (Draft)
Status: STARTUP-ORDER + PAYLOAD-BUFFER HARDENED / SECOND POST-REBOOT ACCEPTANCE PENDING

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

Read this file and `docs/ai-history/2026-08-30-reboot-startup-readiness-hardening.md`, verify current HEAD/status, then continue only from `SECOND POST-REBOOT ACCEPTANCE PENDING` and the acceptance-fix sections appended below.

## Post-reboot acceptance attempt #1 — 2026-08-30

The requested real cold-start acceptance was executed after the Windows reboot. The hardened launcher failed closed exactly as intended; it did not claim READY and did not terminate any pre-existing process.

Observed sequence:
- existing-runtime full verification failed;
- ports 3000/8080 were free, so Picker and Tunnel startup was allowed;
- the Picker build/start path took long enough that Tunnel probed MCP before port 3000 was accepting connections;
- Tunnel logged `ECONNREFUSED 127.0.0.1:3000` during its initial MCP readiness probe;
- Picker later became reachable on 3000;
- Tunnel `/healthz` returned 200/live, but `/readyz` remained 503;
- the launcher timed out without the required 10-second stable READY window and returned `[NOT READY]`.

This proves the remaining reboot defect was startup ordering, not the previously investigated CSP/template/port basics.

A second cold-start acceptance is required after the fixes below. Do not repeat the old investigation unless new evidence specifically points there.

## Acceptance fix prepared after attempt #1

1. Added `scripts/mcp-ready.mjs`, a small local MCP protocol readiness probe that verifies both required Picker tools without generating the full gallery payload.
2. Added `ops/windows/Wait_SlideMasterPicker_LocalMcp.ps1` and changed the launcher to require local MCP readiness before Secure Tunnel startup.
3. Increased the Picker payload subprocess `maxBuffer` to 16 MiB. The final validation path uses limit 10 and can exceed Node's default child-process buffer; before this fix the JSON was truncated and validation returned an error.
4. `mcp-smoke.mjs` now emits the verifier-required `RESOURCE_META` marker and accepts `MCP_URL` for isolated validation.
5. Verifier marker checks use literal `.Contains()` matching.

Non-disruptive validation completed:
- local pre-tunnel readiness against the running Picker: `LOCAL_MCP_READY=PASS attempt=1`;
- patched Picker started separately on port 3001 for isolation;
- full smoke on 3001: `VALIDATE true ...`, exit 0;
- `npm run check`: PASS;
- Node syntax checks for both smoke/readiness scripts: PASS;
- PowerShell parser checks: PASS;
- `git diff --check`: PASS.

## Exact next action

`controlled Windows reboot -> Desktop Start_SlideMasterPicker.bat -> confirm LOCAL_MCP_READY=PASS occurs before Tunnel startup -> wait for [READY] -> send exactly one ChatGPT Picker request`

Do not repeatedly retry ChatGPT before `[READY]`. GitHub Actions remain prohibited unless the user explicitly requests them.
