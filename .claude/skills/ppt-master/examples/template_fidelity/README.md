# Native template fidelity, synthetic review fixture

This is a feature-verification fixture, **not a recommended company design**.
All facts, wording, owners and dates are synthetic. No user company file exists
in this repository. The existing six-page fixture was reused as native input,
with a two-run title (33pt bold + 24pt regular) and native source speaker notes.
Only that title and one table owner cell were authorized for replacement.

- [Original native fixture](sources/template-source.pptx)
- [Filled native result](review/filled.pptx)
- [Title before](review/source-01.png) / [after](review/filled-01.png)
- [Table before](review/source-05.png) / [after](review/filled-05.png)
- [Validation evidence and hashes](review/validation-summary.json)
- [Task brief](design_brief.json) / [fill plan](fill_plan.json)
- [Workflow and limits](../../../../../docs/ppt-project/TEMPLATE_FIRST_WORKFLOW.md)

## Reproduce in the cloud or another repo root

Run from your checkout's repo root, retaining the repository folder structure.
No `/workspace`, machine username, drive letter or global company defaults are
encoded in this recipe. Use the existing prepared runtime and dependencies.

```bash
python3 .claude/skills/ppt-master/scripts/presentation_brief.py \
  .claude/skills/ppt-master/examples/template_fidelity/design_brief.json --check-environment
python3 .claude/skills/ppt-master/scripts/template_fill_pptx.py analyze \
  .claude/skills/ppt-master/examples/template_fidelity/sources/template-source.pptx \
  -o projects/native_review/analysis/source.slide_library.json
python3 .claude/skills/ppt-master/scripts/template_fill_pptx.py check-plan \
  projects/native_review/analysis/source.slide_library.json \
  .claude/skills/ppt-master/examples/template_fidelity/fill_plan.json
python3 .claude/skills/ppt-master/scripts/template_fill_pptx.py apply \
  .claude/skills/ppt-master/examples/template_fidelity/sources/template-source.pptx \
  .claude/skills/ppt-master/examples/template_fidelity/fill_plan.json \
  -o projects/native_review/exports/filled.pptx --transition keep
```

The plan confirmation is explicitly the user-authorized **synthetic engineering
fixture**, never a reusable approval for company documents. For real material,
confirm the actual task brief and slide mapping afresh. `check-plan` warns that
two source charts and one untouched table retain original content; preserving
them is intentional here. No source chart data is changed.

Eighteen real-fixture checks passed, including stale source, locked targets,
run topology, explicit transitions, style mutation, notes retention, legacy fill,
two-mode intake, runtime/font preparation and different-root execution. A fresh
Linux root with the canonical repo folder structure produced identical ZIP part
bytes. A flattened scripts-only copy lacks the repo-relative helper context and
is not a supported distribution. Other operating systems were not tested.

The shared Presentations finalizer validated the six-slide output and both charts'
embedded workbook data; its output preserves the candidate bytes. The supplied
runtime rendered all six source and six result pages with registered bundled
Pretendard Regular/Bold. All twelve were individually inspected. Slides 2/3/4/6
are pixel-identical; slide 1 retains mixed sizes and style, slide 5 retains table
geometry. There was no observed Korean tofu, overflow or unintended overlap.
No new packages, login, API provider or server were introduced.

**Acceptance limits:** fonts are not embedded; source font availability must be
checked on each execution machine. OfficeCLI/PowerPoint opening, Edit Data and
native application line wrapping remain unverified. Inherited font properties
are reported as inherited, not guessed. Strict v1 leaves charts unchanged and
rejects unsupported changes; it does not assert exact rendering for arbitrary
company files. Real logo/image/theme variants require the actual private source.
