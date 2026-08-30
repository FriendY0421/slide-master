# 2026-08-31 — Picker confirm reliability hardening

## Trigger
Real ChatGPT test rendered the Slide Master Picker surface but the final selection could not be confirmed. The assistant retried the tool and incorrectly treated the initial `host_ui_rendered:false` field as proof of render failure.

## Evidence
- Runtime logs around the failed interaction contain intermittent Tunnel upstream HTTP 502 for MCP `tools/call` and `initialize`.
- Local MCP/resource/CSP smoke remains healthy.
- CSP metadata is already exposed in both current `ui.csp` and compatibility `openai/widgetCSP` forms.
- Therefore `CSP 꺼짐` was not established as the direct cause of the selection-confirm failure.

## Root causes
1. Final confirm synchronously depended on an additional `validate_slide_master_selection` server call. A transient host/Tunnel 502 therefore failed the whole UI confirmation.
2. Initial tool output used `host_ui_rendered:false`, although the server cannot know the host render state at initial response time. This invited false model diagnosis.
3. The Picker needed a stronger fail-soft handoff when `app.sendMessage` is unavailable.
## Fix
- Picker payload received from the MCP server is now the primary selection authority.
- Server revalidation is advisory: success records `server_validated`; failure falls back to `local_payload` without blocking the user.
- Initial render state is now `host_ui_rendered:null` + `host_ui_render_status: pending_app_signal` rather than false.
- Model context explicitly states that false/null at initial tool time is not a render-failure signal.
- Final handoff remains fail-closed for PPT generation: `NEXT_STATE=WAIT_STORYLINE_PREVIEW`, `GENERATION_ALLOWED=false`.
- Requested slide count is extracted dynamically from the purpose; no 20-slide hard-code remains.
- If `app.sendMessage` fails, the full official selection/handoff message is displayed and clipboard copy is attempted.

## Verification
- `npm run check`: PASS
- `npm run build`: PASS
- live port-3000 resource contains the new preview gate and local validation fallback
- isolated port-3001 smoke: PASS
- isolated initial state: `host_ui_rendered=null`
- selection validation: PASS
- workflow contract: `WAIT_STORYLINE_PREVIEW / generation_allowed=false / storyline_preview_required=true`

## Operating rule
Do not diagnose visible Picker UI as failed solely from the initial `host_ui_rendered` field. For final-selection failures, inspect the confirm bridge first. A transient Tunnel/server-validation error must not erase a valid template+preset selection already present in the server-issued Picker payload.

Implementation commit: `71c93082088a9dd826481d581d8c5d1fd3e38257`
