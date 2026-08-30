# Interactive Picker Execution Contract

## Recommendation flow
1. Build latest catalog/shortlist.
2. Render the best available template picker and record visible render evidence.
3. Show real template detail previews and obtain explicit template id.
4. Render 3-5 purpose-ranked production presets and obtain explicit preset id.
5. Record the locked pair with `record_template_choice_v2.py --preset <preset_id> --picker-evidence ... --confirmed`.
6. Research/verify current evidence.
7. Present the slide-by-slide storyline/content outline and wait for explicit approval.
8. Initialize with `new_deck_init.py` and generate only after approval.
9. QA, then deliver.

## Mandatory two-stage selection
1. Stage 1 is template selection: user explicitly returns `deck:<id>`, `layout:<id>`, or `free`.
2. Stage 2 is production-preset selection: show 3-5 relevant presets and require an explicit preset id.
3. Lock the template and preset together; neither may be silently changed later.
4. Record both in `template_selection.json` using gate v3.
5. Research begins only after this lock.
6. After research, present a slide-by-slide storyline/content outline and wait for explicit approval before generation.
7. On developer-MCP `FORBIDDEN`, use `Open_SlideMasterPicker_Fallback.bat` followed by `Open_SlideMasterPreset_Fallback.bat`; fallback changes only the UI surface, not the stage order.

## Direct-template flow
When the user names a valid registered template before recommendation:
1. Resolve and lock the exact template id.
2. Skip only the template picker; still show/require a production preset unless already supplied.
3. Record the pair with `record_template_choice_v2.py --preset <preset_id> --direct-template --confirmed`.
4. Research, present the storyline/content outline, and wait for explicit approval.
5. Generate only after approval, then QA and deliver.

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
- Selecting a card copies its namespaced template id to the clipboard. Then open `Open_SlideMasterPreset_Fallback.bat`, return the preset id, and record the template+preset pair with fallback picker evidence before research.
