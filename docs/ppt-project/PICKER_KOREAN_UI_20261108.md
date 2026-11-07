# Korean Picker menus and actual host observation

The user reported operating the original Picker and seeing **"선택이
확정되었습니다"**. This is user evidence of visible interaction/success screen,
not an assistant screenshot or a captured returned template/preset pair. No
automatic selection message with the IDs arrived in this task. Therefore actual
host rendering has user-reported evidence while exact selection return remains
unverified. Do not insert an isolated test's pair as the user's choice.

The actual connected tool after the safety fix returned the current GitHub/main
21-entry catalog, six candidates and five presets; both existing server/tunnel
health endpoints returned 200. See [live receipt](evidence/picker-confirmation-20261108/live-host-call.json).
It still reports initial host_ui_rendered=null, separate from user observation.

## Applied local runtime changes

Same original PR #6 runtime/App, no replacement or dependency installation:

- Korean menu labels: basic template choice, complete-slide versus individual
  layout filters, free design, preview-unavailable notice and known detail labels.
- Six existing production-preset IDs have Korean display labels, including
  균형형 보고서, 핵심 요약 보고, 설득형 제안서, 데이터 분석 보고,
  교육·사용 안내 and 제품·서비스 소개. IDs/original names/profiles remain intact.
  Future payload `display_name_ko` is preferred; current runtime uses the same
  ID-based labels without requiring an unmerged live-catalog change.
- Existing company-source/CUSTOM path is described in the gallery: attach the
  actual company file/photo in chat. No nonfunctional upload button, invented
  attachment or registered CUSTOM template ID is added.
- Host-message acknowledgement screen now says **"선택값 전달 요청 완료"**,
  rather than proving conversation receipt. It retains the exact token and a
  user-clicked copy button if the token does not appear in chat. Existing
  automatic `ui/message`/model-context bridge remains; no duplicate legacy send.

The [official shared UI bridge](https://developers.openai.com/plugins/build/chatgpt-ui)
distinguishes `ui/update-model-context` from `ui/message`. Installed MCP Apps SDK
1.7.5 defines `isError` as delivery rejection/failure; absence of that flag is
the current acknowledgement path, not independently observed transcript content.
Root cause of the missing selection pair in this task is **not established**.

## Verification and recovery

[Exact patch](evidence/picker-korean-20261108/picker-korean.patch) applies after
the [confirmation safety fix](PICKER_CONFIRMATION_FIX_20261108.md). Existing
esbuild and Node syntax checks pass. [Sixteen confirmation cases](evidence/picker-korean-20261108/confirmation.json)
still pass. [Isolated real-frontend inspection](evidence/picker-korean-20261108/ui.json)
uses an actual live 21-template payload with an **explicit mocked host bridge**:
Korean filter/preset/final labels, unchanged selection IDs and generation=false,
single mock message, copy-button presence, zero page errors and 320px layout pass.
Its [mobile image](evidence/picker-korean-20261108/mobile.png) is not a real host
screenshot or the user's selected pair. Images were visually inspected.

The [actual current server resource readback](evidence/picker-korean-20261108/resource.json)
also contains the localized menus, presets, copy action and delivery-request
wording: 607,381 bytes, SHA256
`e320d1edc8d8964774ad0b51f0421bc940a9a6e3e33f0255d01aea9fea99eb82`.
Initial literal-string inspection failed because esbuild escapes Unicode;
decoding those JavaScript escapes in the inspection copy resolves the check
with the raw resource bytes/hash unchanged. This was an inspection issue, not a
missing Korean label. Existing preset JSON matches its baseline exactly after
removing the six added optional display-name fields.

Runtime source SHA256:
`1c1c25340fbda21b2d853de12c72e459c392d6c88cd629cb02d62e8ad80e5294`.
Bundle SHA256:
`9b327d3d88de57ff8c270b7e30734bdcdcc19322ebe697ffaeb21186027bb9e8`.
Original pre-localization source/bundle are preserved in project sibling
`review/picker-korean-20261108/` as `app.before.js`/`bundle.before.js`.
Restore only those files to undo localization while keeping the previous safety
fix; do not reset the runtime checkout/pre-existing server modification.

Public `docs/gpts/PRODUCTION_PRESETS.json` adds only optional Korean display
fields. Existing source/backup copies and main plugin 0.4.5 remain intact.
Currently opened host frames may retain old text until reopened. This does not
establish PC-off availability, install a persistent service or update the main
plugin package. Existing foreground server/tunnel were started only for this
user test; stop only their owned sessions when the test is finished. Handle
records stay in the private review directory.

Cleanup after the user's reported test: both owned foreground sessions were
terminated, and ports 3000/8080 have no remaining listeners. No persistent
process was left behind. Use the existing launcher for a later host check.
