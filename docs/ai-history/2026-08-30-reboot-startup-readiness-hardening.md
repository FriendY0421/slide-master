# Slide Master Picker reboot startup readiness hardening

Date: 2026-08-30 KST
Status: LOCAL COLD-START ACCEPTANCE PASS / CHATGPT HOST ACCEPTANCE PENDING

## Incident

After a real Windows shutdown/restart, ChatGPT showed repeated `Failed to fetch template` errors. The observed sequence included an initial 404 followed by 429 responses after repeated retries. The Picker selection gate correctly prevented PPT generation, but the runtime readiness path was not reliable enough after reboot.

The Desktop launcher also produced an error. During investigation, the in-progress repository launcher was found truncated at 37 lines, which is an independent direct launcher defect.

## Confirmed root causes

1. Startup readiness race: local process/tunnel warm-up can lag behind a ChatGPT app request.
2. `/readyz=ready` or an open port alone is weaker than full MCP usability.
3. Repeated ChatGPT retries before stable readiness can turn the original failure into misleading 404/429 sequences.
4. Automatic port-process termination is unsafe because the user may have unrelated or concurrent work running.
5. The launcher working copy had been partially written and was therefore incomplete.

## Safety decision

The launcher is now fail-closed and non-destructive. It MUST NOT use `taskkill`, `Stop-Process`, or equivalent automatic process termination.

## New launcher behavior

1. Verify an already-running runtime first.
2. If it is healthy, return `[READY]` without restarting anything.
3. If verification fails and port 3000 or 8080 is already occupied, return `ACTION REQUIRED` and stop there.
4. Only when both ports are free may the launcher start the Picker and Tunnel helpers.
5. After startup, require continuous stable health and a real MCP protocol smoke before returning `[READY]`.

The verifier now requires:

- TCP 3000 reachable;
- TCP 8080 reachable;
- `/healthz = live`;
- `/readyz = ready`;
- the above conditions continuously stable for the configured window;
- `scripts/mcp-smoke.mjs` exit code 0;
- smoke markers for tools, picker payload, resource metadata, UI resource, and final validation;
- a final post-smoke runtime health check.

## Non-disruptive validation completed

- PowerShell verifier parse: PASS.
- automatic process-termination command scan: PASS / none found.
- repository launcher copied to Desktop and SHA-256 matched.
- Current runtime check at the time of hardening found both ports 3000 and 8080 not listening. No process was terminated by this work.
- Because the user had other work running, no Picker/Tunnel startup, shutdown, or Windows restart was performed.

## Pending acceptance

A user-controlled Windows restart is still required for the final cold-start acceptance test.

Required acceptance flow:

`restart Windows -> run Desktop Start_SlideMasterPicker.bat -> wait for [READY] -> issue one ChatGPT Picker request`

Do not repeatedly retry the ChatGPT app before `[READY]`.

The Apps SDK PR #6 remains Draft until the real ChatGPT host renders the template cards/images and the final selection returns to the conversation.

GitHub Actions were not used.

## Real post-reboot acceptance result and follow-up hardening

The first real cold-start acceptance was executed on 2026-08-30 after Windows had rebooted. It failed safely rather than producing a false READY.

Evidence:
- Picker/Tunnel ports were initially free;
- Tunnel started before Picker MCP had completed its build/start path;
- Tunnel's first MCP initialize/probe received `ECONNREFUSED 127.0.0.1:3000`;
- Picker later listened on 3000;
- Tunnel stayed `/healthz=live` but `/readyz=503`;
- stable end-to-end readiness was never established within the launcher timeout.

A second defect was exposed while validating the full smoke path: `validate_slide_master_selection` reloads the payload with limit 10, whose JSON can exceed Node child-process default buffering. The subprocess output was truncated at roughly the 1 MiB boundary and surfaced as an MCP tool error. This was not a bad template/preset selection.

Follow-up hardening:
- the launcher now waits for a dedicated lightweight local MCP readiness probe before starting Secure Tunnel;
- the probe verifies both required Picker MCP tools;
- Picker payload spawning now uses a 16 MiB `maxBuffer`;
- the full smoke emits `RESOURCE_META` and supports an override MCP URL for isolated testing;
- verifier marker matching is literal and deterministic.

Validation after the follow-up hardening:
- local MCP readiness probe: PASS on first attempt;
- isolated patched server on port 3001: started successfully;
- full open/resource/validate smoke against 3001: PASS, `VALIDATE true`, exit 0;
- JavaScript, PowerShell, and Git diff checks: PASS.

The temporary 3001 test server was created only for isolated verification and was removed afterward. No unrelated port owner was terminated. GitHub Actions were not used.

Pending acceptance remains one controlled reboot and one real ChatGPT host request after launcher `[READY]`. PR #6 remains Draft until real cards/images render and the final selection returns through the ChatGPT app.

## Second real post-reboot acceptance — PASS

At 2026-08-30 20:51:04 KST, the hardened runtime passed the second real Windows cold-start acceptance on HOME-PC.

Observed acceptance evidence:
- pre-tunnel local MCP protocol gate: `MCP_READY PASS`;
- runtime verifier: `ok=true`, `stage=ready`, `attempt=1`;
- branch/HEAD in verifier: `feat/apps-sdk-template-picker-20260827` / `a63a95078ef3`;
- smoke markers: `TOOLS`, `PICKER`, `UI`, `RESOURCE_META`, `CSP`, and `VALIDATE true`;
- verifier exit code: `0`.

This closes the local reboot/startup acceptance. The only remaining acceptance is the real ChatGPT host rendering/selection round trip. PR #6 remains Draft until that host-side acceptance succeeds. GitHub Actions were not used.