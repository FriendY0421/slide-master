# Company / User Template Registration

## Goal
When a user supplies a company PPT/POTX/PDF/image/photo and asks to reuse it, convert it into a governed Slide Master template candidate rather than treating it as a one-off visual reference.

## Supported sources
- PPTX / POTX: extract real theme, master, layout, placeholder, color, font, footer and page geometry where possible.
- PDF: analyze visual rules and reconstruct a reusable template; do not claim an editable master was extracted.
- PNG/JPG/WebP/screenshot/photo: treat as reference-based reconstruction; only visible evidence is authoritative.

## Security classification
Before committing any source asset, classify it.
- Never place confidential company source files, customer/employee data, internal metrics, internal URLs, credentials, or restricted documents in public `FriendY0421/slide-master`.
- Prefer a private companion repository for confidential originals.
- A sanitized derived template may enter the public repository only when the source-sensitive content has been removed and the user approves public reuse.
- Keep source material and derived design assets logically separate.

## Extraction targets
Extract or reconstruct, where supported:
- canvas/aspect ratio and safe margins;
- font hierarchy and typography;
- primary/secondary colors;
- cover and section pages;
- normal content layouts;
- data/table/chart layouts;
- comparison / before-after layouts;
- image-led layouts;
- ending page;
- logo/footer/page-number rules;
- shape, line and icon style.

## Registration lifecycle
1. Analyze the supplied source.
2. Classify source security and storage location.
3. Create an ASCII template id and workspace.
4. Create/update `design_spec.md` and real SVG/layout examples.
5. Start new imports as `status: CANDIDATE` unless they are already an approved native repository template.
6. Add source metadata such as `source_type`, `fidelity`, `visibility`, `version`, categories, keywords and aliases.
7. Render a registration-preview picker/card showing representative output and up to 6 detail layouts.
8. Wait for explicit user approval to register/activate the template.
9. Run `register_template.py` for the correct kind (`deck`, `layout`, or `brand`).
10. Change the approved template to `status: ACTIVE` and record approval metadata.
11. Regenerate/validate template galleries as required by repository rules.
12. Verify that the next live picker discovers the newly ACTIVE template automatically.

## Status policy
- `CANDIDATE`: can be reviewed but must not appear in normal recommendation/picker inventory.
- `ACTIVE`: eligible for normal picker display and recommendation.
- `DEPRECATED`: retained for history/explicit legacy use but excluded from normal recommendation.
- `DISABLED`: excluded from normal picker/recommendation.
- Missing status on legacy registered templates is interpreted as `ACTIVE` for backward compatibility.

## Fidelity policy
- `native`: repository-native template.
- `master_extracted`: based on actual PPTX/POTX master/layout extraction.
- `reference_reconstructed`: recreated from PDF/image/photo evidence.
Do not present `reference_reconstructed` as an exact extracted master.

## Direct-use rule
If the user explicitly names an existing registered template, validate that template and use it directly; do not force the recommendation picker. A deprecated template may be used only when the user's explicit request resolves unambiguously to it.
