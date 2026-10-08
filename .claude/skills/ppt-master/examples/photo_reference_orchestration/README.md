# Synthetic photo reconstruction connection fixture

Every image, instruction reference, figure and replacement sentence in this directory is **SYNTHETIC**. These files contain no company data or actual user approvals. The two simulated photographs include a white 16:9 screen within a 1280×800 picture, two editable navy section bars, Korean text, a tiny supplied crop and an explicitly omitted decorative dot. Page 2 keeps the observed `/ /` separately from the synthetic approved replacement.

The host model first views every original, records the screen region/text and writes the full finite layout in `plan.json`. `photo_reconstruct.py` validates that plan, emits complete SVG prototypes, calls the existing **structured** `template_preview_pptx.py`, reads back native objects/text/point sizes, runs the shared Presentations finalizer and renders every final page through the supported runtime. No OCR/model/API or new PPTX engine is installed or called.

The explicit `review_only:true` branch records model-estimated coordinates/font/decoration with review references rather than inventing individual user approvals. The actual reference-purpose choice still needs the current user instruction. Model-written hypothetical content uses `user_authorized_synthetic/model_written` with the actual request reference and a visible disclosure. See the input documentation for that branch; no exact-source identity or user-delivery readiness is certified.

```bash
"$CODEX_PRIMARY_RUNTIME_PYTHON" .claude/skills/ppt-master/scripts/photo_reconstruct.py .claude/skills/ppt-master/examples/photo_reference_orchestration/plan.json --check
"$CODEX_PRIMARY_RUNTIME_PYTHON" .claude/skills/ppt-master/scripts/photo_reconstruct.py .claude/skills/ppt-master/examples/photo_reference_orchestration/plan.json --workspace-parent projects/private --presentations-skill-dir <verified-shared-Presentations-skill>
```

Read the verified shared Presentations skill before the build command. All supplied runtime variables must be present. Each build needs a fresh `project_name`; outputs are collision-protected, private and unregistered. `--check` creates no workspace or presentation. Confirmation references in real plans come from the host's actual current instruction/approval events; the adapter cannot authenticate those events by itself.

The JSON Schema is `../../schemas/photo_reconstruction_plan.v1.json`. The production input/limits and parent-model provenance path are documented in `docs/ppt-project/PHOTO_MODEL_ORCHESTRATION.md`. Formal shape validation supplements the runtime checks for source hashes, finite bounds, observation correspondence, licensed glyph fit and unsupported properties.

See the separate [public validation summary](../../../../../docs/ppt-project/PHOTO_REVIEW_VALIDATION.md). Per-run receipts and private output locations are not published. It does not relabel the earlier 65 intake checks, any earlier one-page experiment, a parent's separate Artifact Tool deck or an actual company photo as this compiler's reconstruction success. The final review receipt remains `user_delivery_ready:false` until the host compares every final image with the actual source and handles disclosed differences.
