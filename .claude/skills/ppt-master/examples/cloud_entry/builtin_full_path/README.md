# 기본 SVG 전체 경로 합성 검증

2026-10-07, 실행 source SHA `07c781d53f1eb327671af0d2ed9f4cb8ac9bd425`. 승인 main/catalog SHA는 `0578dba7ddf56cf5d7024cf574063c4db7332a3e`이며 둘을 구분했다. 등록 `deck:executive_boardroom` 패키지는 두 SHA에서 동일하다. 그 패키지와 `executive_brief`, 기존 공개 합성 KPI 84/90, 저장소 OFL Pretendard Regular/Bold로 1장 engineering fixture를 만들었다. 새 템플릿 등록이나 운영 변경은 없다.

[최종 합성 PPTX](review/builtin-full.pptx), [전체 최종 1장 렌더](review/slide-1.png), [단계/버전/해시/검증 receipt](validation-summary.json).

기존 korean_fit 템플릿 복사 + review exporter 시험은 반복하지 않았다. 이 실행은 `new_deck_init → import-sources → registered template → design_spec/spec_lock → validate_spec --strict → hand-authored svg_output → P01/full SVG QA → verify-charts → svg_to_pptx --native-objects → verify_deck → supported shared finalization/render`다. `--visual-only`, review exporter, `-s final`, `--no-render`를 사용하지 않았다.

| 단계 | 실제 결과 |
| --- | --- |
| 저장소 guard/local FAH fallback/routing | 지침 확인, 기존 합성 gate fixture 검증; live FAH ALLOW 조회·인증은 하지 않음 |
| init/표준 import | 종료 0; complete licensed-font v2 brief, count1, `--move` 입력 |
| preflight | 종료 0 + 경고 4개: Flask, requests, 시스템 Pretendard, OfficeCLI |
| planning + validate_spec --strict | 1장, §VII 1행, 오류·경고 0 |
| live preview | 실패: `ModuleNotFoundError: No module named flask`; UI 표시 주장 없음 |
| P01/전체 SVG QA | 최종 오류·경고 0; 초안 fallback hash 경고를 기존 helper로 해결 |
| verify-charts | 두 calculator 결과가 0–100 축의 84/90 bar geometry와 일치 |
| 정상 exporter | 종료 0; 1 Master/1 Layout/8 Layout atoms/3 slots, 1 native chart/workbook. editable-first 정규화 경고는 별도 유지 |
| verify_deck | 최종 종료 0. planning/SVG 내부 재호출은 최신 clean stamp로 생략됨; 새 PASS 실행으로 중복 계산하지 않음 |
| 공유 finalizer/render | 정확한 candidate bytes 유지, 1장 전부 렌더·개별 시각 검수 |
| OfficeCLI/네이티브 PowerPoint | 미실행; exported contact sheet 자동 생략. 공유 렌더는 네이티브 앱 검증을 대체하지 않음 |

첫 공유 렌더에서 chart가 기본 파랑/주황으로 나온 fixture 작성 오류를 발견했다. 문서화된 `style.colors`에 기존 팔레트를 넣어 재출력했다. 수정은 합성 SVG payload만이며 기존 엔진 결함이나 소스 수정으로 보고하지 않는다. 최종 native chart cache와 workbook B2/C2가 84/90이고, 테마 accent2/accent3이 B38B3F/315E52로 연결된 것을 확인했다. 최종 1장에 한글 누락·잘림·오버플로를 발견하지 않았다. 이것은 새 디자인 상품의 품질 승인이나 장문/모든 템플릿/긴 덱 coverage가 아니다.

`confirmed`/`approved_by: user`는 기존 합성 test fixture 형식이다. 실제 template/preset/storyline/Strategist UI 확인, 실제 회사자료·개인 사진·사설 글꼴, 두 PC, Edit Data, 비공개 전달은 미실행이다. 사용자의 실자료 승인으로 재사용하지 않는다. local FAH 계약을 읽었고 FAH/HDM/Weather 저장소·실운영 endpoint·credential에 접근하지 않았다. 폰트 설치·새 의존성·플러그인 변경·main 병합·배포 없음.

## 기록된 합성 출력을 재현하는 순서

현재 공급 runtime과 공유 Presentations skill을 먼저 읽고 사용한다. 아래는 기존 손작성 SVG를 재실행하는 engineering replay이며 새로운 LLM authoring/실제 사용자 승인/UI 동작의 재시험이 아니다. 운영 요청에서는 실제 최신 catalog와 사용자 확인을 새로 기록한다.

1. 현재 source와 catalog SHA를 별도로 기록한다. 고정 replay의 선택/구성은 부모 디렉터리의 `selection-fixture.json`, `storyline-fixture.json`이다. current main과 해당 registered source bytes의 일치가 깨지면 중단하고 재검토한다.
2. `new_deck_init.py builtin_full_replay --dir <NEW_EMPTY_SCRATCH> --template-selection-result <SELECTION_FIXTURE> --storyline-approval-result <STORYLINE_FIXTURE> --design-brief <THIS_FOLDER/task-brief.json>`을 실행한다. initializer가 반환한 날짜 접두어 경로를 `<PROJECT>`로 사용한다.
3. `facts.md`의 임시 복사본을 만든 뒤 `project_manager.py import-sources <PROJECT> <TEMP_FACTS> --move`로 들인다. 공개 원본을 이동하지 않는다. `preflight.py` 경고와 실제 막힌 항목을 기록한다.
4. registered Executive Boardroom workspace를 구조 검사한 뒤 모든 대상 충돌을 먼저 확인하여 `templates/`/존재하는 images/icons를 작업별 peer roots로 설치한다. 이 fixture의 design_spec/spec_lock을 프로젝트 루트에 둔다. `validate_spec.py <PROJECT> --strict`가 0 오류/경고여야 한다.
5. spec_lock을 읽고 기록된 `svg_output/01_합성_KPI_점검.svg`를 프로젝트 svg_output에 둔다. 실제 이번 실행에서는 주 에이전트가 단일 페이지를 직접 작성하고 P01 gate 후 전체 gate를 별도로 실행했다. replay는 동결된 손작성 페이지를 읽는 단계다.
6. `svg_quality_checker.py <PROJECT>`와 아래 calculator를 실행한다. notes/images 없음, svg_final deferred는 적용 조건이 없어 실행하지 않은 단계다.

```bash
"$CODEX_PRIMARY_RUNTIME_PYTHON" .claude/skills/ppt-master/scripts/svg_position_calculator.py calc bar --data '현재:84' --area '180,520,420,610' --bar-width 120 --value-range '0,100'
"$CODEX_PRIMARY_RUNTIME_PYTHON" .claude/skills/ppt-master/scripts/svg_position_calculator.py calc bar --data '목표:90' --area '350,520,590,610' --bar-width 120 --value-range '0,100'
```

7. `svg_to_pptx.py <PROJECT> --native-objects` 후 `verify_deck.py <PROJECT>`를 실행한다. verify의 cached/skipped 단계와 optional OfficeCLI 미실행을 숨기지 않는다.
8. 공유 Presentations finalizer를 별도 candidate/final 경로, count1, native chart/workbook owner1, 12192000×6858000 EMU, design font policy Pretendard로 실행한다. 현재 supplied RUNTIME_*만 사용한다. renderer profile에 실제 저장소 Regular/Bold OFL 파일을 작업별 상대 경로로 넣고 기존 `examples/korean_business/render_review.mjs`로 모든 최종 페이지를 렌더/검수한다. 이 파일의 exact final receipt와 render/font hashes는 validation-summary.json에 있다. actual PowerPoint 검사 완료로 표기하지 않는다.
