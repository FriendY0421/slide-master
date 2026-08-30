# 2026-08-30 — Picker Storyline Handoff Fail-Closed

## Trigger
A real 20-slide Samsung future-strategy test selected a template and preset correctly but then generated the PPT immediately. The required user-editable slide-by-slide preview did not appear.

## Root cause
The Apps SDK Picker still contained legacy final-action wording:
- final button meaning: “create PPT with this configuration”;
- `app.sendMessage()` meaning: confirm selection and continue PPT production.

That host bridge contradicted the newer `main` workflow, where template+preset selection grants research permission only and explicit storyline approval grants generation permission.

## Fix
The Picker final-selection bridge now sends a hard next-state contract:
- `NEXT_STATE=WAIT_STORYLINE_PREVIEW`;
- `GENERATION_ALLOWED=false`;
- complete slide-by-slide preview required;
- per-slide fields: number, title, core message, key content, visual/layout plan;
- user may edit/delete/add/reorder/change slide count;
- generation/export remains forbidden until explicit approval of the current revision.
## Structured server contract
`validate_slide_master_selection` now returns `production_profile` and `workflow_contract`. The workflow contract explicitly sets `generation_allowed=false`, `storyline_preview_required=true`, user revision support, and explicit storyline approval requirement.

Production profile carries the preset's delivery purpose and body baseline. Current main authority recommends text 28px, balanced 34px, presentation 40px.

## UI changes
- final button: `선택 확정 → 장표안 미리보기`;
- model context records WAIT_STORYLINE_PREVIEW / generation blocked;
- host message instructs research/verification first, then the full editable slide plan;
- success UI explains that slide preview/edit/approval is the next step, not PPT generation.

## Validation
Isolated MCP server on TCP 3001 passed full smoke:
- tools/picker/UI/resource/CSP: PASS;
- selection validation: PASS;
- `WORKFLOW WAIT_STORYLINE_PREVIEW false true 34`;
- temporary 3001 server was stopped after the test.

The live foreground 3000/8080 processes were not terminated. The rebuilt UI resource can be served immediately; the richer structured server contract becomes active on the next normal Picker server restart.

GitHub Actions were not used. PR #6 remains Draft pending real host E2E acceptance.
