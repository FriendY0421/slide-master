# Standard PPT workflow - 2026-08-30

## Decision
The user approved the staged PPT workflow used for a future-strategy deck and requested that it become the default for future PPT work.

## Canonical order
1. Understand request/purpose/audience.
2. Show live template picker; require explicit template id.
3. Show purpose-ranked production preset picker; require explicit preset id.
4. Lock template + preset; never silently substitute either.
5. Research/verify current evidence only after the lock.
6. Present slide-by-slide storyline/content outline.
7. Wait for explicit user approval/revision.
8. Generate using the locked template/preset.
9. Run QA including content logic, source/date accuracy, layout fidelity, clipping/overlap, and render sanity.
10. Deliver PPTX only after QA passes.

## Surface independence
If Developer MCP is supported, use the Apps picker. If it returns `FORBIDDEN`, switch to Desktop Commander self-contained template HTML followed by the production-preset HTML. The UI surface may change; stage order may not.

## Enforcement
- `docs/ppt-project/state_machine.json` schema v2 models the stages.
- `record_template_choice_v2.py` / `template_gate.py` gate v3 require the production preset for new selections while retaining legacy v1/v2 validation.
- Canonical GPTS, request guard, project instructions, AGENTS, AI_CONTEXT, acceptance tests, and handoff are aligned.

GitHub Actions were not used.
