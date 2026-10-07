# 2026-10-06 PR10 required-count follow-up

Only the residual native count P2 was changed against 72ca5817e93a788f10ae275c6d840337264651fd.
`task_contract.py` no longer treats absence as legacy/resume. Both creation and
resume require a separate complete confirmed v2 custom brief and a confirmed plan
bound by requested slide count and the exact brief SHA256. No separate legacy
bypass is introduced. Existing engine, template assets, font/selection/strict
readback fixes and public sample bytes are preserved. CLI documentation records
that `--force` cannot bypass the approval binding.

34 residual negative/positive checks and the prior 38 local regressions passed.
The positive native regression inputs explicitly bind their synthetic task approval;
this is intentional validation-contract tightening, not fabricated real approval.
The preceding historical evidence files are preserved. Parent-reported independent
45-check suite is unavailable here; no rerun is claimed. Re-review the new exact HEAD.

Normal six-slide regeneration preserves all reviewed ZIP parts. Shared runtime
finalization and six registered-font renders passed; every page was viewed, and
all six renders are pixel-identical to the earlier review. Exact binding evidence
is in examples/cloud_entry/count_binding_required/regression-summary.json.

Actual company/photo/private-font/PowerPoint acceptance boundaries remain.
PR #10 stays Draft; no merge, operating change, new dependency or plugin activation.
