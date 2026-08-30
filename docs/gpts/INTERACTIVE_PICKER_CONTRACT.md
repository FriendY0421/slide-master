# Interactive Picker Execution Contract

## Recommendation flow
1. Build latest catalog/shortlist.
2. Render App Block/GenUI picker.
3. Record visible render with `picker_surface_gate.py`.
4. Show real detail previews.
5. Obtain explicit user final id.
6. Record with `record_template_choice_v2.py --picker-evidence`.
7. Initialize with `new_deck_init.py`.

## Direct-template flow
When the user names a valid registered template before recommendation:
1. Resolve exact template.
2. Lock it.
3. Record with `record_template_choice_v2.py --direct-template --confirmed`.
4. Continue generation.

## Why this exists
The previous system had contradictory authority: some files prioritized the stable GitHub gallery while other files prioritized inline interactive HTML. That allowed GPTS to fall back to text even when an interactive conversation surface was desired. The current authority makes conversation-native App Block/GenUI first and adds picker evidence to the local gate.

## Evidence examples
Primary:
`picker_surface_gate.py record picker.json --surface app_block --purpose "천안센터 문제점" --source-ref "github:main" --candidate-count 6 --detail-preview-max 6 --rendered`

Fallback:
`picker_surface_gate.py record picker.json --surface inline_html --purpose "천안센터 문제점" --source-ref "github:main" --candidate-count 6 --detail-preview-max 6 --fallback-reason "developer_mcp_forbidden" --rendered`
## Host rejection policy
- An actual tool error containing `FORBIDDEN` / `does not support developer MCPs` is authoritative evidence that the current conversation surface cannot run the developer MCP app.
- Do not re-diagnose that exact condition as CSP, preview-image, GitHub catalog, port 3000, or Tunnel failure unless separate runtime checks show a new fault.
- If Remote Desktop Commander is available, execute `ops/windows/Open_SlideMasterPicker_Fallback.bat <purpose>` and open the self-contained HTML picker automatically.
- The fallback still uses the live GitHub catalog and explicit user selection; it never authorizes skipping the template-selection gate.
- Selecting a card copies its namespaced template id to the clipboard. Record the returned id with fallback picker evidence before PPT generation.
