# Slide Master Picker operational baseline — 2026-08-30

## Status

`LOCAL COLD-START PASS / REAL NORMAL CHAT PICKER FLOW USER-CONFIRMED OPERATING / FULL PPT E2E STILL PENDING`

## Confirmed runtime facts

- Branch: `feat/apps-sdk-template-picker-20260827`
- Cold-start after real Windows reboot passed on 2026-08-30.
- Local MCP readiness: `MCP_READY PASS`.
- Full smoke: tools, picker payload, UI resource, `RESOURCE_META`, CSP and `VALIDATE true` all passed.
- Secure Tunnel reached `ready` on the first verifier attempt after the startup-order fix.
- The payload subprocess uses a 16 MiB `maxBuffer`; do not revert to the default child-process buffer.
- Launcher ordering is Picker start -> local MCP readiness -> Secure Tunnel start -> stable full verifier.
- Launcher remains fail-closed and non-destructive; it must not auto-kill owners of ports 3000/8080.

## Real ChatGPT host result

- The PPT-project conversation returned `FORBIDDEN: This conversation does not support developer MCPs`; this was a host/conversation capability limit, not a local runtime defect.
- A new normal ChatGPT conversation was then used.
- User reported the Slide Master Template Picker flow appears to be operating normally and is progressing without errors.
- The final PPT file had not yet been generated at the time of this checkpoint, so full PPT end-to-end acceptance is not claimed.
- PR #6 remains Draft until the interactive selection return and complete PPT path are confirmed.

## Accepted operating method

The user explicitly chose to keep the current foreground runtime model. Do not convert it to a hidden/background service unless the user later requests that change.

During Slide Master Picker use, keep both runtime windows alive:
1. `node src/server.js` on TCP 3000 — Picker MCP server.
2. `tunnel-client.exe run --profile slide-master-picker` with health/admin on TCP 8080 — Secure MCP Tunnel.

Closing either runtime window can interrupt a new Picker request or selection-return flow. Keep both windows open/minimized until the PPT workflow is finished.

## Do not repeat these investigations without new evidence

Do not restart diagnosis from CSP, template inventory, port basics, tunnel installation, startup ordering, or Node default buffer. Those issues were already diagnosed and hardened. First read this file, `docs/session-handoff/LATEST.md`, and the latest handoff.

If a future failure occurs, classify it from fresh evidence:
- launcher not READY -> inspect exact readiness stage/log;
- READY but ChatGPT cannot call -> inspect host/developer-MCP capability;
- Picker displays but selection fails -> inspect app selection/message return;
- selection succeeds but PPT fails -> inspect downstream generation/QA only.

## Safety and control

- GitHub Actions were not used and remain opt-in only.
- Do not terminate unrelated processes automatically.
- Preserve the FAH template-selection gate and explicit user selection before PPT generation.
