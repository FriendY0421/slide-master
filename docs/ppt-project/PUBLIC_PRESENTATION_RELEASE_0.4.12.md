# Public presentation guidance in private plugin 0.4.12

The user approved the latest public presentation candidate for the existing
private Slide Master plugin. The Plugin Creator update returned version
`0.4.12` as the current release. The publication used the observed `0.4.10`
release as its update precondition and submitted no file deletions.

The design reference includes layout guidance derived from Samsung Electronics'
public earnings deck, Galaxy Unpacked, TED/Gapminder, LinkedIn and Figma, with
examples from the existing template catalog. The delivery reference adds the
cloud font and mobile viewer guidance. See the
[source and design notes](BRAND_DESIGN_REFERENCES_20261111.md).

## Readback

| Check | Result |
|---|---|
| Current release and plugin identity | The update and source readback agree on version `0.4.12`. The plugin identity and personal private scope match the baseline. |
| Expected changes | Both manifests and both changed instruction files match the candidate. The compatibility manifest matches as parsed JSON and the delivery reference matches after text normalization. |
| Preserved source | All 29 paths were read. The other 25 files match the baseline, including the App declaration, skill entry point, Picker contract and validation scripts. The existing Drive font registry guidance remains present. |
| Runtime verification | PPTX generation, reopening, rendering and physical mobile use of this release were deferred at the user's request. The readback covers server-side saved source. |

No new connection, permission, installation or paid service was used in
the update.

## Recovery

The verified private candidate overlay was
`slide-master-0.4.12-public-presentation-layouts.zip`
with SHA-256 `c346e4049e4b4b523d6e55a6449812eaa6618375f209e4d423d4bd4ca6814e4e`.
The retained private overlay `slide-master-0.4.13-restore.zip` has SHA-256
`2e89ad0fa7d91fababcc4b348b3924259ea4c4f39641dff7ee26371ff593e93e`.
Its two reference files were compared with the live `0.4.10` baseline and its
manifests differ from that baseline only in version.

To restore that behavior while `0.4.12` is current, use the recovery overlay
with the same plugin and the freshly read current release ID as the update
precondition. Read back the new release and compare both references, both
manifests and the retained App declaration. If a later release is current,
reconcile its source before preparing a new restoration overlay.
