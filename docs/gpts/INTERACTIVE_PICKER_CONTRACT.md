# Interactive Picker Execution Contract

## Primary recommendation flow
1. Refresh the latest GitHub Slide Master catalog.
2. If the connected `Slide Master Template Picker` app exposes `open_slide_master_template_picker`, call it **before any prose template recommendations**.
3. The tool renders the conversation-native MCP Apps picker with 5–10 relevant real templates (default 6), full ACTIVE catalog access, real previews, detail layouts, Free Design, and production presets.
4. Card selection is tentative; show up to 6 real registered detail previews from the exact workspace.
5. The final UI button sends `deck:<id> | preset:<id>` back into chat through the MCP Apps message bridge.
6. Treat that returned user message as explicit final selection; record picker-surface evidence and then `record_template_choice_v2.py --picker-evidence --confirmed`.
7. Initialize only through `new_deck_init.py`; only then research/generate/QA/export PPTX.

## Direct-template flow
When the user names a valid registered template before recommendation:
1. Resolve the exact template.
2. Lock it.
3. The picker app is not required.
4. Record with `record_template_choice_v2.py --direct-template --confirmed`.
5. Continue generation.

## Fallback flow
If `open_slide_master_template_picker` is genuinely unavailable or fails to render:
`other App Block/GenUI → native visual cards → inline HTML → GitHub visual gallery → external/local recovery → text last resort`

Every non-primary path requires a concrete recorded fallback reason. A fallback never authorizes generation before explicit user selection.

## Picker app implementation
- App path: `apps/slide-master-picker/`.
- MCP endpoint: `/mcp`.
- UI resource: `ui://slide-master/template-picker-v1.html`.
- UI MIME: `text/html;profile=mcp-app`.
- Picker data helper: `.claude/skills/ppt-master/scripts/template_picker_payload.py`.
- Tool: `open_slide_master_template_picker` (read-only).

## Why this exists
Earlier authority files disagreed about which selection surface was primary, so GPTS could return a prose list even when an interactive picker was desired. This contract makes the exact MCP Apps picker tool primary when connected and keeps the existing picker-evidence/template-selection gates fail-closed.
