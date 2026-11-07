# Dot computer, Picker hosting and storage assessment

## Identified and unidentified environments

The user selected OpenAI dots' own virtual computer as the preferred existing
cloud target. Do not substitute the connected Windows PC or the saved Codex
Cloud environment with a similar name. The accessible Desktop Commander device
inventory contains HOME-PC only. The saved Codex configuration is a reusable
configuration, not proof of the identity or capacity of a running Dot computer.
No new environment, service, credential or App has been provisioned.

The user supplied a status from a separate Service Insight conversation:

| User-reported filesystem view | Earlier remaining | Latest reported after that task's cleanup |
| --- | --- | --- |
| Work volume, approximately 33.8GB total | 0.71GB | 3.52GB |
| Temporary volume, approximately 9.44GB total | 1.34GB | 7.59GB |

These are user-provided approximate observations, **not measurements made by
this Slide Master task**, current availability guarantees, or account quotas.
The other project owns its sources, builds and cleanup. Do not inspect/delete
its files or send it messages under this project's authority. Keep Slide Master
work isolated and avoid competing heavy builds/renders on a shared low-space VM.

## Official support and limits

OpenAI documents that [a dot's computer remains available with the user's PC
off](https://learn.chatgpt.com/docs/dots/computers-and-apps). Disk/browser state
can persist. This does not establish an always-running Node/tunnel daemon,
inbound endpoint support, process restart policy or unlimited disk/RAM.

The numerical VM table in [Codex Cloud environments](https://learn.chatgpt.com/docs/environments/cloud-environments)
describes that product's cloud tasks: 8GiB disk for the listed Plus tier and
32GiB for the listed Pro/Business/Enterprise tiers. **It is not a Dot-specific
storage guarantee.** No fixed Dot disk/RAM quota was established in the inspected
Dot documentation. Confirm the actual selected computer and applicable plan;
do not relabel this table or a filesystem's host-visible space as the Dot quota.

[Dot tasks](https://learn.chatgpt.com/docs/dots/tasks-and-memory) run on their
original computer/environment; selecting another computer does not move an
existing task. This current local Codex task has not migrated into the Dot VM.

## Read-only resource probe

Prepared existing-source helper:
`.claude/skills/ppt-master/scripts/probe_picker_host.py`.

```sh
python .claude/skills/ppt-master/scripts/probe_picker_host.py --path ACTUAL_TASK_DIRECTORY
```

Run **inside the identified Dot computer** and correlate the receipt with the
host-provided computer reference. It reports filesystem-view free bytes, current
Python/Node versions, visible CPU count and Linux cgroup-v2 memory/CPU counters.
Optional `--measure PUBLIC_ASSET_DIRECTORY` counts metadata with bounded traversal;
it excludes Git/dependency caches and symlinks, so it is not full installed size.
It reads no environment variables/keys, makes no network requests, installs
nothing, starts no server and deletes nothing. Unsupported counters stay null.
The helper intentionally cannot certify computer identity, account quota,
outbound access or service persistence by itself.

Current tool access cannot execute commands on the user's named Dot computer.
During the later local 0.4.6 installed-cache verification, the authorized device
inventory still exposed only HOME-PC. This is not evidence of Dot free space or
absence of a Dot computer in the user's account, and no device was added.
The smallest needed handoff is to run this read-only probe from that Dot's own
conversation/computer and return its receipt. A result from the already used
Cloud Work trial must remain labeled Cloud Work unless platform identity proves
it is that same Dot computer. No tunnel key may be copied for this diagnostic.

## Measured source/artifact footprint and working-space guidance

Local file measurements, not Dot quota: tracked source about 29.5MiB; current
main skill directory about 31.25MiB; installed 0.4.5 package about 0.28MiB;
provided complete Node package directory about 367MiB (the Artifact Tool package
alone is about 122MiB, not its full dependency closure). These values exclude
OS/Python/browser installations and do not prove every platform's installed size.

The representative two-slide PPTX is only 40,449 bytes; its two PNG renders and
receipts are about 0.11MiB. This is not a photo-heavy workload estimate. Current
self-contained template HTML is about 0.77MiB. See the sanitized measurement
receipt beside the offline UI evidence.

When the existing runtimes are already available, recommend about **2GB free work
space** for an initial bounded job and **5GB or more** for image-heavy work or many
retained revisions. These are conservative operating recommendations, not official
minimum specifications or a measured large-deck pass. The reported 3.52GB may be
adequate for a lightweight task, subject to a fresh check and other workloads.
Below 1GB, avoid downloading another runtime/model and assess a small job first.

Use existing libraries rather than duplicating them per job. Keep authoritative
source, inputs, results and recovery in GitHub/private Drive as appropriate;
download only the active job. Temporary-volume bytes are not durable backup.
Verify upload/access/raw hashes before considering disposal of task-owned
reproducible files; no deletion of originals or shared caches is authorized here.

## Same-App hosting versus the no-server alternative

| Option | Cost/permission and identity boundary | Recovery |
| --- | --- | --- |
| Existing self-contained HTML / GitHub visual gallery | No new server, key or App. Offline template/detail/preset display requires actual manual return of IDs in chat. It is not the original Picker callback. | Keep existing App/runtime; retain the old source commit and artifact snapshots. |
| Existing Picker runtime and matching tunnel on the identified Dot VM | Potential same-App route, but needs actual runtime/dependency, allowed outbound access, process persistence and private credential-storage verification. Copying the runtime key/installing a platform client needs a separate concrete approval. No fee-free hosting guarantee yet. | Stop the approved cloud client, retain same tunnel/App mapping, resume preserved Windows foreground runtime; never overlap clients blindly. |
| Site-hosted MCP | Officially supported hosting, but publication provisions an associated App/plugin. Current owner inventory has no identified Slide Master Site. It is not an approved same-App migration and is not selected as a replacement. | Preserve old connection; requires separate reviewed identity/hosting scope first. |

[Official tunnel routing](https://github.com/openai/tunnel-client/blob/master/docs/connectors.md)
requires the matching runtime client to poll and forward to the configured MCP
server. A cloud connector invocation alone does not move that client. A same-ID
runtime migration is a **candidate**, not a verified hosted service or a license
to transfer the key. [Sites hosting](https://help.openai.com/en/articles/20001547-hosting-a-plugin-with-chatgpt-sites)
requires its own publication/connection workflow; no Site was created or changed.

Before live migration, group the exact computer, dependencies, outbound targets,
credential handling, expected usage/cost, ownership, stopped/resumed client plan
and rollback into one approval. Validate original UI rendering, real template +
preset callback, restart/reconnect and PC-independent operation afterward. Keep
the full delivery goal active until actual intake/approval/production/download
and recipient evidence exist.
