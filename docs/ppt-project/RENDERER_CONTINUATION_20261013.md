# Renderer continuation and real cloud trial

Continues Draft #14. Source/quality work is separate from operational deployment
and the user's authenticated attachment/approval/private-delivery acceptance.

## Recovered CPU workaround

The earlier local operating handoff contained a successful `render_review.mjs`
CPU fix. It was inspected and reused rather than rebuilding a renderer.
In the current supplied runtime, setting `Canvas.gpu = false` explicitly yields
OS exit 0. Earlier constructor-option CPU, sync and single-thread probes still
terminated abnormally. This is a validated local workaround, not identification
or repair of the vendor's exact native teardown function.

`render_pptx_review.mjs` reuses that process-local Canvas subclass/setter before
Artifact Tool import. No bundled dependency, registry, OS font or operating
checkout is changed. `render_pptx_review.py` launches it and accepts a receipt
only after OS exit 0, actual presentation page count, source SHA and all PNG hashes
agree. It preserves existing nonempty review folders and rejects failed/partial
render receipts. A supplied font profile must bind explicit family/files/SHA;
the caller must have rights. Registration alone does not certify every rendered
text run or establish a license.

```text
python .claude/skills/ppt-master/scripts/render_pptx_review.py PRIVATE.pptx NEW_PRIVATE_OUTPUT --node SUPPLIED_NODE --runtime SUPPLIED_NODE_MODULES --profile APPROVED_PRIVATE_PROFILE.json
```

Profile shape:

```json
{"font_family":"approved family","font_files":[{"path":"approved-file.otf","sha256":"actual 64-character hash"}],"slide_count":1}
```

`--geometry-only` is explicit, excludes slide text/charts and enabled template
footer fields, and does not read/register font files. Instructional placeholder
samples in otherwise empty template layouts are not treated as displayed slide
content. Vector/geometry output is not a selected-font certificate.

The existing final verifier is connected through an opt-in path, without changing
the older default OfficeCLI behavior:

```text
python .claude/skills/ppt-master/scripts/verify_deck.py PRIVATE_PROJECT --review-node SUPPLIED_NODE --review-runtime SUPPLIED_NODE_MODULES --review-font-profile APPROVED_PRIVATE_PROFILE.json
```

All three flags are required together and conflict with `--no-render`. Prior
validation failures prevent render certification. Outputs have unique private
folders and `review_render_receipt.json` points to the manifest. Manual visual
review stays false until an actual operator inspects the pages.

## Actual evidence

- Font-free two-page native geometry deck: both pages reimported/exported, OS 0,
  source and PNG hashes checked; images inspected. No registered font files.
- A text-bearing deck is rejected by geometry-only mode. An invalid font profile
  is rejected, no successful render receipt is issued, and previous review evidence
  cannot be overwritten accidentally.
- The repository's existing [Pretendard OFL license](https://github.com/orioncactus/pretendard/blob/main/LICENSE)
  was read. An explicitly temporary Pretendard sample has actual-font metrics
  errors 0, native header 12pt/body 11pt/note 9pt, and a successful one-page CPU render.
  No Samsung files were read, registered, embedded or sent to a cloud environment.
- The temporary sample passed the actual `verify_deck.py --review-*` integration
  with renderer OS 0. Planning validation was skipped for the engineering fixture;
  this is not a production storyline approval or company-template certificate.
- Original failure logs remain. [A similar upstream Windows report](https://github.com/openai/codex/issues/36375)
  has a different status code and failure stage; do not equate its cause with ours.

## Existing production components and trial boundary

The current approved main is still `0578dba`. Existing #6 and #10–#13 remain open
Draft PRs. #10–#13 form a stacked series; #6 is a separate picker branch. They
must not be treated as present in main or operationally connected. The #13 CI
workflow can run on matching pushes/PRs: do not copy or activate it casually under
an approval limited to source review without checking its impact.

Official dependency lookup cannot resolve the GPT-derived instruction package
through its public-plugin-only interface. This is not an ownership denial. The
main editable release and saved connection/access scope remain unverified.
The current connected device inventory exposes only HOME-PC, not a cloud device.
Browser automation initialization failed before opening a new management view;
no authentication/settings action or access bypass was attempted.

The user authorized one new Cloud Work trial on the same ChatGPT account using
PR #14 and a non-sensitive synthetic image, within the existing plan only. Stop
if a new permission, payment, installation or service is required. No Samsung
font or company input is transferred; no plugin/server replacement is approved.
This authorizes a trial, not merge/deployment or full-flow completion.

[synthetic-cloud-input-20261013.png](evidence/synthetic-cloud-input-20261013.png)
is an original synthetic review image using the licensed temporary font. It has
no company data or font binary and explicitly labels its non-Samsung status.
If a host only downloads this public source, do not call that a real user upload
or fabricate an actor-bound file ID. The actual host attachment/ownership,
current outline/design approval and private recipient download/opening still
require direct evidence. Ask only for the exact missing boundary, not a new
plugin, invented identity or unrelated source file.
