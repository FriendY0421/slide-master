# 작업별 제작 모드와 원본 양식 보존

매 작업 시작 시 **기본 제공 템플릿 / 사용자 정의 템플릿**을 선택한다.
이 선택과 글꼴·크기·작성 기준은 해당 작업의 brief에만 저장한다.
사용자가 요청하지 않은 영구 회사 기본값은 만들지 않는다.

## 기본 제공 템플릿

기존 등록 템플릿 → 제작 프리셋 → 최신 근거 → 스토리라인 확인 → 제작 순서를 유지한다.
디자인 개선 예제는 리뷰 후보이며 전체 등록 템플릿을 자동 교체하지 않는다.
`presentation_brief.py`는 입력만 점검하며 기존 선택/승인 gate를 대체하지 않는다.

## 사용자 정의 템플릿

원본 PPTX, 참고 샘플, 이번 내용 자료, 글꼴, pt 크기, 작성 기준을 작업별로 받는다.
글꼴/크기/작성 기준은 '원본 유지'를 명시적으로 확인해도 된다.
샘플이 없으면 '샘플 없음'을 확인한다. 빠진 필수 항목만 한 번에 묻는다.
이미 제공/확인된 값을 다시 질문하지 않는다. 입력 충돌은 제작 전에 해결한다.

우선순위: 이번 사용자 명시 지시 → 확인한 작업 brief → 원본 템플릿/선택 샘플 → 모드 기본값.
명시 지정값이 원본과 다르면 임의로 원본 또는 새 값 중 하나를 선택하지 않는다.
글꼴/pt 덮어쓰기는 현재 native-fill v1 범위 밖이다. 원본을 지정값으로 수정한 사본을
사용자가 확인하거나, 별도 스타일 수정 범위를 합의한 뒤 진행한다. 원본 충실모드를
스타일 변경 모드라고 오인하지 않는다.

`ppt-template-fill` 경로로 원본 슬라이드를 복제하고 허용된 텍스트/표 셀만 바꾼다.
Master/Layout/theme/placeholder/slide size/위치/여백/로고/색/번호/각주를 이미지로
평탄화하거나 새 디자인으로 덮지 않는다. 슬라이드 순서/반복/삭제와 편집 영역을 확인한다.
샘플은 실제 회사 양식을 재현하는 근거이며 장식 참고용 기본 템플릿으로 취급하지 않는다.

```json
{
  "schema_version": 1, "scope": "task", "mode": "custom",
  "template_files": ["sources/original.pptx"],
  "sample_files": ["sources/approved-sample.pptx"],
  "content_files": ["sources/current-material.md"],
  "font_policy": {"basis": "source"},
  "font_size_policy": {"basis": "source"},
  "writing_rules_policy": "source",
  "inputs_confirmed": false
}
```

실행: `python3 .claude/skills/ppt-master/scripts/presentation_brief.py <project>/analysis/design_brief.json`
공개 입력 schema: `.claude/skills/ppt-master/schemas/presentation_brief.v1.json`.
상대 경로는 brief 파일 디렉터리 기준이다. `inputs_confirmed`는 사용자 확인 사실만 기록한다.
검증 통과가 제작 승인을 의미하지 않는다. 다음은 기존 fill-plan 검토/확인이다.

## 선택형 template_fidelity v1

fill plan 루트에 `template_fidelity: {schema_version: 1, source_sha256: "..."}`를 기록하고
각 슬라이드에 `editable_targets: {slots: ["s01_sh4"], table_cells: []}`를 명시한다.
교체 대상은 canonical slot/table ID만 허용한다. apply는 `--transition keep`이 필요하다.
사용자 승인 없는 필드, 로고/각주/번호/고정문구 변경은 allowlist 밖이면 거부한다.

`analyze`는 각 slot의 `paragraph_run_texts`를 제공한다. 같은 개수의 문단/run에 새
문자열을 대응시킨다. 예: `{"slot_id":"s01_sh4","paragraph_run_texts":[["새 제목"]]}`.
표 셀도 `paragraph_run_texts`를 사용한다. 혼합 크기·색·강조의 run을 합치지 않는다.
run/문단 추가, 동적 필드 변경, 개행/tab 삽입, stale 원본 SHA는 거부한다.
`paragraph_run_styles`는 직접 지정된 글꼴과 pt 크기도 제공한다. `null`은 inherited이며
기본 글꼴/크기를 추측해 넣지 않는다. 별도 지정 시 brief의 `values`는 역할→값 매핑이다.
예: `font_policy: {basis: "specified", values: {body: "Pretendard"}}`,
`font_size_policy: {basis: "specified", values: {title: 14, body: 12}}`.
이 값은 이번 작업에만 적용하는 확인 입력이며 원본에 자동 덮어쓰는 기능은 아니다.
실행 후 편집 대상의 텍스트를 제외한 XML 전체가 동일한지 검사한다. 살아 있는 원본
Master/Layout/theme/미디어/글꼴 파트의 bytes와 슬라이드 크기도 확인한다.
원본 notes는 bytes를 복제하고 새 슬라이드 역참조만 변경한다.

엄격 모드 v1에서는 차트를 그대로 보존한다. 기존 일반 fill의 chart_edits는 지원하지만
엄격 모드의 축·서식 동일성 검증은 아직 없으므로 차트 변경을 요청하면 명시적으로 거부한다.
일반 fill은 그대로 유지한다. 공유차트의 중복 슬라이드 편집 독립성, SmartArt 수정,
이미지 교체, inherited font의 실제 시스템 해석은 이 모드의 보장이 아니다.

## 검증과 개인정보

합성 fixture만 저장소 리뷰에 올린다. 실제 사용자 원본/샘플/민감 내용은 별도 승인 없이
공개 GitHub나 외부 AI에 전송하지 않는다. brief도 실제 값이 들어가면 private project에 둔다.
지원 runtime으로 원본과 결과 모든 페이지를 렌더하고 변경/고정 영역을 비교한다.
XML 서식 보존은 폰트 설치나 동일 줄바꿈을 보장하지 않는다. 글꼴 누락/대체와 렌더러
차이는 보고한다. OfficeCLI/PowerPoint가 없으면 native application 검증 미완료로 명시한다.
실제 회사자료 도착 전 합성 fixture 통과를 회사 원형 재현의 최종 승인으로 표현하지 않는다.

## Cloud-first와 다른 컴퓨터

제작 본체는 기존 클라우드 실행환경과 GitHub 소스/변경이력을 재사용한다.
신규 서버/계정/유료 API를 자동 도입하지 않는다. 입력은 project-relative 경로를
권장하고 repo-relative 폴더 구조를 유지한다. 실행 시 `presentation_brief.py ...
--check-environment`로 기존 준비 probe를 재사용해 Python 의존성, 제공된 runtime,
이번 작업의 `font_files` 또는 `font_families`, OfficeCLI 여부를 기록한다.
실행환경이 없으면 임의 글로벌 패키지를 설치/대체하지 않고 blocker를 보고한다.
font 파일 존재 확인은 등록/렌더의 대체 검증이 아니다. 지원 runtime 등록 후 별도로
전 페이지를 검수한다. 합성 예제는 다른 Linux root에서 동일 파트 바이트로 재현됐으나
Windows/macOS에서 실행하지 않았으므로 모든 OS 지원이라고 표시하지 않는다.
