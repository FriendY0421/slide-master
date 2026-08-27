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
- picker evidence + template selection evidence exist before generation.

## B. MCP Apps protocol
Expected:
- `/mcp` is Streamable HTTP and stateless-safe;
- tool list contains `open_slide_master_template_picker`;
- tool is annotated read-only/non-destructive;
- tool result has lightweight `structuredContent` plus full UI payload in `_meta.pickerPayload`;
- `ui://slide-master/template-picker-v1.html` resolves with MIME `text/html;profile=mcp-app`;
- ChatGPT UI can receive the result and render real previews.

## C. Direct template
Input: `McKinsey Strategy로 천안센터 문제점 PPT`
Expected:
- exact registered template is resolved and locked;
- recommendation picker is skipped;
- `--direct-template` evidence path is used.

## D. Fallback
Simulate unavailable Slide Master Picker app/App Block.
Expected: next visual surface is used, fallback reason is recorded, and text is only the last resort.

## E. Invalid evidence
Call `record_template_choice_v2.py ... --confirmed` without `--picker-evidence` and without `--direct-template`.
Expected: exit non-zero.

## F. Company template lifecycle
- A newly registered CANDIDATE template must not appear in normal picker/recommendation inventory.
- After the same template becomes ACTIVE, it must appear automatically on the next live catalog/picker request.
- DEPRECATED and DISABLED templates remain excluded from normal recommendations.
- A user-explicit valid registered template may bypass recommendation, subject to direct-template validation.
- PPTX/POTX imports are master-extraction candidates; PDF/image/photo imports must be labeled reference reconstruction.
- Confidential company source assets must not be committed to the public repository.
