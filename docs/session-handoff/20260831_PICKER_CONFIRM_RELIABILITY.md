# Picker confirm reliability handoff — 2026-08-31

## Current status
The Picker selection-confirm path has been hardened after a real ChatGPT failure. The visible UI could load, but the extra server validation call intermittently encountered Tunnel upstream HTTP 502 and blocked confirmation.

## New contract
- The MCP-issued Picker payload is sufficient to validate that the selected template and preset came from the current server catalog.
- `validate_slide_master_selection` remains useful but is advisory, not a single point of failure.
- On validation-call failure, the app uses the payload-backed local selection token and continues.
- Initial host render state is unknown/pending, never a boolean failure from the server.
- PPT generation remains prohibited until the separate full storyline preview is shown, edited as needed, and explicitly approved.

## User-visible flow
`template -> preset -> selection confirm -> research/verification -> full slide-by-slide preview -> user edits -> explicit approval -> generation -> Design V3 QA -> PPTX`

The final Picker button communicates selection confirmation and storyline preview, not immediate PPT production.
## Verification evidence
- source syntax/build PASS
- port-3000 live resource: new `WAIT_STORYLINE_PREVIEW` and local fallback code present
- isolated port-3001 MCP smoke PASS
- initial server render state: `null / pending_app_signal`
- server selection validation PASS
- workflow: `WAIT_STORYLINE_PREVIEW`, `generation_allowed=false`, `storyline_preview_required=true`

## Runtime application note
The UI bundle is read from disk by the running server resource handler, so the critical 502-tolerant confirmation logic is already available to new Picker resource loads on the current port-3000 process. The server-side `host_ui_rendered:null` structured field requires the Picker server to be restarted normally; do not kill unrelated processes or alter the Tunnel just for this metadata change.

## First diagnostic order if confirmation still fails
1. confirm the visible app has the new `선택 확정 → 장표안 미리보기` button;
2. inspect Tunnel log for HTTP 502 near the click time;
3. confirm UI shows `server_validated` or `local_payload` rather than resetting to gallery;
4. if automatic chat delivery fails, use the displayed full handoff text without losing the selection;
5. only then investigate host app rendering/bridge behavior.

GitHub Actions remain opt-in only and were not used.
