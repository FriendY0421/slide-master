# 슬라이드 마스터를 클라우드에서 사용하는 방법

사용자는 **슬라이드 마스터 호출 → 기본/사용자정의 선택 → 자료·기준 확인 → PPT 받기**로 요청한다.
제작 도구와 검증 기록은 클라우드에서 처리한다. 내부 스크립트 이름을 사용자에게 입력시키지 않는다.
시작 메뉴는 기본 템플릿 / 사용자 정의 두 항목이다. 지원되는 선택 도구로 표시하고,
UI 기능이 없으면 표시했다고 주장하지 않는다. 이미 제공한 자료·선택·기준을 다시 묻지 않는다. 자료 검토 후 보여준 구성안에 대한 확인은 필요하다.

> 2026-10-06 점검: 이 문서와 작업별 입력·품질 개선은 PR #10의 리뷰 후보다.
> 연결된 플러그인 본문을 수정하지 않았다. main 통합이나 새 대화 자동 적용 완료를 의미하지 않는다.

2026-10-07 추가: [클라우드 재현 실행 안내](CLOUD_REPRODUCIBLE_START.md)에 동일 Linux의 두 checkout 검증과 남은 PC/native 앱 경계를 기록했다. 기능 소스는 58a25ce 기준 그대로다.

## 짧게 요청하기

**기본 모드**

> 슬라이드 마스터, 기본 모드로 첨부 자료를 임원보고용 3장 PPT로 만들어줘.
> 결론·실적·실행계획 순서로, 도형과 차트는 편집 가능하게 해줘.

템플릿을 아직 지정하지 않았으면 실제 등록 미리보기에서 선택한다. 제작 방식도 함께 확인한다.
템플릿 선택 후 글꼴·글자 크기·장수·기본 작성 기준의 빠진 값을 한 번에 확인한다.
선택과 자료가 충분하면 구성안을 바로 보여주고, 사용자가 그 구성안을 확인한 다음 제작한다.
‘기본’이라는 말만으로 특정 디자인이나 Free Design을 자동 선택하지 않는다.

직접 지정하는 요청 예시:

> 슬라이드 마스터, 기본 모드. `deck:executive_boardroom`과 `executive_brief`로
> 첨부 합성자료를 3장 보고서로 만들어줘. 최신 외부 조사는 필요 없어.

위 ID는 점검일 main에서 확인한 예시다. 매 요청마다 최신 카탈로그에서 유효성을 확인한다.
이미 지정한 선택값은 갤러리·프리셋 질문을 반복하지 않고 기록한다. 구성안 확인은 별도다.
2차 디자인 개선 예시를 등록된 템플릿 ID인 것처럼 부르지 않는다.

**사용자정의 모드**

> 슬라이드 마스터, 사용자정의 모드. 첨부 원본 또는 예제 PPTX에 이번 자료를 3장으로 채워줘.
> 글꼴·크기·로고·여백·작성 기준은 원본 유지. 참고 샘플은 없음.
> 바꿀 페이지와 텍스트·표 영역을 먼저 보여줘.

사용자정의는 템플릿 또는 예제를 먼저 받는다. 예제 PPT만 있어도 원본 배치·테마·스타일을
검토할 수 있다. 사진·스크린샷·PDF도 참조 입력으로 받을 수 있다. 원본·내용·글꼴/크기·장수·작성 기준이 모두 제공됐다면 같은 질문을 반복하지 않는다.
빠진 필수 항목만 한 번에 묻는다. 기본 템플릿이나 제작 프리셋을 추가로 고르게 하지 않는다.
원본 페이지와 편집 영역의 계획을 확인한 뒤 native PPTX로 채운다.
PPTX의 엄격 원본 보존 v1은 텍스트·표 셀만 바꾸고 차트를 그대로 유지한다.
POTX는 실제 Master/Layout 추출 후 확인한 정규화가 필요하다. 사진/PDF는 편집 가능한
도형·텍스트로 참조 재구성한다. 픽셀·원근/크롭·인식한 텍스트·화면비를 확인하고, 정확한
폰트/pt를 모르면 추정값으로 표시해 확인한다. 보관 글꼴의 실제 후보 미리보기·사용권·렌더
근거와 추정 신뢰도(`font_matching.confidence`), 사용자 선택·유사 글꼴 승인을 함께 기록한다.
파일명·크기만 일치하는 후보는 자동 사용하지 않는다. 원본과 동일하다고 단정하거나 raster를
배경에 붙인 결과를 완전 편집 가능 재현이라고 부르지 않는다.
다른 글꼴/크기를 요청하면 자동 덮어쓰기 대신 해당 작업의 스타일 변경 범위를 먼저 해결한다.

## 클라우드 실행 담당자가 연결할 단계

1. `FriendY0421/slide-master`의 최신 승인 main SHA, guard, routing, 카탈로그와 실행 계약을 읽는다.
   리뷰 브랜치를 승인 소스라고 취급하지 않는다. FAH 현재 권한 판정은 외부 연결의 별도 확인 사항이다.
2. 요청에서 `workflow_version: 2` 작업별 brief를 만든다. `presentation_brief.py`의 missing 항목만 함께 질문한다.
   이 검사는 입력완전성 검사이며 제작 승인을 만들지 않는다.
3. 기본 모드는 `template_gallery_chat_manifest_v2.py --source github`로 최신 등록 디자인을 읽는다.
   실제 대화형 UI가 가능하면 그것을 먼저 사용한다. 불가능하면 이유를 기록하고 지원되는 실제 미리보기
   표면을 사용한다. 클라우드에서 노트북의 Desktop Commander 실행을 필수 조건으로 만들지 않는다.
4. 확정된 기본 선택은 아래 명령으로 기록한다. `--expected-source-commit`에는 미리보기에 사용한
   manifest의 `source_commit`을 전달한다. main이 바뀌면 미리보기를 다시 확인한다.
   직접 지정한 경우에만 `--direct-template`을 사용한다. 추천 선택은 대신 실제 `--picker-evidence`가 필요하다.

   ```bash
   python3 .claude/skills/ppt-master/scripts/record_template_choice_v2.py <선택ID> \
     --source github --expected-source-commit <manifest_SHA> --preset <프리셋ID> \
     --confirmed --direct-template --output <선택기록.json>
   ```

   `--confirmed`는 실제 사용자 확인 후에만 지정한다. `--source local` 기본값은 기존 오프라인/재개 호환용이며
   새 회사자료 제작의 최신 승인 소스 확인을 대신하지 않는다. 과거 fixture 선택 기록도 재사용하지 않는다.
5. 기본 모드는 선택 후 자료를 분석하고 전 페이지 구성안을 보여준다. 현재 구성안의 실제 승인 기록과
   선택 기록 둘 다 있어야 초기화한다. 이후 main SVG owner의 제작·QA 절차를 따른다.

   ```bash
   python3 .claude/skills/ppt-master/scripts/new_deck_init.py <프로젝트명> \
     --template-selection-result <선택기록.json> --storyline-approval-result <구성승인.json> --design-brief <작업brief.json>
   ```

6. 사용자정의 PPTX는 `ppt-template-fill` owner로 들어간다. 사진/PDF는 참조 재구성 owner의
   분석·확인·project-private 템플릿 핸드오프가 필요하며, 이번 감사는 생성까지 연결됐다고 주장하지 않는다. 직접 PPTX exemption, source SHA,
   원본 분석, 편집 allowlist, 실제 확인한 fill plan을 기록한다. native apply/validate는 별도 `analysis/design_brief.json` 또는 `--design-brief`의 확인 장수를 읽는다. plan의
   `requested_slide_count`만으로 장수 확인을 대신하지 않는다. 확인된 workflow_version 2 custom brief와 plan의 `requested_slide_count`·`task_brief_sha256`은 모두 필수이며 기존 재개에도 생략할 수 없다. 계획·출력 장수도 read-back으로 확인한다. 기존 native apply·read-back·OfficeCLI·렌더 gate를 따른다.
   main SVG의 선택·초기화·QA 도구를 이 경로에 강제로 적용하지 않는다.
7. local/cloud 각 endpoint에서 요청한 font family/style/version/hash를 확인한다. 없다면
   폰트 파일·라이선스를 요청하며 조용한 대체를 하지 않는다. [비공개 폰트 재사용 계약](PRIVATE_FONT_LIBRARY.md)을 따른다.
   제공된 런타임·글꼴 파일을 확인하고 지원 경로로 렌더·시각검수한다.
   한글 장문은 [실제 glyph 사전 측정과 최종 렌더](KOREAN_TEXT_FIT_EVIDENCE.md)를 함께 확인한다.
   넘치면 사용자와 요약/분할을 확인하며 조용한 축소·삭제·장수 변경은 하지 않는다. 공유 Presentations runtime으로
   실제 PPTX를 검사할 때는 해당 skill을 먼저 읽는다. 사용자정의 owner의 OfficeCLI 검증 누락을
   공유 렌더 성공으로 지우지 않는다. 누락 시 최종 검증 미완료로 알린다.
8. QA를 통과한 정확한 파일을 호스트의 다운로드/Library 전달 기능으로 제공하고 전달을 확인한다.
   실제 회사 원본·내용은 비공개 작업공간에 둔다. 공개 GitHub 링크는 합성 리뷰 자료에만 사용한다.

## 어디까지 연결됐는가

| 단계 | 확인한 연결 | 남은 사항 |
|---|---|---|
| 호출·모드 입력 | repo guard/router와 작업별 brief가 기본/custom을 구분 | 연결된 플러그인의 새 대화 자동 실행은 미검증; PR 개선도 미통합 |
| 승인 소스·선택 | GitHub main 조회, immutable SHA로 catalog/preset 읽기, ACTIVE만 선택; SHA 변경 시 거부 | 호스트의 실제 UI 표시·클릭값 전달은 이번 감사에서 실행하지 않음 |
| 입력·승인 | 기본 선택+프리셋+storyline, custom 입력+native plan gate; 빠진 항목만 질문 | 실제 회사 템플릿·승인은 제공되지 않음; 이미지/PDF 전체 재구성 생성은 계약·합성 입력 검사 단계 |
| 제작 | 기존 SVG→DrawingML 및 native fill; 별도 한글 장문 2장 합성 PPTX 생성 | 실제 입력부터 호스트 전달까지 새 전체 제작은 미실행 |
| 품질 | 기존 합성자료와 별도 장문 2장의 공유 runtime 렌더·검수, native 표·텍스트 확인 | 이 클라우드에 OfficeCLI 없음; 실제 PowerPoint 열기/Edit Data 미검증 |
| 새 디자인 선택 | 2차 3장 디자인은 별도 리뷰 예시로 저장 | 승인된 재사용 템플릿 패키지 및 ACTIVE 카탈로그 등록 미완료 |
| 전달·다른 PC | 공개 합성자료로 동일 Linux의 두 checkout 경로 생성·readback·공유 렌더를 검증; 8쌍 픽셀 동일 | 비공개 다운로드/Library 전달 및 같은 계정의 다른 PC 새 대화까지 검증하지 못함 |

수신 PC의 글꼴은 별도다. HOME-PC에 PowerPoint가 있다는 확인은 받았지만 Pretendard가 없었다.
클라우드 렌더 성공이 수신 PowerPoint에서 같은 줄바꿈을 보장하지 않는다. 임의 설치·대체는 하지 않는다.

## 이번 검증의 범위

[합성 입력·선택 evidence와 감사 결과](../../.claude/skills/ppt-master/examples/cloud_entry/README.md)를 확인한다.
입력부터 선택·승인 gate·초기화까지의 연결과 실패 차단을 실행했고, custom 원본 분석·계획 검사를 실행했다.
이전 검토된 PPTX/QA 증거와 전달 파일을 연결해 확인했으며 **새로운 한 번의 전체 제작·렌더·전달 성공으로 표현하지 않는다**.
main 통합은 별도 승인, 카탈로그 등록은 실제 후보 검토·승인, 전달은 지원 호스트에서의 파일 전달 확인이 남아 있다.

별도 [한글 장문 2장 검증 자료](../../.claude/skills/ppt-master/examples/cloud_entry/korean_fit/README.md)는 실제 glyph 측정과 최종 PPTX 렌더를 연결한 합성 기술 검증이다. 사용자 자료 제작·전달이나 실제 사진 재구성 완료를 뜻하지 않는다.
