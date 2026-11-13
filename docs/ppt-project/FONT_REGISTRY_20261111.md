# Shared font registry for Slide Master

The user approved the same private plugin update from 0.4.8 to 0.4.9.
The official readback verified both manifests and both instruction files
after normalizing JSON formatting and line endings. The 29-file inventory
and App declaration match the prior release. The mobile Chat workflow from
0.4.8 remains in the instruction file. The local 0.4.9 installation cache
was not observed during the check, and physical-device uptake is pending.

The shared registry is an owner-only Google Drive text file containing
schema-versioned JSON. Readback of revision 1 shows Pretendard as a temporary
production candidate and SamsungOneKorean 400/700 with usage rights pending.
The Samsung Drive location is user-reported; exact file IDs were not resolved.
No font binaries were read, uploaded, installed, or embedded. No default font
was set.

An owner-only QA copy exercised actual Drive upload, append to the same file
ID, and fresh readback. Revision 2 preserved both existing entries and the
default value, and included one additional pending font. A separate read
confirmed the actual registry remained at revision 1 with its two entries.
The connector roundtrip does not establish uptake in the PC and phone apps.
The user received the same-account lookup prompt for both devices. Adding
a real third font and checking both devices awaits the font choice and device
readbacks. The test copy remains private for verification.

The 0.4.8 changed-file baseline and a 0.4.10 overlay restoring that behavior
were preserved and ZIP-read verified. No new scopes, installations or fees
were added. Keep the actual registry link and account identifiers private.

## First addition to the live list

The user requested Noto Sans KR 400. A fresh read confirmed revision 1 and
no duplicate. The same owner-only Drive file was updated and read back as
revision 2 with three entries. The original entries and unset default were
preserved. Noto Sans KR was registered by name with usage checks pending.
The user received a prompt to compare revision 2 and the new entry on the
PC and phone. The two device readbacks are pending.
