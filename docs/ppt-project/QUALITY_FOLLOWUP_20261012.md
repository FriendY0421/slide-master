# Quality follow-up: evidence and remaining conditions

This continues Draft #14 and preserves its earlier 38-region report and original
fixtures. It does not activate the candidate, register a replacement plugin,
install fonts or certify a production attachment/download round trip.

## PowerPoint chart editing

PowerPoint 16.0 opened the existing two-slide synthetic fixture. The embedded
Excel B2 changed from 84.5 to 85.75. The workbook, chart values, saved OOXML chart
cache and reopened PowerPoint chart all retained 85.75/90. The original deck's
SHA-256 stayed unchanged. There were no external relationships or font parts.

The first automation closed the workbook before refreshing the chart: the
workbook retained 85.75 but the chart cache retained 84.5. Calculating the sheet
and refreshing while the workbook remained open resolved that mismatch. An
earlier cleanup sequence also produced RPC/unavailable-object errors; retain
those attempts as failures. Export the reopened slide before closing its data
workbook and close only the presentations/workbooks created by the probe.
This is an automation ordering finding, not proof of a converter defect.
See [ChartData.Workbook](https://learn.microsoft.com/en-us/office/vba/api/powerpoint.chartdata.workbook).

The edited deck is a verification copy: its table deliberately keeps the original
84.5 while the chart changes to 85.75. It is not a final company presentation.
Its PowerPoint preview is explicitly font-unverified.

## Renderer exit isolation

Bundled Node v24.19.0 / skia-canvas 3.0.8 on Windows:

| Probe | Process result |
|---|---|
| Node only | 0 |
| Load native module only | 0 |
| Artifact Tool import only | 0 |
| Render a rectangle with no PPT, text or private font, CPU | 0xc0000409 |
| Same rectangle, GPU | 0xc0000409 |

The PNG buffer completed and the JavaScript exit event reported 0; the operating
system still reported abnormal termination. Earlier synchronous and single-thread
probes did not resolve it. This isolates the failure to the local native rendering
or shutdown stack. It does not identify an exact native function without a dump
and does not establish that the PPT is defective. Do not suppress the result with
process.exit(0). The existing PNGs remain partial artifacts, not a clean process
receipt. No runtime replacement, installation or dependency upgrade was made.

`scripts/diagnose_native_renderer.mjs` runs font-independent child probes, records
raw OS status and returns failure if any probe fails. Use an existing approved
runtime; the script does not install dependencies. Example from the repository:

```text
node .claude/skills/ppt-master/scripts/diagnose_native_renderer.mjs <node_modules> <private-report.json>
```

This emits hardware/runtime diagnostics: keep reports private. A supported
vendor runtime fix or a different approved renderer is the next option. Windows
PowerPoint export is an independent local check, subject to font permission.
CPU/GPU controls are documented by [Skia Canvas](https://skia-canvas.org/api/canvas).

## Real material and font conditions

The user identified a previous generated three-slide deck, not a company source.
It was not found in the working and handoff directories or the user's Documents,
Downloads and Desktop filename scan. Do not substitute similarly named synthetic
fixtures. Review that exact supplied result when available; source/master/protected
area comparison still requires the original company PPTX and edit-region brief.

No new Windows font registration occurred. Local production/rendering permission
and separate temporary-session registration approval remain pending. Cloud
installation, cloud rendering and output embedding are separate unresolved rights.
File possession and embedding flags are not license evidence.

## Connection and cloud evidence

Existing owner-visible settings establish the picker identity, not the main
instruction plugin's editable release identity or saved transport/workspace scope.
Do not repeat failed discovery or replace the installed plugin. The remaining
owner-side record must identify the main editable plugin/release, exact transport
target and authorized account/workspace scope, then map that release to source.

The current signed-in account exposes Work composition and cloud-computer settings.
Its Work plugin search offers the existing Slide Master as a selectable checkbox;
the menu exposes no release/editor identity. No checkbox was enabled.
That proves UI availability only. Execution entitlement, plugin tool access,
file retention/private download and effective limits/cost have not been exercised.
No task was submitted and no permission or billing setting changed. An actual
approved cloud job is required before claiming PC-independent production.
