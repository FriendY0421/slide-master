# Slide Master Template Picker — Windows Reinstall & Recovery Runbook

Date established: 2026-08-30

## 0. Purpose

This document is the durable recovery authority for rebuilding the ChatGPT `Slide Master Template Picker` environment after a Windows format, PC replacement, profile reset, or accidental local deletion.

Target outcome:

`ChatGPT normal conversation` -> `Slide Master Template Picker` -> `OpenAI Secure MCP Tunnel` -> `Windows HOME-PC` -> `Picker MCP server` -> `GitHub FriendY0421/slide-master ACTIVE templates`

The repository is the source of truth for the picker app, launcher scripts, recovery instructions, template catalog, and registration/recommendation rules. Do not rely on a temporary folder or chat history as the only copy.

## 1. Current non-secret operating identifiers

- GitHub repository: `FriendY0421/slide-master`
- Picker app path: `apps/slide-master-picker/`
- MCP model-visible tool: `open_slide_master_template_picker`
- MCP local endpoint: `http://127.0.0.1:3000/mcp`
- Tunnel profile name: `slide-master-picker`
- Tunnel display name: `Slide Master Template Picker`
- Current known Tunnel ID: `tunnel_6a9024fa8a808191991fffb6092c66e3`
- Health endpoint: `http://127.0.0.1:8080/healthz`
- Ready endpoint: `http://127.0.0.1:8080/readyz`
- Runtime checkout: `%USERPROFILE%\Tools\slide-master-picker-runtime`
- Tunnel-client target: `%USERPROFILE%\Tools\tunnel-client\v0.0.13\full\tunnel-client.exe`
- Tunnel profile target: `%APPDATA%\tunnel-client\slide-master-picker.yaml`
- Runtime key target: `%LOCALAPPDATA%\OpenAI\SlideMasterTunnel\runtime_key.txt`
- Logs: `%LOCALAPPDATA%\OpenAI\SlideMasterTunnel\logs\picker.log` and `tunnel.log`
- Desktop launcher: `%USERPROFILE%\Desktop\Start_SlideMasterPicker.bat`

The Tunnel ID is an identifier, not the Runtime API Key. If the existing tunnel is unavailable after reinstall, create a new tunnel and replace the ID in the local profile.

## 2. Secrets and confidential assets that MUST NOT be stored in GitHub

Never commit any of the following:

- the actual OpenAI Runtime API Key (`sk-...` or equivalent secret value);
- passwords, service-account private keys, OAuth secrets, cookies, or session tokens;
- confidential company PPT/POTX source files unless the repository/storage classification explicitly allows them;
- customer, employee, internal metric, restricted URL, or other protected company data.

The Runtime API Key must live only in the local `runtime_key.txt` file and be referenced with tunnel-client's `file:` secret reference.

## 3. Repository recovery package

The files below are intentionally committed so a new Windows installation can reproduce the same setup:

- `ops/windows/Install_SlideMasterPicker_Runtime.bat`
  - clones/updates this repository into `%USERPROFILE%\Tools\slide-master-picker-runtime`;
  - uses `main` when the Picker app is available there;
  - temporarily falls back to `feat/apps-sdk-template-picker-20260827` while PR #6 remains unmerged;
  - runs `npm ci`, syntax checks and UI build;
  - copies the one-click launcher to the Desktop.
- `ops/windows/Start_SlideMasterPicker.bat`
  - first verifies an already-running Picker/Tunnel without restarting anything;
  - never terminates an existing process;
  - fails closed when verification fails and port 3000 or 8080 is already occupied;
  - starts Picker/Tunnel only when both ports are free;
  - returns `[READY]` only after stable health and a full MCP protocol smoke.
- `ops/windows/Verify_SlideMasterPicker_Runtime.ps1`
  - validates TCP 3000/8080, tunnel health/ready, continuous stability, MCP smoke markers, and post-smoke health;
  - writes machine-readable PASS/FAIL status under `%LOCALAPPDATA%\OpenAI\SlideMasterTunnel\logs`.
- `ops/windows/Run_Picker_Server.cmd`
  - starts the MCP Picker with `PICKER_SOURCE=github`.
- `ops/windows/Run_Secure_Tunnel.cmd`
  - starts tunnel-client with profile `slide-master-picker`.
- `ops/windows/slide-master-picker.yaml.example`
  - safe profile example containing no API key value.

## 4. Fresh Windows prerequisites

Install these first:

1. Git for Windows (`git` available on PATH).
2. Node.js with npm (`node` and `npm` available on PATH).
3. Python (`python` available on PATH).
4. OpenAI `tunnel-client` supported Windows build.
5. ChatGPT account/workspace access to Developer Mode / custom app registration used by the Slide Master Picker.

For the currently validated environment, tunnel-client `v0.0.13` was used. If a later supported version is used, update this runbook and `Run_Secure_Tunnel.cmd` only after successful local doctor + host smoke validation.

## 5. Restore the Slide Master runtime

From a cloned copy of this repository, run:

`ops\windows\Install_SlideMasterPicker_Runtime.bat`

Expected result:

- repository exists at `%USERPROFILE%\Tools\slide-master-picker-runtime`;
- `apps\slide-master-picker\package.json` exists;
- `npm ci` succeeds;
- `npm run check` succeeds;
- `npm run build` succeeds;
- `%USERPROFILE%\Desktop\Start_SlideMasterPicker.bat` exists.

While PR #6 is still draft/unmerged, the installer may use `feat/apps-sdk-template-picker-20260827`. After PR #6 is merged, `main` must become the normal recovery source and this fallback can be removed in a later cleanup.

## 6. Restore tunnel-client

Install the supported tunnel-client binary at:

`%USERPROFILE%\Tools\tunnel-client\v0.0.13\full\tunnel-client.exe`

Do not place a Runtime API Key in the repository or command file.

After installation, verify:

`tunnel-client.exe version`

Then use the product's `doctor` command/profile validation before relying on ChatGPT host calls.

## 7. Restore or recreate the Runtime API Key

If the old local secret is gone after formatting, create a new Runtime API Key in OpenAI Platform.

Required policy used for this Picker:

- key type: Restricted;
- `Tunnels: Read` enabled;
- `Tunnels: Use` enabled;
- unrelated API permissions remain disabled unless separately required.

Create:

`%LOCALAPPDATA%\OpenAI\SlideMasterTunnel\runtime_key.txt`

Put the secret value on exactly one line. Do not paste it into GitHub, Notion, Obsidian, or chat history.

Recommended Windows ACL hardening from Command Prompt/PowerShell under the target user account:

```text
icacls "%LOCALAPPDATA%\OpenAI\SlideMasterTunnel\runtime_key.txt" /inheritance:r
icacls "%LOCALAPPDATA%\OpenAI\SlideMasterTunnel\runtime_key.txt" /grant:r "%USERNAME%:(R)"
```

Re-check the ACL after creating/replacing the file.

## 8. Restore the tunnel profile

Create the directory if missing:

`%APPDATA%\tunnel-client`

Copy:

`ops\windows\slide-master-picker.yaml.example`

as:

`%APPDATA%\tunnel-client\slide-master-picker.yaml`

Then edit only the machine-specific values:

- replace `<WINDOWS_USER>` with the actual Windows profile folder name;
- reuse `tunnel_6a9024fa8a808191991fffb6092c66e3` if that OpenAI tunnel still exists and belongs to the correct workspace;
- otherwise create a new `Slide Master Template Picker` tunnel in OpenAI Platform and replace `control_plane.tunnel_id`.

The important routes are:

- MCP: `http://127.0.0.1:3000/mcp`
- health listener: `127.0.0.1:8080`
- API key reference: local `file:` path, never a literal secret.

## 9. Restore ChatGPT custom app registration

In ChatGPT Developer Mode/custom app settings:

1. Create or reconnect the app named `Slide Master Template Picker`.
2. Connection method: `Tunnel`.
3. Select the `Slide Master Template Picker` tunnel.
4. Authentication: `None / No authentication` for the Picker MCP itself.
5. Do not configure OAuth for this MCP server; it intentionally does not advertise OAuth.
6. Scan tools/actions.
7. Confirm `open_slide_master_template_picker` appears.
8. Open a new normal ChatGPT conversation and test the app.

Expected usage example:

`@Slide Master Template Picker 삼성전자서비스 미래에 대한 ppt`

## 10. One-click daily operation

Double-click:

`%USERPROFILE%\Desktop\Start_SlideMasterPicker.bat`

The launcher is fail-closed and non-destructive. It NEVER terminates an existing process.

Normal outcomes:

```text
[READY] Existing Picker runtime is healthy.
Nothing was restarted or terminated.
```

or, after a clean reboot when ports 3000 and 8080 are free:

```text
[2/4] Ports are free. Starting Picker MCP...
[3/4] Starting Secure Tunnel...
[4/4] Waiting for stable end-to-end readiness...
[READY] Picker + tunnel + MCP smoke all passed.
```

READY now requires continuous local stability plus a real MCP protocol smoke. Port-open or `/readyz` alone is not sufficient.

If verification fails while port 3000 or 8080 already has a listener, the launcher exits with `ACTION REQUIRED` and does not kill, replace, or restart that process. Finish other work first and perform a user-controlled Windows restart when safe.

Do not repeatedly press ChatGPT `Retry` before the launcher prints `[READY]`; repeated calls during tunnel warm-up can produce misleading 404/429 failures.

## 11. Validation after reinstall

Local checks:

1. `127.0.0.1:3000` is LISTENING.
2. `http://127.0.0.1:8080/healthz` returns HTTP 200 and `live`.
3. `http://127.0.0.1:8080/readyz` returns HTTP 200 and `ready`.
4. `apps/slide-master-picker`: `npm run smoke` passes.
5. tunnel-client doctor/profile validation returns success.
6. ChatGPT can discover `open_slide_master_template_picker`.
7. Actual Picker UI renders registered ACTIVE templates.
8. Final UI selection must return `deck:<id> | preset:<id>` into the ChatGPT conversation before PR #6 is considered fully host-validated.

## 12. Troubleshooting

### `Failed to fetch template`
Most likely first check:

- port 3000 Picker MCP stopped;
- port 8080 Secure Tunnel stopped;
- tunnel `/readyz` not ready.

Run `Start_SlideMasterPicker.bat`, then inspect `picker.log` and `tunnel.log`.

### Plugin exists but template UI does not load
Confirm the tunnel is ready and the custom app is attached/selected for the current message. Plugin registration can remain visible even while the HOME-PC runtime is offline.

### OAuth configuration error / `does not implement OAuth`
Set the custom app authentication to `None / No authentication` instead of OAuth.

### `mcp_server_reachable` refused
Start the Picker MCP first and verify `127.0.0.1:3000`.

### 404 followed by 429 during repeated retries
Do not repeatedly retry a dead runtime. Restore port 3000 + tunnel readiness first, then issue one fresh ChatGPT call.

## 13. Update and maintenance policy

When Picker/Tunnel installation details change:

1. update this runbook in the same change;
2. update `ops/windows/*` scripts if paths or versions change;
3. keep the Runtime API Key out of GitHub;
4. run local `npm run check`, `npm run build`, `npm run smoke`;
5. run tunnel health/ready checks;
6. run actual ChatGPT host smoke;
7. record the validated version/commit in PR/handoff docs;
8. do not use GitHub Actions unless the user explicitly requests/approves it.

## 14. Relationship with FAH and template registration

FAH governs company/user template onboarding, while `slide-master` remains the technical single source of truth for template metadata, recommendation scoring, Picker discovery and rendering.

After a new company/user template is approved:

`source -> security classification -> CANDIDATE -> preview approval -> ACTIVE -> recommendation audit -> live Picker discovery`

The Windows recovery package described here restores the Picker runtime only. It must not bypass template security classification or expose confidential source templates.

## 15. Recovery completion checklist

- [ ] Git / Node.js / npm / Python installed
- [ ] repository runtime restored
- [ ] npm dependencies installed and checks passed
- [ ] tunnel-client installed
- [ ] Runtime API Key recreated locally with restricted permissions
- [ ] local secret file ACL hardened
- [ ] tunnel profile restored
- [ ] tunnel ID validated/replaced
- [ ] Desktop launcher restored
- [ ] `/healthz` = live
- [ ] `/readyz` = ready
- [ ] ChatGPT custom app registered with Authentication=None
- [ ] `open_slide_master_template_picker` discovered
- [ ] real Picker UI test passed
- [ ] final template/preset return path tested

## 16. Stale runtime / CSP host-render diagnostic rule (2026-08-30)

A healthy tunnel does not prove the latest Picker build is running. `/healthz=live` and `/readyz=ready` only prove local tunnel/runtime connectivity.

After any `server.js`, `app.js`, MCP metadata, CSP, or UI build change:

1. run syntax/build checks without disturbing the active runtime;
2. identify the process currently listening on port 3000 and record its runtime branch/HEAD;
3. if a restart is required, wait for an explicit maintenance window or user approval; never terminate an unrelated or currently needed process automatically;
4. after the user-controlled restart, run `Verify_SlideMasterPicker_Runtime.ps1` and require continuous stable health plus the full MCP smoke;
5. only after `[READY]` test through ChatGPT once.

The launcher must never contain `taskkill`, `Stop-Process`, or equivalent automatic termination logic. A source-code diff, an open port, or tunnel `/readyz` alone is insufficient evidence of a usable Picker.

## 17. Reboot startup readiness rule (2026-08-30)

A real Windows reboot exposed a startup race: the local process/tunnel can still be warming up while ChatGPT tries to fetch the app template. Repeated retries during this period can produce `Failed to fetch template`, 404, and then 429 responses.

Canonical reboot flow:

`Windows restart -> run Start_SlideMasterPicker.bat -> wait for [READY] -> issue exactly one ChatGPT Picker request`

`[READY]` is valid only when all of the following pass:

- TCP port 3000 is reachable;
- TCP port 8080 is reachable;
- `/healthz` returns `live`;
- `/readyz` returns `ready`;
- those conditions remain continuously stable for the configured stability window;
- `scripts/mcp-smoke.mjs` passes and confirms tools, picker payload, resource metadata, UI resource, and final validation.

If any step fails, do not loop ChatGPT retries. Use `%LOCALAPPDATA%\OpenAI\SlideMasterTunnel\logs\runtime.verify.status.json` and resolve the runtime first.
