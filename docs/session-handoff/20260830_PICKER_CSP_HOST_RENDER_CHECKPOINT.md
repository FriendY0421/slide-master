# 2026-08-30 — Slide Master Picker CSP / Host Render Checkpoint

## Current result
Local MCP + Secure Tunnel regression is PASS after host-render hardening. PR #6 must remain Draft until real ChatGPT visible-UI acceptance passes.

## Fixed
- explicit CSP for embedded `data:` SVG previews;
- Apps SDK + ChatGPT compatibility UI metadata;
- false success distinction: payload prepared vs host UI rendered;
- `SLIDE_MASTER_PICKER_UI_RENDERED` emitted only by the rendered app view;
- app-only validation result no longer destroys picker UI;
- 8-second fail-closed host-payload error;
- stale port-3000 process identified as cause of misleading old validation behavior;
- smoke test now validates the actual recommended template/preset instead of a hard-coded pair.

## Current local evidence
`npm run smoke` => 21 ACTIVE / 6 shortlist / `layout:future_tech` first / 5 presets / UI resource loaded / CSP `data:` / final token `layout:future_tech | preset:executive_brief` PASS.
Tunnel `/healthz=live`, `/readyz=ready`. GitHub Actions were not used.

## Do not repeat old debugging first
On recurrence, use this order:

`port 3000 process/version -> npm run smoke -> tunnel 8080 health/ready -> MCP tool/resource metadata -> host UI render signal -> final app selection`

Do not start by blaming GitHub preview images: previews are embedded `data:` SVGs. Do not say the picker is visible from tool success alone.

## Remaining host acceptance
In an eligible normal ChatGPT chat run:
`@Slide Master Template Picker 삼성전자서비스의 미래 대응 전략 ppt작성`

Pass only if cards and preview images visibly render, `Future Tech` is appropriately recommended, detail/preset interactions work, and final confirmation sends the selection token back into chat. Only then move PR #6 out of Draft and consider merge.

Durable detailed history: `docs/ai-history/2026-08-30-picker-csp-host-render-hardening.md`.
