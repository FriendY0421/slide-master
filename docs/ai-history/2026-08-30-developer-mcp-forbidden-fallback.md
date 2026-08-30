# Developer MCP forbidden fallback — 2026-08-30

## Incident
Repeated `@Slide Master Template Picker` attempts showed no usable cards/images. Direct tool invocation returned `FORBIDDEN: This conversation does not support developer MCPs`.

## Root-cause classification
- This exact `FORBIDDEN` result is a ChatGPT host/product-surface rejection.
- It is not evidence of a GitHub catalog, preview SVG, CSP, port 3000, or Secure MCP Tunnel defect.
- Do not repeat those lower-layer investigations unless independent runtime evidence changes.
- A tool-attempt or payload-ready result is never proof that a visible picker rendered.

## Durable fallback
- Primary: Apps SDK / App Block picker only on a host that actually supports the developer MCP app.
- Automatic fallback when Desktop Commander is available: `ops/windows/Open_SlideMasterPicker_Fallback.bat <purpose>`.
- The fallback runs `template_gallery_inline_html.py --source github`, embeds real previews as data URIs, opens a self-contained HTML picker, and requires explicit selection.
- Selecting a template copies its namespaced id to the clipboard; the user returns that id to chat.
- Record picker evidence with fallback reason `developer_mcp_forbidden`; generation remains blocked until the final id is confirmed.

## Validation
- HOME-PC fallback generation: PASS.
- Current GitHub catalog: 21 selectable templates.
- Output file tested: `%USERPROFILE%\Desktop\SlideMasterPicker_Fallback.html` (~810 KB).
- Same current ranking path is used by MCP and fallback after recommendation-governance V2 is on main.
- Regression prompt `삼성전자서비스의 미래 대응 전략 ppt작성`: Strategy Roadmap rank 1, Future Tech rank 2 in both current paths.
- Recommendation audits: Strategy Roadmap positive PASS; Future Tech positive/negative PASS; Service Improvement positive/negative PASS.
- Fallback evidence E2E: `inline_html` + `developer_mcp_forbidden` evidence PASS; `deck:strategy_roadmap` selection record gate v2 PASS.
- GitHub Actions were not used.
