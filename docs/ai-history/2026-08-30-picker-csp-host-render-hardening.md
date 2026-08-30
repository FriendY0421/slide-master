# 2026-08-30 — Picker CSP / Host Render Hardening

## Trigger
A real ChatGPT call showed `Slide Master Template Picker CSP 꺼짐`. The assistant then incorrectly said the picker had loaded normally, but no template cards, preview images, or selectable UI appeared and the flow stopped.

## Root causes confirmed
1. A stale Node process on port 3000 could continue serving an older build even after the Git working tree had newer fixes.
2. MCP tool success only proved picker payload generation; it did not prove the ChatGPT host rendered the Apps SDK view.
3. App resource/tool metadata did not explicitly expose the CSP/ChatGPT compatibility metadata used by the current host.
4. `app.ontoolresult` treated app-only validation results as if picker data were missing and could replace a working gallery with an error.
5. Template previews are embedded `data:image/svg+xml;base64,...` resources, not remote GitHub image fetches.

## Fixes applied
- Resource CSP explicitly allows `data:` preview resources and declares no network connect domains.
- Tool metadata exposes both Apps SDK UI resource metadata and ChatGPT compatibility metadata.
- Picker result now exposes `payload_ready=true` and `host_ui_rendered=false` separately.
- Model instructions explicitly forbid claiming the gallery is visible until the app view reports `SLIDE_MASTER_PICKER_UI_RENDERED`.
- App view reports `SLIDE_MASTER_PICKER_UI_RENDERED` through `updateModelContext` only after real picker payload reception and gallery render.
- App ignores validation tool results that do not contain picker payload, preventing the final-selection call from destroying the gallery.
- If the host does not deliver picker data to the view within 8 seconds, the view shows an explicit fail-closed error instead of hanging.

## Runtime diagnostic finding
The first post-edit smoke still hit an old server process and reported a false validation schema error. Current `server.js` did not contain the alleged extra property. After terminating the stale port-3000 Node process, rebuilding, and restarting the stable runtime, the error disappeared.

Durable rule: after server/UI code changes, do not trust source inspection plus `/healthz` alone. Restart the port-3000 Picker process and run `npm run smoke` against the live process.

## Local acceptance evidence
Exact test purpose: `삼성전자서비스 미래 대응 전략`

- ACTIVE catalog: 21
- shortlist: 6
- first recommendation: `layout:future_tech`
- displayed production presets: 5
- `payload_ready`: true
- `host_ui_rendered`: false at server-only stage, as designed
- UI resource: 484084 bytes, module bundle present
- CSP: `connectDomains=[]`, `resourceDomains=["data:"]`
- final validation: PASS
- returned token: `layout:future_tech | preset:executive_brief`
- tunnel `/healthz`: HTTP 200 `live`
- tunnel `/readyz`: HTTP 200 `ready`
- GitHub Actions: not used

## Remaining proof before PR #6 merge
Local MCP/server/tunnel behavior is validated, but PR #6 remains Draft until a real eligible ChatGPT conversation proves all host-side steps:

1. invoke `@Slide Master Template Picker 삼성전자서비스의 미래 대응 전략 ppt작성`;
2. visible interactive gallery actually renders;
3. preview images are visible;
4. `Future Tech` is ranked appropriately;
5. template detail and preset controls work;
6. final confirmation returns the validated selection token to chat through `app.sendMessage`;
7. only then mark PR #6 ready/merge.

Do not report “picker loaded normally” from MCP tool success alone. If visible cards are absent, treat the host render as failed and stop PPT production.

## First diagnostic order for recurrence
`port 3000 process/version -> npm run smoke -> 8080 health/ready -> tool/resource metadata -> host UI render signal -> app final selection`

This order supersedes repeating broad template/image/network debugging first.
