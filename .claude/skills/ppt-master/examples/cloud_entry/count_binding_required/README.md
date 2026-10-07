# Mandatory native count and brief binding

[Evidence](regression-summary.json) reproduces the remaining P2 at
`72ca5817e93a788f10ae275c6d840337264651fd`: omitting brief, requested count and
brief SHA allowed native apply/readback to pass without resume evidence.

Current code removes both silent success branches. Creation **and resume** need:

- A separate complete, confirmed `workflow_version: 2` custom task brief,
  discovered at `analysis/design_brief.json` or passed with `--design-brief`.
- A confirmed fill plan with positive integer `requested_slide_count`, equal to
  the separate approved brief and plan/output counts.
- Mandatory `task_brief_sha256` equal to the exact approved brief bytes.

There is no implicit or separate legacy bypass. An existing task can resume only
with the same explicit confirmed bindings. Missing files/fields, stale brief,
unconfirmed inputs/plan, v1 no-count brief, self-assigned legacy/resume labels and
`--force` cannot skip approval binding. Resuming an actual task must use its real
approval evidence; synthetic confirmation is not permission for company inputs.

The 34 new negative/positive checks pass, including API and CLI apply/readback,
auto-discovered and explicit current brief paths. The prior 38 local regressions
also pass with complete approval bindings supplied for positive native samples.
All public example/source PPTX and font assets are preserved.

Normal six-slide generation has identical ZIP-part bytes to the prior reviewed
native result. Shared Presentations finalization passes with two charts, embedded
workbooks and tables; six registered-font renders were individually inspected and
are pixel-identical to the prior reviewed renders. Exact PPTX/font/PNG hashes and
finalizer checks are included in the evidence; duplicate public PPTX is omitted.

The parent reported 45 independent review checks. That executable suite was not
supplied or readable in this environment, so this evidence does not claim it was
rerun. The parent/reviewer should rerun it against the exact new review HEAD,
using confirmed brief/count/hash for intended positive native creation/resume.

Actual company files/photos/private fonts/PowerPoint and host delivery remain
unverified. Keep Draft; no main merge, plugin activation or operational change.
