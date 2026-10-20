# Samsung font verification in the fresh cloud environment

The exact PR baseline `05fee47cc454317e9b79182f516bb7ea009adfb0` was
restored from GitHub before execution. No running build/render process was
present. The user assigned the latest approved 44-host environment; its effective
policy revision and host list are not exposed. No network configuration changed.

Both authorized Samsung files were downloaded through references returned by
the official Drive connector and verified locally: 4,002,384 and 4,063,000 bytes,
with the exact requested SHA256 values. No guessed download endpoint, credential
read, laptop or external disk was used. Font binaries remain in the ignored
private task directory and are excluded from commits and delivery archives.

## Numeric weight faces

The real Samsung 700 file declares OS/2 weight 700 and subfamily `700`, but
uses mutually consistent legacy Regular flags. Skia registers that exact file
as normal-width upright weight 700. The old adapter rejected it before rendering.

The adapter now recognizes a narrow numeric-weight declaration: an exact numeric
subfamily matching supported static OS/2 weight, both legacy bold flags unset,
and the Regular flag set. Other contradictory flags and mismatched names remain
blocked. Font bytes are never modified. Existing hash binding, actual per-file
Skia face mapping, Latin/East Asian slots and cmap checks remain required.
The new synthetic regression accepts this case and rejects five near misses.

## Fresh actual specimen

Historical private builder/deck artifacts were unavailable in this workspace.
This run does **not** claim to replay them. A new isolated synthetic specimen
uses the existing supplied Artifact Tool/native finalizer, the registered
Consulting Clarity visual reference and balanced_report fixture context. It
adapts the reference's spacing/color language for QA; native Master/Layout
fidelity and an interactive production-picker callback are not claimed.

The original contains native bilingual text, a native table and a native chart
with an intentionally new literal-data workbook snapshot. Original data 12/18
sum to 30. Its actual builder/data hashes were retained **before** regenerating
the separate 13/18/31 candidate. The retained-source manifest verifies, source
bytes remain unchanged, and all seven actual cloud QA stages pass:
preservation, font-map, dense-scope, package, layout, dense and render.

Six targeted text/table objects pass actual-font measurement; two objects
(decoration and chart) remain outside dense scope. The finalizer separately
passes native table arithmetic, chart-title and quantitative chart/workbook
checks. Full-page inspection of the actual final PPTX render confirms Korean
and English, visibly distinct 400/700 weights, the explicit two-line break,
unclipped text, table total 31 and chart bars 13/18. Fourteen design warnings
are retained: explicit line-spacing is absent and the checker uses actual font
metrics. These are not hidden or converted into exact PowerPoint-layout proof.

The new candidate SHA256 is
`35f1276e9c5387577452c0d3f3750daca3e6b75307a72cdaf6d1c50dfb0daf17`.
Its inspected PNG SHA256 is
`af68a3a47a81eba98b4ddf5f2e141c2f45dd71b413f43265e4c0758ff8aece3f`.
No font binaries are embedded in the PPTX.

Actual import/edit/export again drops the source embedded workbook. The existing
guard blocks this failed draft at stage one, even with a valid retained-source
manifest; no later QA or render executes. Regeneration without the manifest is
also blocked at stage one. Failed drafts remain local and are not delivered.
The external engine defect remains unresolved.

Initial incorrect invocation/contract attempts are preserved separately: missing
table label-column declaration, an inapplicable original-workbook requirement
for a newly authored chart, and missing dense table point requirements. Each was
corrected in the owning fixture/QA contract; no failed renderer was bypassed.
Only one final candidate render was executed.

## Checks and limits

Fresh results: 20 preservation regressions, eight focused adapter checks, and
81 complete adapter/schema cases pass with zero failures/skips. The focused
eight are a subset, not additional cases to add to 81. The pinned existing dense
source was restored from its documented GitHub commit and its hash verified by
the existing regression. Compile and diff checks pass.

OfficeCLI is absent, so its independent workflow was not run or replaced with
a claim of OfficeCLI verification. Native PowerPoint open/edit/save/reopen,
per-glyph renderer selection tracing, company-deck fidelity and an actual user
picker/delivery callback remain unverified. No main merge, installed plugin or
runtime change, new keys/cost/permissions, or SI repository execution occurred.

Sanitized machine evidence: [samsung-cloud-20261020.json](evidence/samsung-cloud-20261020.json).
Private PPTX, PNG and source/validation handoff remain in the ignored task
workspace. The current official Library helper failed at hosted-app tool
discovery with HTTP 403, before upload preparation. No file IDs were issued;
no direct upload fallback or retry was attempted. Library persistence requires
the platform to restore the existing authorized helper access. Public commits
contain neither the private outputs nor company assets.
