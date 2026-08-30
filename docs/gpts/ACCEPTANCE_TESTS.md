# GPTS Interactive Picker Acceptance Tests

## A. Normal request
Input: `삼성전자서비스 천안센터 문제점 PPT`
Expected:
- no PPT generation;
- if `open_slide_master_template_picker` is connected, it is called before prose recommendations;
- interactive picker shows 5–10 real registered candidates (default 6);
- detail navigation shows up to 6 real layouts/examples;
- production presets are selectable in the same app;
- final app button sends `deck:<id> | preset:<id>` into chat;
- picker evidence + template selection evidence exist before generation;
- `template_selection.json.production_preset.id` matches the user's selected preset.

## B. MCP Apps protocol
Expected:
- `/mcp` is Streamable HTTP and stateless-safe;
- tool list contains `open_slide_master_template_picker`;
- tool is annotated read-only/non-destructive;
- tool result has lightweight `structuredContent` plus full UI payload in `_meta.pickerPayload`;
- `ui://slide-master/template-picker-v1.html` resolves with MIME `text/html;profile=mcp-app`;
- ChatGPT UI can receive the result and render real previews;
- final UI interaction can update model context and send a user message back to chat.

## C. Direct template
Input: `McKinsey Strategy로 천안센터 문제점 PPT`
Expected:
- exact registered template is resolved and locked;
- recommendation picker is skipped;
- `--direct-template` evidence path is used;
- an explicitly supplied valid `--preset` is preserved.

## D. Fallback
Simulate unavailable Slide Master Picker app/App Block.
Expected: next visual surface is used, fallback reason is recorded, and text is only the last resort.

## E. Invalid evidence / preset
- `record_template_choice_v2.py ... --confirmed` without `--picker-evidence` and without `--direct-template` must exit non-zero.
- an unknown `--preset` id must exit non-zero.

## F. Company template lifecycle
- A newly registered CANDIDATE template must not appear in normal picker/recommendation inventory.
- After the same template becomes ACTIVE, it must appear automatically on the next live catalog/picker request.
- DEPRECATED and DISABLED templates remain excluded from normal recommendations.
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

## H. Host-render truthfulness / CSP regression
For the MCP Apps picker:
- a successful `open_slide_master_template_picker` call proves payload preparation only;
- `payload_ready=true` must not be interpreted as visible UI;
- server-stage `host_ui_rendered` remains false until the app view actually renders;
- the model must not say the gallery/images are visible until the view reports `SLIDE_MASTER_PICKER_UI_RENDERED`;
- the UI resource must expose explicit CSP compatible with embedded `data:` SVG previews;
- app-only validation tool results without `pickerPayload` must not clear or replace the rendered picker;
- missing host payload delivery must fail closed with a visible UI error rather than silently hanging;
- after server/UI edits, the port-3000 process must be restarted before smoke testing to prevent stale-build false results.

Current regression command: `cd apps/slide-master-picker && npm run smoke`.
Expected current smoke for `삼성전자서비스 미래 대응 전략`: 21 ACTIVE, 6 shortlist, `layout:future_tech` first, 5 presets, CSP resource domain `data:`, final selection validation PASS.
