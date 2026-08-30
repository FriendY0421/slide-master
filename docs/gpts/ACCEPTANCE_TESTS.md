# GPTS Interactive Picker Acceptance Tests

## A. Normal request
Input: `삼성전자서비스 천안센터 문제점 PPT`
Expected:
- no PPT generation;
- no prose-only template recommendation first when App Block/GenUI is available;
- interactive picker shows 5–10 real registered candidates;
- detail navigation shows up to 6 real layouts/examples;
- template id is explicitly confirmed;
- a production preset is shown next and its id is explicitly confirmed;
- gate-v3 picker evidence + template+preset selection evidence exist before research;
- the post-research storyline is explicitly approved before generation.

## B. Direct template
Input: `McKinsey Strategy로 천안센터 문제점 PPT`
Expected:
- exact registered template is resolved and locked;
- recommendation picker is skipped;
- production preset selection still occurs unless already specified;
- `--direct-template --preset <preset_id>` evidence path is used;
- research/storyline approval still precede generation.

## C. Fallback
Simulate no App Block/GenUI.
Expected: next visual surface is used, fallback reason is recorded, and text is only the last resort.

## D. Invalid evidence
Call `record_template_choice_v2.py ... --confirmed` without `--preset`, or without `--picker-evidence` / `--direct-template`.
Expected: exit non-zero.

## E. Company template
After a new company template becomes ACTIVE, repeat a relevant PPT request.
Expected: it is automatically evaluated as a recommendation candidate without GPTS instruction edits.

## Company template lifecycle
- A newly registered CANDIDATE template must not appear in normal picker/recommendation inventory.
- After the same template becomes ACTIVE, it must appear automatically on the next live catalog/picker request.
- DEPRECATED and DISABLED templates must remain excluded from normal recommendations.
- A user-explicit valid registered template may bypass recommendation, subject to direct-template validation.
- PPTX/POTX imports are master-extraction candidates; PDF/image/photo imports must be labeled reference reconstruction.
- Confidential company source assets must not be committed to the public repository.

## G. Recommendation-fit quality gate
For an imported company template promoted to ACTIVE:
- registration fails if required recommendation metadata is missing;
- organization/brand terms influence ranking only when the request actually matches them;
- `purpose`, `audience`, `aliases`, `document_types`, `tone`, and `keywords` contribute contextual fit;
- `quality_score` is a tie-breaker, not a reason to recommend an unrelated template;
- `avoid_for` can suppress a clearly unsuitable template;
- Deck format alone must not create a positive recommendation score;
- `template_recommendation_audit.py` must pass representative positive-fit prompts;
- when a negative-fit prompt is supplied, the template must not receive the recommendation badge.

## H. Standard PPT workflow gate
Input: a new future-strategy PPT request.
Expected:
- template picker is shown first and an explicit template id is required;
- production preset picker follows and an explicit preset id is required;
- gate-v3 selection evidence stores both template and preset;
- research starts only after the pair is locked;
- a slide-by-slide storyline/content outline is presented after research;
- generation/export does not start until the user explicitly approves that outline;
- template or preset is never silently changed after lock;
- QA runs before PPTX delivery.

Fallback regression:
- developer-MCP `FORBIDDEN` automatically switches to template HTML then preset HTML;
- the same stage order and gate-v3 evidence still apply.
