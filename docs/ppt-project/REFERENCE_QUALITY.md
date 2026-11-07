# Reference preservation and repair tracking

This opt-in layer extends the existing `dense_pptx_quality.py` and
`verify_deck.py` route. It does not replace the converter, auto-edit source,
resize fonts, install OCR, change template selection or authorize generation.
No external package is required beyond the existing inspector's dependencies.

## Declare the actual preservation scope

Keep an immutable original/recovery copy. Add this block to the task's existing
`dense_layout_contract.json`, alongside its font/geometry/slide requirements:

```json
{
  "reference_comparison": {
    "path": "original.pptx",
    "sha256": "<actual 64-character lowercase SHA256 of original.pptx>",
    "preserve_text": true,
    "protected_objects": [
      {"slide": 1, "name": "right-panel"}
    ],
    "protected_parts": ["ppt/theme/theme1.xml"],
    "require_complete_text_coverage": false
  }
}
```

Paths resolve relative to the contract. Use real native names; a grouped child
uses `group-name/child-name`. Names must be unique within their parent and form
unambiguous paths. No fuzzy matching or invented object IDs are used. Pin actual
source bytes; a missing/wrong hash or empty preservation scope fails closed.
The example names/hash are placeholders, not evidence or production defaults.

`preserve_text` compares each shape/paragraph and every native table cell,
including children of groups, fields and explicit line breaks. It also compares
table row/column topology and merge flags/spans. It does not normalize away
numbers, units, punctuation or whitespace. User-approved rewriting needs an
appropriately scoped contract; do not disable preservation silently to pass.
Object renaming/regrouping can require an explicitly reviewed new comparison
scope, even if the resulting slide looks similar.

Protected objects compare canonical local XML, ancestor group transforms,
sibling order, slide-level context and inherited layout/master/theme. Referenced
images, charts, workbooks and other dependency bytes/relationship edges are
compared too: unchanged relationship IDs alone do not prove unchanged content.
External protected relationships are unverified errors. Protected package parts
are exact bytes plus their reachable dependencies. Such strict protection can
reject harmless serialization or structural changes; review these differences
rather than silently treating them as an unchanged company original.

## Run through the existing production verifier

```sh
python .claude/skills/ppt-master/scripts/dense_pptx_quality.py output.pptx --contract dense_layout_contract.json --output dense_quality_report.json
python .claude/skills/ppt-master/scripts/verify_deck.py projects/<actual-project>
```

`verify_deck.py` already invokes the inspector on the latest native export when
this contract exists. Reference errors therefore fail that existing gate.
There is no separate engine, server or approval bypass. Without the opt-in block,
the inspector's existing report and checks are unchanged.

The report adds:

- `reference_comparison`: per-target checks and reference/candidate hashes;
  inventory counts for native tables/cells/groups/pictures/shapes; unverified
  graphic frames. It emits identifiers/status, not original wording.
- `repair_tracking`: the pinned reference is measured again by the existing
  inspector with the same mechanical contract/font inputs. Finding counts are
  marked resolved, remaining, new or unverified. Missing/unreadable targets are
  not called repaired merely because their former height error disappeared.
- `reference_status`: pass, fail or partial in CLI output. Partial is explicitly
  propagated as a warning by `verify_deck.py`; `--strict` rejects warnings.
  `require_complete_text_coverage: true` rejects unsupported text/data coverage
  directly, even when the checked XML/bytes are unchanged.

Repair tracking certifies mechanical findings only, not that an edit looks
better. Baseline and output hashes tie the evidence to actual bytes. Do not use
an old JSON result as proof of a new output or count missing metrics as 100%.

## Boundaries

The inventory covers native slide DrawingML. Charts/SmartArt/other graphic
frames need dedicated data/text/render checks and remain listed as unverified
by this layer. Their explicitly protected parts can still be byte-identical;
that does not certify native chart editing, data correctness or font appearance.
Notes, macros and application-specific behavior are not certified here.

Font metrics, structural checks, final-file reimport/render, model visual review,
and actual PowerPoint editing/save/reopen are separate evidence. Keep requested
fonts and approved slide count. For the current company task, retain 14/12/11/9pt
and table maximum 12pt, but do not impose these defaults on other templates.
Samsung usage rights and actual rendering remain subject to their existing gates.

See [November comparison and project order](QUALITY_ROADMAP_20261107.md).
