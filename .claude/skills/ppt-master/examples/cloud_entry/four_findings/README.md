# Independent review counterexamples and fixes

[Regression evidence](regression-summary.json) covers the two P1 and two P2
findings reported against `13f6eabc19ae88a37af4d0bdb836d453dd3310fe`.
All inputs and approval/picker records are explicitly synthetic. No actual
company request, displayed picker or personal-font activation is asserted.

The previous HEAD reproduced all four failures (five observations, because the
font failure also reached project initialization). The changed code passed 38
positive/rejection checks using existing CLI/library calls in the gitignored
`projects/_smoke_four_findings` workspace, without a new test framework.

- Original PPTX exported as the result was accepted by the old strict readback.
  Now every requested paragraph/run is read from the exact output slide/slot or
  table cell and compared, including whitespace and run boundaries. A whole-deck
  substring in another shape cannot satisfy the target. The receipt names the
  exact final artifact SHA256. Apply also verifies requested runs before masking
  editable text for format comparison.
- A new missing `font_policy.values.body` was hidden by stale `font_requests`.
  Effective policy families now participate in actual face/metadata/hash/license
  checks. Init freshly verifies them and binds the requirement fingerprint,
  verified face/style/version/hash and current brief SHA256. Old success objects
  do not grant readiness.
- Picker evidence from another SHA/candidate/final pair created a new selection.
  New evidence v2 binds the displayed manifest hash, pinned source SHA, displayed
  candidate keys and explicitly confirmed template/preset; the record writer and
  downstream project gate both check it. Legacy unbound evidence cannot produce
  a new recommendation; original unpinned resume records remain compatible.
- A six-slide plan with its own `requested_slide_count=6` ignored a separate
  one-slide task request. Current native apply/validate read the separate current
  confirmed custom brief, compare plan and actual output counts, and reject a
  self-reported count without that external brief. At that historical review HEAD, approved brief SHA was optional and v1
  no-count resume was accepted. The later
  [required count-binding follow-up](../count_binding_required/README.md) removes
  that omission fallback; current creation and resume require all bindings.

The normal six-slide native result regenerated with identical ZIP-part bytes to
[the prior reviewed result](../../template_fidelity/review/filled.pptx).
Shared Presentations finalization passed with two native charts/workbooks and two
native tables. Six final rendered pages were inspected individually and all were
pixel-identical to the prior reviewed renders, with the same two bundled OFL
Pretendard fonts. The finalization and exact font/PPTX/PNG hashes are in the
regression evidence. No new public duplicate PPTX is needed.
The existing two-page [Korean fit fixture](../korean_fit/README.md) and all source
sample/font assets remain unchanged. Its 26 glyph/native/pixel checks also pass.

The related 29 entry and 72 intake/font regressions pass. For the latter, the
synthetic init input now supplies actual licensed fonts: it must not demonstrate
successful initialization from an unverified-font brief. Runtime contracts,
generated stubs, compile and diff checks pass.

Actual photos/company inputs/private fonts, OfficeCLI/PowerPoint, host picker
visibility/state, private delivery and cross-PC use remain unverified. Keep PR
#10 Draft; no main integration or automatic user execution is activated here.
