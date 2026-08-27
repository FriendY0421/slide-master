# 2026-08-27 — Slide Master Apps SDK Template Picker

## Goal
Replace inconsistent prose-only GPTS template recommendations with a deterministic conversation-native interactive picker.

## Implemented on branch
`feat/apps-sdk-template-picker-20260827`

- New read-only MCP Apps server: `apps/slide-master-picker/`.
- Primary model-visible tool: `open_slide_master_template_picker`.
- App-only validation tool: `validate_slide_master_selection`.
- MCP Apps UI resource: `ui://slide-master/template-picker-v1.html`.
- UI MIME: `text/html;profile=mcp-app`.
- Live payload helper: `.claude/skills/ppt-master/scripts/template_picker_payload.py`.
- Exact current ACTIVE template catalog; no hard-coded template ids/counts.
- Default recommendation target 6, configurable 5–10.
- Recommended/all tabs, search, Deck/Layout filter, pagination, real representative previews, up to 6 detail examples, Free Design.
- Purpose-ranked production presets, maximum 5.
- Final template/preset is validated server-side, then sent back into the conversation using MCP Apps `updateModelContext` + `sendMessage`.
- `record_template_choice_v2.py` now accepts/validates `--preset` and preserves `production_preset` in selection evidence.
- GPTS guard/contract/instructions now reference the exact picker tool.

## Validation completed before HOME-PC disconnect
- Node.js v24.18.1 / npm 11.16.0 available.
- `@modelcontextprotocol/sdk` 1.30.0 installed locally.
- `@modelcontextprotocol/ext-apps` installed; UI bundle build PASS (~723 KB on the first implementation).
- JavaScript server syntax check PASS on the first implementation.
- Python payload helper test PASS for `삼성전자서비스 천안센터 문제점`: 11 selectable templates, 6 shortlist, McKinsey first, 6 real detail previews.
- The first MCP smoke exposed one defect: a single Streamable HTTP server/transport was reused across requests and returned HTTP 500.

## Fix prepared after defect
The server was refactored to create a fresh `McpServer` + stateless `StreamableHTTPServerTransport` per `/mcp` request, following the MCP SDK stateless pattern. It was also migrated to `registerAppTool` / `registerAppResource` and the standard MCP Apps resource MIME.

## Current status
`LOCAL_MCP_PROTOCOL_VALIDATED_CHATGPT_HOST_SMOKE_PENDING`

HOME-PC reconnected and the corrected server was re-run. Local MCP protocol validation now passes. Do **not** merge this branch to main until the remaining ChatGPT Developer Mode host smoke is completed.

### Validation completed after reconnect
- `npm install`, bundle build and JavaScript checks: PASS.
- Python payload/selection scripts compile: PASS.
- `PICKER_SOURCE=local`: initialize, tools/list, picker call, UI resource read and final selection validation: PASS.
- `PICKER_SOURCE=github`: same MCP smoke: PASS.
- Picker result: 11 selectable / 6 shortlist / `deck:mckinsey` first / 5 production presets / 6 detail previews.
- Picker evidence + `--preset storytelling_proposal` selection record + template gate: PASS.
- Direct-template + preset compatibility: PASS.
- UI resource size during smoke: about 589 KB, bundled module present.

### Remaining host validation

1. `npm install && npm run build && npm run check`.
2. Start with `PICKER_SOURCE=local npm start`.
3. MCP client/Inspector can initialize `/mcp`.
4. `tools/list` contains `open_slide_master_template_picker`; app-only validation tool is not model-visible where host honors visibility.
5. Calling picker returns 5–10 shortlist items and real preview payload.
6. UI resource resolves as `text/html;profile=mcp-app`.
7. App final selection validates and sends a user message back to the host.
8. Repeat with `PICKER_SOURCE=github`.

GitHub Actions were not used.
