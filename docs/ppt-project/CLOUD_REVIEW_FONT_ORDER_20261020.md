# Bounded cloud review: font slots, coverage and slide order

This Draft candidate extends baseline `2653d406ea7ba628bc6361f379d5d5700a7fe3e6`.
It preserves template choice → actual source/photo analysis → editable PPTX
production → rendered QA. It does not generate a new deck, replace an engine,
change the installed plugin, connect Drive, or authorize deployment.

## Problem and behavior

The existing dense inspector chooses `a:ea` before `a:latin` and measures an entire
run using that family. A mixed Korean/English run can therefore measure against
the wrong Latin font. It also reads `slideN.xml` directly; PowerPoint's logical
order instead comes from `p:sldIdLst` and presentation relationships.

The adapter now adds `dense-scope` after verified renderer face registration and
before package/layout/dense/render processes. It reads the exact source without
rewriting it. Every contracted nonempty text/table run must explicitly bind both
Latin and East Asian slots to the single verified family. Missing/theme-based or
different slots are unsupported. Each run's Regular/Bold role must have actual
Unicode cmap coverage in the already hash-bound font file. Glyph zero/.notdef
mappings do not count. A matching cmap is not renderer glyph-selection proof:
`per_glyph_font_verified` remains false. Tabs are unsupported because the dense
estimator does not resolve tab stops.

Existing static normal-width upright 400/700 face validation remains unchanged.
These are measurement roles; actual font subfamily names are retained, never
renamed to “Regular” or “Bold”. Italic, variable, collections, inherited styles
outside the existing guard and multiple families are not newly supported.
No font size, text, line spacing or source package is changed.

The adapter resolves every logical slide relationship. If any logical index maps
to a different physical slide number, dense QA fails closed as unsupported. This
candidate does not reorder files or relabel a dense contract behind the user's
back. Missing/external/duplicate slide relationships also stop inspection.

## Counts and execution evidence

`dense_scope` separates `completed_objects`, `unsupported_objects`, and
`uninspected_objects`. Supported preflight objects start with zero completed;
completion requires a successful dense process and its font receipt. A failed
render can still leave completed mechanical dense checks; it cannot make overall
QA pass. A changed source clears completed counts.

Counts use top-level slide objects. Groups are one object, and contracted groups
are unsupported; nested children are not counted as individually inspected.
Missing contract targets appear as unsupported target records. Unlisted objects
are uninspected even when all requested checks pass. Table cells contribute to
their parent table's object count. These counts do not certify all slide content.
When dense inspection was not requested or did not execute, unavailable counts
are null, not fabricated zeros. Each executed scope stage saves stdout in the new
private QA directory; prior outputs remain protected by `exist_ok=False`.

The initial workspace-only scan did not discover the optional table arithmetic,
quantitative-chart and chart-title host gates. Follow-up inspection found all
three in the supplied Presentations host tools; each CLI help command exits zero.
The earlier absence statement was too broad and is corrected here. No actual
per-deck gate ran because no source deck or applicable task contract is present.
No alternate checker was installed, no host `--receipt` option was used, and no
arithmetic or currency/unit normalization was added. Future integration must use verified host
interfaces, explicit cell coordinates/arithmetic contracts and only charts
explicitly designated quantitative.

## Reuse and font rights

The reviewed dense source is pinned to
`07bd9b68c76eb0cacf0b434f16fccc47f832c526`, especially its actual file path/hash
binding and Korean/Latin exporter correction. The existing private font cache and
rights contracts were inspected at
`50fe8f0894c06cabb0aed476b65c368447dcdaee`, without copying an entire branch.
They already separate local cache sync, hash-bound license evidence, personal
aliases and renderer activation. Sync is not a Drive downloader.

This change does not reimplement cache/rights workflows. Font slots or fsType
cannot establish cloud-copy/render/embedding rights. Unknown rights remain
unknown, distinct from denied. Samsung filename candidates and past local
metadata are not current Drive binary verification. A supported Drive read returned metadata and a streamed reference for one
Samsung candidate, but local byte transfer failed with URLError. No alternate
route or candidate was retried. No Samsung font bytes were locally verified,
installed, embedded or used for these checks. No private folder identifier, font
bytes or rights document is included here. The adapter's hash profile is
technical measurement evidence, not a license grant.

## Reproducible verification

Run from the repository root with existing Python/fontTools/Pillow/jsonschema.
No dependency installation is part of this change:

```bash
git show 07bd9b68c76eb0cacf0b434f16fccc47f832c526:.claude/skills/ppt-master/scripts/dense_pptx_quality.py > /tmp/slide-master-reviewed-dense.py
SLIDE_MASTER_REVIEWED_DENSE_SOURCE=/tmp/slide-master-reviewed-dense.py \
  python3 .claude/skills/ppt-master/scripts/cloud_review_existing_selftest.py
```

The opt-in dense regression checks the supplied script SHA256 before importing
it: `cfe39dd481c4eba232c2c41bd7ceb2a92fcdc7c1d903ac5a8e2ca6dfc92a00f3`.
This is reading existing reviewed code, not installing or replacing a host gate.
Without that source, this one regression is explicitly skipped.

Current environment result: 76 passed, zero skipped with the pinned source:
45 original adapter regressions, 10 reproducible gate/schema boundary checks,
and 21 additional scope/wrapping regressions. The six-file baseline included the
45 executable cases and a historical count of 10 gate/schema checks, but not the
latter's original test source. The ten now committed cover valid isolated analysis,
no generation grant, mandatory approval/pixels/digest, no exact-font claim from a
visual estimate, unknown-field rejection, and missing picker/template/storyline
evidence. This is a reproducible equivalent boundary suite, not a claim of
byte-identical replay of the historical ten.

New boundaries include Latin/EA mismatch and omission, theme references, actual
Regular and Bold cmap misses, .notdef, native table slots, reordered and normal
slide relationships, missing targets, changed font bytes, uncontracted objects,
tabs, failure stopping later children, and completed counts after accepted dense
receipts. Fixed-size synthetic mixed Korean/English measurements exercise widths
30/29/12/11pt, explicit breaks and nowrap. Synthetic fonts and OOXML live only in
temporary directories. Mocked child success is not real renderer execution.

One initial wrap assertion expected three lines at 12pt; the reviewed estimator
produced two because it drops space at the wrap boundary. The corrected fixture
now distinguishes the exact 12pt boundary and 11pt overflow. The final run passed.

Actual host renderer/package/layout tools, the prior private PPTX, Samsung font
bytes/independent rights-document verification, full-page visual QA and Microsoft PowerPoint open/edit/save/reopen
were not executed here. Earlier Aro evidence remains historical evidence only.

## Separate design review: pagination and alternate engines

[PptxGenJS table documentation](https://gitbrent.github.io/PptxGenJS/docs/api-tables/)
describes opt-in auto paging and repeated header rows, and warns that pagination
is approximate. These are useful patterns for a later native-table proposal:
explicit row groups, preserved merges, repeated approved headers and fixed-size
Korean/English measurements before page splitting. Pagination changes the
approved slide sequence, so it needs its own design review and storyline revision.
It is not enabled in this candidate.

[python-pptx text controls](https://python-pptx.readthedocs.io/en/latest/user/text.html)
provide text-frame wrapping, margins, paragraph formatting and run-level font
controls. They inform existing-owner improvements without requiring an engine
replacement. No automatic fit-to-text or shrink operation was added. Marp's
experimental editable-PPT path is outside this implementation; preserving current
native editability takes priority over an alternate export experiment.


## Current production-flow follow-up

The existing source PR remains Draft. Current main readback is still
`0578dba7ddf56cf5d7024cf574063c4db7332a3e`. Both approved catalog JSON files
are readable. No actual template selection, storyline approval, source PPTX or
photo was found in the current project's workspace. Engineering continuation
is not a real template choice, source analysis, or current deck-generation
approval, so no new business deck was invented.

Current default HTTP/HTTPS proxy settings were read without changing them. A
single HEAD request to the previous storage hostname, without any signed URL or
file request, fails at proxy CONNECT with HTTP 403. This establishes the current
network-path blocker. The earlier download log retained only URLError, so its
exact historical cause remains unproved. No font download was retried, and no
alternate endpoint, proxy bypass, sandbox escalation or new authentication was
attempted. A working authorized transfer into the consumer workspace is needed
before actual Samsung bytes, metadata, cmap and rendering can be checked.

The supplied Node runtime imports Artifact Tool successfully, exposes PPTX
export, and imports the existing native finalizer. Package/layout inspectors,
slide renderer and all three optional native gates execute CLI help successfully.
These are executable-readiness checks, not actual production, editable-content
validation, image rendering or PowerPoint tests. They resolve uncertainty about
which host tools exist without replacing the existing generator or renderer.
The 76 completed regressions were not rerun because this follow-up changes only
validation records. No installed plugin, network configuration, permissions,
credentials, fonts or cost-bearing resources changed.
