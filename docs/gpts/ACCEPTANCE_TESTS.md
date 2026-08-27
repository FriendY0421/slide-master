# GPTS Interactive Picker Acceptance Tests

## A. Normal request
Input: `삼성전자서비스 천안센터 문제점 PPT`
Expected:
- no PPT generation;
- no prose-only template recommendation first when App Block/GenUI is available;
- interactive picker shows 5–10 real registered candidates;
- detail navigation shows up to 6 real layouts/examples;
- final id is explicitly confirmed;
- picker evidence + template selection evidence exist before generation.

## B. Direct template
Input: `McKinsey Strategy로 천안센터 문제점 PPT`
Expected:
- exact registered template is resolved and locked;
- recommendation picker is skipped;
- `--direct-template` evidence path is used.

## C. Fallback
Simulate no App Block/GenUI.
Expected: next visual surface is used, fallback reason is recorded, and text is only the last resort.

## D. Invalid evidence
Call `record_template_choice_v2.py ... --confirmed` without `--picker-evidence` and without `--direct-template`.
Expected: exit non-zero.

## E. Company template
After a new company template becomes ACTIVE, repeat a relevant PPT request.
Expected: it is automatically evaluated as a recommendation candidate without GPTS instruction edits.