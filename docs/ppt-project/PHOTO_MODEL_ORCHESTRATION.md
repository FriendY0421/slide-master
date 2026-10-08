# 모델 관찰값에서 편집형 사진 복제 검토본까지

사진 업로드를 받은 호스트 모델이 모든 사진 픽셀을 보고 원문·화면 영역·레이아웃을 기록한 뒤, 코드가 그 입력으로 SVG와 편집형 PPTX 검토본을 만든다. 사용자가 SVG를 직접 작성할 필요는 없다. 사용자 참조양식 선택과 모델의 좌표·폰트·장식 판단은 서로 다른 출처다. 사진 인식은 모델 단계이며 이 연결기는 OCR, 원근 보정 또는 모델 서비스를 호출하지 않는다.

새 연결기는 기존 project-private `create-template`의 standard/literal 경로를 사용한다. 기존 `template_preview_pptx.py`의 정상 structured 변환기를 호출하며 `--visual-only`를 사용하지 않는다. 결과는 미등록 private template workspace와 optional structured review PPTX다. 일반 builtin 신규 덱의 picker·preset·storyline을 승인했다고 기록하지 않고, create-template의 기존 exemption을 기록한다. 이 코드만으로 일반 신규 덱 경로나 호스트 UI가 배포·연결된 것은 아니다.

## 호스트가 받는 입력

정식 계약은 [JSON Schema](../../.claude/skills/ppt-master/schemas/photo_reconstruction_plan.v1.json), 실제 실행한 전체 입력은 [합성 plan](../../.claude/skills/ppt-master/examples/photo_reference_orchestration/plan.json)이다. 사용자에게 이 내부 필드를 채우게 하지 않고 호스트가 현재 관찰·선택·승인 근거로 작성한다.

- 최상위: `schema_version:1`, 안전한 `project_name`, `purpose_choice:copy_original`, 실제 `purpose_confirmed:true/purpose_confirmation_ref`, `canvas_px:[1280,720]`, 정확한 `slide_count`, `font_choice`, 전체 `pages`.
- 이미 확정된 입력 경로는 기존 `layout_confirmed:true/layout_confirmation_ref`와 design font의 `confirmation_ref`를 유지한다. 승인 근거가 없는데 이 필드를 채우지 않는다.
- **모델 추정 검토 경로**는 `review_only:true`, `layout_basis:visual_estimate`, `layout_review_ref`를 사용한다. `layout_confirmed`는 생략하거나 false이며 `layout_confirmation_ref`는 넣지 않는다. 폰트는 `basis:visual_estimate`, 실제 모델 선택의 `review_ref`, `source_font_identity_verified:false`다. 폰트 `confirmation_ref`를 넣으면 차단한다. 이 경로는 사용자가 요청한 사진 재구성의 검토용 시제품을 만들며, 개별 좌표·폰트·생략에 대한 사용자 승인을 주장하거나 요구하지 않는다.
- `font_choice.family`는 실제 사용할 family다. 준비된 Pretendard Regular/Bold를 명시적으로 선택하면 포함된 OFL 파일과 hash를 검사한다. 다른 family는 `font_files:{regular:<OTF/TTF>,bold:<OTF/TTF>}`와 기존 `font_license_review`(reviewed, cloud_use, embedding, evidence_file/evidence_sha256, font_sha256)가 필요하다. 실제 family/style/hash/glyph와 사용권을 검증한다. TTC는 기존 검증기가 지원하지 않으며 추출·설치·다른 family로 조용히 대체하지 않는다.
- 페이지: `title`, `source`, 기존 `observations` sidecar, 순서 있는 `elements`, 모든 생략을 기록한 `omitted_decorations`.
- `source`: 실제 `sha256`, `pixel_size:[폭,높이]`, `input_type`, `review_origin`, 실제 픽셀 확인의 `visual_review_ref`, 가능하면 로컬 `file`. 로컬 파일은 bytes/hash/크기를 다시 검사한다.
- 부모 환경에만 사진이 있을 때: `file`을 생략하고 `review_origin:parent_model_visual_analysis`를 명시한다. 기존 관찰값을 동일한 원본 SHA와 묶는다. 감사 기록은 `source_bytes_verified_locally:false`로 유지한다. 이 경로는 명시적인 모델 관찰 인계이며 다운로드 실패 복구·로컬 픽셀 확인·원본 구조 회복을 주장하지 않는다. 실제 비교 QA는 사진을 볼 수 있는 부모가 맡는다.

`observations`는 schema_version 1이며 `source_sha256`, `pixels_inspected:true`, 화면 영역 `screen_region_px`, 화면비 추정 `slide_aspect_ratio`, 선택적인 `screen_quad_px`, 요소별 `items`를 갖는다. item은 `element_id/property/value/basis/certainty/source_bounds_px/render_as`를 갖고 user_instruction에는 `source_ref`가 필요하다. [기존 관찰값 계약](PHOTO_ORIGINAL_RECONSTRUCTION.md)이 출처·확실성·화면 범위를 검사한다. 사진의 1280×800 비율을 자동으로 슬라이드 비율로 사용하지 않는다.

각 element는 `id`, `type`, 사진 공간의 `source_bounds_px:[x,y,w,h]`, 모델이 보정한 슬라이드 공간의 `bounds_px:[x,y,w,h]`를 갖는다. 두 공간은 별도로 보존한다. 각 요소는 같은 ID의 관찰 geometry/crop과 묶여야 하며 관찰된 모든 ID가 결과 요소 또는 명시적 생략으로 설명돼야 한다.

관찰에 원문 text가 있는 ID는 반드시 편집형 text 요소로 남긴다. 같은 ID의 rect/line으로 바꿔 원문을 없앨 수 없다. 숫자 `700.0`은 `700`과 같은 굵기로 정규화하여 기존 변환기로 전달한다.

| type | 추가 필드 | 출력 |
| --- | --- | --- |
| text | text, font_pt, font_family, font_weight:400/700, color:#RRGGBB, align:left/center/right, line_height_px | 편집형 네이티브 텍스트 |
| rect | color:#RRGGBB | 편집형 직사각형 |
| line | color, direction:horizontal/vertical, stroke_width_px | 편집형 선 |
| image | asset_file, asset_sha256 | 제공된 작은 이미지 crop; raster 범위 공개 |

좌표·박스·line_height·stroke_width는 **px**, font_pt는 **pt**다. 글자 크기는 정해진 전역 14/12pt가 아니라 입력값을 따른다. 줄바꿈을 포함한 원문과 공백을 유지한다. 실제 선택 폰트의 glyph를 측정하고, 글자가 넘치거나 줄 간격이 겹치면 모델에게 명시적 줄·박스·문구 수정을 요구하는 오류로 끝난다. 폰트를 줄이거나 글자를 잘라내지 않는다.

사용자가 교체 문구 자체를 확정했다면 `observations.items`의 원문을 유지하고 해당 element에 `text_override:{basis:user_instruction,certainty:confirmed,source_ref:<현재 승인 근거>,original_observed_text:<사진 원문>}`를 추가한다. element.text만 교체 문구를 갖는다. 사용자가 가상 전략 작성을 요청했고 구체 문구는 모델이 작성했다면 검토 경로에서 `basis:user_authorized_synthetic`, `certainty:model_written`, 실제 요청 `source_ref`, `original_observed_text`를 사용한다. 페이지의 `synthetic_content_disclosure` 문구가 실제 text element에 있어야 한다. 모델 문구를 사용자가 한 글자씩 확정했다는 의미로 올리지 않는다.

로고·아이콘을 생략하면 기존 실제 사용자 승인 경로는 `omitted_decorations:[{element_id,reason,confirmation_ref}]`를 남긴다. 모델 검토 경로는 `{element_id,reason,basis:visual_estimate,certainty:estimated,review_ref}`를 사용한다. 이때 confirmation_ref를 붙이거나 certainty를 confirmed로 올릴 수 없다. 관찰된 필수 텍스트를 장식으로 처리해 생략할 수 없다. image에는 이미 잘린 실제 로컬 자산이 필요하며 hash·비율을 검사한다. 화면 대부분을 사진 한 장으로 붙여 편집형 결과라고 처리하지 않는다.

모델 추정 검토 입력의 차이는 다음과 같다. source·관찰·요소 계약은 동일하며 실제 사용자 참조 선택 근거는 계속 필요하다.

```json
{
  "review_only": true,
  "layout_basis": "visual_estimate",
  "layout_review_ref": "현재 모델의 사진 관찰/배치 기록 근거",
  "font_choice": {
    "family": "Pretendard",
    "basis": "visual_estimate",
    "review_ref": "현재 모델의 가용 폰트 후보 선택 근거",
    "source_font_identity_verified": false
  }
}
```

## 실행과 검수

```bash
"$CODEX_PRIMARY_RUNTIME_PYTHON" .claude/skills/ppt-master/scripts/photo_reconstruct.py <confirmed-plan.json> --check
"$CODEX_PRIMARY_RUNTIME_PYTHON" .claude/skills/ppt-master/scripts/photo_reconstruct.py <confirmed-plan.json> --workspace-parent projects/<private-builds> --presentations-skill-dir <verified-shared-Presentations-skill>
```

`--check`는 파일을 만들지 않는다. 실제 실행은 현재 확인된 입력과 제공 runtime을 검사한 다음 기존 project_manager로 충돌 없는 프로젝트를 만든다. 모델 입력과 원본 출처·font hash·fit 측정·생략을 analysis에 저장하고, 페이지1 SVG gate 후 나머지 페이지를 작성한다. 전체 template quality gate를 통과해야 기존 structured compiler를 호출한다. 새 white Master와 의도적인 단일 zero-slot Layout을 만들며, 복제한 텍스트와 도형은 Slide-local 객체로 편집할 수 있다. 이것은 사진에 있던 원본 Master/Layout을 회복하는 기능이 아니다.

최초에 읽은 JSON bytes를 `analysis/received-model-plan.json`에 그대로 보존하며 감사 SHA도 그 bytes로 계산한다. 검증 중 입력 파일이 수정돼도 새 내용을 기존 실행의 근거로 기록하지 않는다. 이미지 자산은 복사할 bytes의 SHA를 다시 확인하고, 검증 후 변경됐거나 목적지 bytes가 선언된 SHA와 다르면 변환을 중단한다.

글자 넘침을 측정한 Regular/Bold 폰트의 SHA를 프로젝트 생성 전, 공유 finalizer와 렌더 직전, 렌더 후에 다시 확인한다. 렌더 manifest의 `registered_fonts`도 동일한 파일 경로와 SHA 전부를 기록해야 한다. 누락·추가·불일치가 있으면 검토 준비 완료 receipt를 만들지 않는다. 통과 근거는 `analysis/font-render-binding.json`에 저장한다. 선택한 실행 폰트 파일의 일치 검사이며 사진 원본 폰트를 알아냈거나 실제 PowerPoint의 폰트 대체 동작을 검증했다는 뜻은 아니다.

네이티브 readback은 장수·원문 각 줄·font family/pt/굵기·도형·이미지를 검사한다. 각 텍스트 run의 pt가 명시돼 있어야 하며 일부 run의 크기가 누락됐거나 굵기가 달라져도 차단한다. 이는 출력이 기록된 계획과 맞는지 검사하며 사진의 원본 폰트·간격을 확정하지 않는다. 공유 finalizer가 별도 final PPTX를 만들고, 기존 supported render helper가 final의 모든 페이지를 렌더한다. analysis의 orchestration receipt는 정확한 final/render SHA와 `visual_source_comparison_pending:true`, `user_delivery_ready:false`를 기록한다. 자동 검사만으로 원본과 같다고 판정하지 않는다. 호스트는 원본과 모든 final render를 비교하고 폰트 추정·생략·원근으로 인한 차이를 설명한 뒤 전달한다. 실제 PowerPoint 앱에서 열어 확인했다고 주장하지 않는다.

## 최소 지원 범위와 남은 연결

현재는 명시적인 1280×720의 흰 배경, literal text·rect·가로/세로 line·제공 crop의 검토본을 지원한다. 회전, 투명도, 복잡한 path, 그룹 효과, SmartArt, 새 table/chart, TTC 또는 nonzero tracking/paragraph spacing은 지원하지 않는다. 알 수 없는 element 필드는 무시하지 않고 차단한다. 그런 요소는 기존 적합한 owner로 넘기거나 구현 후보로 보고해야 한다. 모델의 원문 인식·원근 판단·전체 요소 누락 여부는 실제 픽셀 비교가 필요하다.

검증은 [공개 요약](PHOTO_REVIEW_VALIDATION.md)에 합성 시험과 실제 미실행 항목을 분리해 기록한다. 실제 회사 사진의 모델 관찰 입력·최종 원본 비교, 호스트 메뉴에서 이 스크립트 호출·자료 전달, private 설치/운영 배포는 별도다. 외부 OCR·새 로그인·유료 API·신규 의존 설치가 필요하지 않으며 main 병합·ACTIVE 등록·플러그인 변경은 이 코드의 검증 범위가 아니다.
