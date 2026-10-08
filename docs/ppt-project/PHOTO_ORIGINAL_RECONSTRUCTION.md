# 사진 원본 복제 입력과 관찰값 계약

사용자는 **원본 그대로 복제 / 기존 자료 수정·보완 / 템플릿으로 새로 제작** 중 목적을 선택한다. ‘복제해줘’, ‘똑같이’, ‘원본 그대로’ 같은 표현이면 원본 복제를 우선 추천한다. 메뉴의 추천·임시 상태는 최종 선택이 아니다. 사용자가 이미 원본 복제를 명시했다면 그 현재 메시지를 선택 근거로 기록하고 다른 등록 템플릿을 추천하지 않는다.

기존 입력·라우팅 연결부에 더해 [모델 관찰→편집형 검토본 연결기](PHOTO_MODEL_ORCHESTRATION.md)를 추가했다. 새 복원 엔진, 자동 OCR, 카메라 보정기, 등록 템플릿 또는 호스트 UI를 만들지 않는다. 호스트 모델이 실제 양식과 전체 배치를 확인하면 지원 범위의 SVG 작성과 기존 변환기·렌더 호출은 코드가 맡는다. 실행 owner는 기존 project-private `create-template`이다. 원본 사진 기반은 `standard` + `literal` 시각 재구성이며 원본 Master/Layout/theme를 복구하는 `mirror`가 아니다. 설치된 플러그인 적용과 실제 회사사진 변환·렌더 성공은 별도다.

## 목적 메뉴에서 사진 참조로

기존 `presentation_brief.py`에 실제 요청을 전달한다.

```bash
python3 .claude/skills/ppt-master/scripts/presentation_brief.py <task-brief.json> --request-text '사진과 똑같이 만들어줘' --output <intake.json>
```

`purpose_menu_contract`의 세 choices를 호스트의 지원 선택 UI로 표시한다. `actually_rendered:false`는 데이터 계약만 준비했다는 뜻이며 UI 표시 완료가 아니다. 메뉴가 필요한 새 요청은 `purpose_menu_required:true`를 작업 brief에 저장한다. 실제 선택 후 `purpose_choice`, `purpose_confirmed:true`, `purpose_confirmation_ref`를 기록한다. 마지막 필드는 현재 사용자 선택 메시지/이벤트의 작업별 근거이며 사용자가 추가로 입력할 옵션이 아니다. 임시 선택이나 추천만 있으면 `ready_for_plan:false`다.

원본 복제는 `copy_original`이고 custom 참조 모드로 연결한다. 수정·보완은 `edit_existing`, 템플릿 제작은 `new_from_template`이며 실제 입력 형태에 따라 기존 router가 다음 owner를 결정한다. 원본 복제에 builtin ID/프리셋을 강제로 붙이면 거절한다. `reference_selection`은 현재 입력들의 정확한 SHA와 사용자 선택 근거를 보존한다. `registered_active_template:false`와 `exact_source_font_verified:false`를 유지하며 등록 선택 evidence로 전환하지 않는다.

새 필드를 사용하지 않는 이전 v2 brief는 기존 입력 동작을 유지한다. `--request-text`를 사용하거나 목적 선택 필드를 새로 기록한 요청은 해당 최종 선택 gate를 따른다. 버전1에 목적 메뉴 CLI를 적용하면 거절한다.

## 원본 관찰값을 추정과 분리하기

먼저 현재 Library 지원 경로로 실제 파일을 받아 모든 선택 사진의 픽셀을 본다. 저장된 관찰값은 `source_sha256`으로 정확한 사진 bytes와 묶고 아래 명령으로 검사한다. 관찰값 없이 기존 `reference_intake.py`를 쓰는 동작은 유지한다.

```bash
python3 .claude/skills/ppt-master/scripts/reference_intake.py <photo.jpg> --observations <observations.json> --output <reference-analysis.json>
```

관찰 sidecar는 schema_version 1이다. [합성 예시](../../.claude/skills/ppt-master/examples/photo_reference_intake/observations.json)는 회사자료가 아니다.

- `screen_region_px`: 사진 안에서 실제 슬라이드 화면을 잡은 x/y/폭/높이. 모니터 테두리나 주변 공간을 canvas로 자동 간주하지 않는다.
- `screen_quad_px`: 원근이 있으면 사진 좌표의 순서 있는 네 모서리. 선택 영역 안의 convex 사각형이어야 한다. 이 값은 보정 입력 후보이며 코드가 사진을 원근 보정했다고 주장하지 않는다.
- `slide_aspect_ratio`: 슬라이드 화면비 추정. 사진 파일의 가로/세로 비율과 분리한다. 원본 PPTX의 화면비가 확인되지 않았다면 추정으로 유지한다.
- `pixels_inspected`: 실제 픽셀 확인 사실. false면 사진 복제의 계획 단계도 막는다.
- `items`: 각 요소 ID와 property/value, 사진 안의 `source_bounds_px`, basis/certainty, `render_as`를 보존한다. 같은 요소/property의 충돌 기록은 거절한다.

property는 `text`, `geometry_px`, `font_family`, `font_size_pt`, `color`, `font_weight`, `line_spacing_pt`, `paragraph_spacing_pt`, `row_gap_px`, `column_gap_px`, `alignment`, `image_crop_px`, `tracking_pt`다. px와 pt를 서로 같은 값으로 간주하지 않는다. source bounds는 사진 화면 영역 안에 있어야 한다. 모든 숫자는 유한해야 하며 pt 크기는 양수, 간격은 음수가 될 수 없다. tracking은 명시적 음수를 허용한다.

basis/certainty는 다음 조합만 허용한다.

| 출처 | 확실성 | 용도 |
| --- | --- | --- |
| visible_text | observed | 실제 보이는 제목/내용/작성기준의 문구 |
| visual_estimate | estimated | 위치·색·굵기·폰트 후보·간격 등 사진 기반 추정 |
| user_instruction | confirmed | 현재 사용자가 명시한 글꼴/pt/기준. source_ref로 해당 지시 근거도 기록 |
| unknown | unverified | 확인 불가인 항목. value는 null |

사진 픽셀만으로 정확한 원본 font family나 theme color를 확정한 기록은 거절한다. unknown 값을 confirmed로 올리거나 관찰 hash가 바뀌어도 통과하는 동작은 없다. 사진에 명시된 pt 기준은 해당 기준 문구와 현재 확인값을 우선 사용한다. 이것이 사진에 보이는 모든 글자가 그 크기라는 의미는 아니다. 실제 font 파일/사용권/후보 렌더의 선택 확인은 기존 font-matching/private-font 계약으로 이어간다. 이미지/로고는 원본 asset 여부를 구별하고 임의 제작한 vector를 원본 로고라고 기록하지 않는다.

`render_as:native_editable`은 텍스트/도형의 재구성 목표이며 실제 출력 검사 PASS가 아니다. `preserved_image_crop`은 일부 이미지 영역을 raster로 보존하는 목표다. 텍스트/style를 image crop으로 표시하거나 화면의 대부분(80% 이상)을 한 이미지로 붙여 편집 가능한 복원이라고 기록하면 거절한다. 최소 native 재구성 목표가 있어야 한다. 작은 이미지 crop의 raster 보존은 허용하지만 최종 이미지의 정체·잘림·품질·편집 가능 범위는 시각 QA에서 확인한다.

## 기존 brief와 결합

현재 custom brief의 `reference_review[<actual input SHA>]`에 `observations_file` 상대 경로를 기록한다. 기존의 pixels/crop/text/aspect/perspective 확인도 모두 필요하다. copy_original에서 사진을 쓸 때 파일 누락, stale SHA, 출처/추정 불일치, 픽셀 미확인은 계획을 차단한다. 작성자가 geometry 확인을 했다고 대신 자동 기록하지 않는다.

실제 사용자 요청이 사진 두 장의 **빈 양식**이면 `output_intent:blank_template`로 내용 자료 요구만 생략할 수 있다. 이 예외는 확정된 사진 복제·실제 사진 참조에만 적용한다. 등록 템플릿 제작, native PPTX 채우기, 내용 덱의 내용 누락을 우회하지 않는다. 실제 보고서라면 `content_deck`와 현재 자료가 필요하다. 임의 가상 예시는 사용자가 요청했을 때만 쓰고 실제 성과로 표시하지 않는다. 글꼴/pt·장수·작성 기준과 현재 inputs_confirmed는 계속 필요하다.

성공한 intake도 `ready_for_generation:false`다. source 기반 template brief/복원 계획 확인 후 기존 owner의 serial SVG 작성, template QA, 정상 exporter, 최종 all-page render/편집성·overflow 검사를 따른다. 사용자에게는 내부 standard/literal/슬러그 옵션을 나열하지 않고 사진 원본 선택과 불확실한 화면 영역·비율·폰트 후보·인식 문구만 필요한 만큼 확인한다. 구현 선택은 작업별로 보존하며 전역 회사 기본값으로 만들지 않는다.

## 완료 범위와 남은 자동화

처음의 65개 계약 시험은 목적 메뉴 데이터와 입력 차단, 사진 관찰값/불확실성/선택 근거 sidecar의 검증이다. 이후 별도 연결기로 모델의 확정 배치→SVG→기존 structured PPTX 변환→공유 finalizer/render를 합성 2페이지에서 검증했다. OCR·모델 호출·원근 보정은 코드가 수행하지 않는다. 실제 호스트 메뉴 호출, 회사 사진과 최종 이미지의 비교, private Library 전달을 합성 시험으로 대신하지 않는다.

[공개 검증 요약](PHOTO_REVIEW_VALIDATION.md)은 목적 선택·출처·값·CLI·schema·legacy 호환과 별도 연결 검증의 범위를 기록한다. 실제 회사 사진의 복제·최종 원본 비교와 호스트 전달은 미검증이다. 공개 변경에는 합성 fixture만 포함한다. main 병합·운영 배포·ACTIVE 등록·플러그인 적용은 별도다.
