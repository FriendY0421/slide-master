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
`picker_surface_gate.py record picker.json --surface inline_html --purpose "천안센터 문제점" --source-ref "github:main" --candidate-count 6 --detail-preview-max 6 --fallback-reason "host_app_block_unavailable" --rendered`