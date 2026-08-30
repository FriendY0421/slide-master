# Picker reboot readiness checkpoint

Date: 2026-08-30 KST
Branch: `feat/apps-sdk-template-picker-20260827`
State: POST-REBOOT ACCEPTANCE PENDING

## Latest confirmed state

A real Windows restart reproduced `Failed to fetch template` before the local Picker/Tunnel path had become reliably usable. Repeated retries produced 404/429 behavior.

The runtime hardening work is now non-destructive:

- `ops/windows/Start_SlideMasterPicker.bat` never kills an existing process;
- it verifies an existing runtime before doing anything;
- a failed verification plus an occupied port fails closed with `ACTION REQUIRED`;
- only free ports allow a new Picker/Tunnel startup;
- `[READY]` requires continuous stability plus full MCP smoke;
- the Desktop launcher is synchronized from the repository copy.

## User concurrency constraint

Do not terminate, restart, or replace existing processes while the user has other work running. A restart is user-controlled only.

At the last non-disruptive check, ports 3000 and 8080 were both not listening. This work did not stop them.

## Final acceptance when the user is ready

1. Save/finish all unrelated work.
2. Restart Windows manually.
3. Run `%USERPROFILE%\Desktop\Start_SlideMasterPicker.bat`.
4. Wait for `[READY] Picker + tunnel + MCP smoke all passed.`
5. Only then issue one `@Slide Master Template Picker ...` request in ChatGPT.
6. If the launcher reports `NOT READY` or `ACTION REQUIRED`, do not loop ChatGPT retries; inspect `runtime.verify.status.json` first.

## Remaining documentation sync

`docs/ops/SLIDE_MASTER_PICKER_WINDOWS_RECOVERY.md` was write-locked by another process during this session. Do not terminate that process. The new history and this handoff are the newest authority until the recovery runbook is synchronized after the user-controlled restart.

## Merge policy

PR #6 remains Draft until actual ChatGPT host acceptance proves visible template cards/images and final `app.sendMessage` selection return.

GitHub Actions remain disabled unless explicitly requested by the user.
