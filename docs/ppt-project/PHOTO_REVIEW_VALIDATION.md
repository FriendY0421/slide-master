# 사진 복제 검토 기능의 공개 검증 범위

이 변경은 목적 선택·사진 관찰값 인계와 기존 structured 변환기를 잇는 project-private 검토 경로다. 사진을 자동 인식하거나 원본 PowerPoint 구조를 회복하는 엔진이 아니다. 모든 공개 입력·이미지·수치·확인 근거는 **합성 fixture**이며 실제 사용자 승인으로 재사용할 수 없다.

## 검증 결과

공개 후보의 실행 로직은 최종 로컬 개선본과 동일하다. 공개 준비에서는 예제의 환경별 절대 경로를 placeholder로 바꾸고 실행별 원문 로그·receipt·작업 경로를 제외했다. 다음 검사는 공개 후보에서 각각 통과했다.

| 검사 | 통과 | 확인 범위 |
| --- | ---: | --- |
| 목적·사진 입력 계약 | 65 | 추천/선택 구분, SHA·출처·관찰값·schema·CLI·이전 v2 입력 호환 |
| 모델 배치→편집형 검토 연결 | 46 | 계획 차단 조건, glyph fit, SVG 입력 일치, 기존 합성 PPTX의 네이티브 readback·렌더 SHA |
| 모델 추정 검토 경로 | 38 | 추정과 사용자 승인 구분, 합성 교체 문구 공개, 폰트 사용권·파일·family 검사 |
| 원문·네이티브 스타일 보존 | 13 | 텍스트를 도형으로 바꾸는 손실 차단, 700.0 굵기, 누락된 run 크기, 입력·이미지 변경 감지 |
| 측정 폰트와 렌더 폰트 결합 | 14 | 정확한 경로·SHA 일치, 등록 누락·추가·오류 및 단계 중 파일 변경 차단 |

176개는 계약·readback·단계 제어 검사이며 실제 회사 사진 E2E 성공 횟수가 아니다. 네이티브 PPTX·PNG 검사는 이미 생성·렌더된 합성 대조 자료를 읽었다. 공유 finalizer·렌더의 새 실행은 반복하지 않았다. 단계 중 파일 변경을 검사할 때 변환·렌더 subprocess는 모킹했다. 실제 시험 스크립트와 실행별 산출물은 저장소 규칙에 따라 gitignored 작업 영역에만 보존했다.

runtime 계약 검사, Codex discovery stub 검사, 변경 Python 문법 검사, finalizer의 Node 문법 검사와 diff 공백 검사도 통과했다. 공개 이미지 네 개는 합성 원본과 bytes가 같고 EXIF·추가 메타데이터가 없다.

## 지원 입력으로 다시 확인하기

저장소 root에서 기존 준비된 Python으로 아래 명령을 실행한다. `--check`는 프로젝트·PPTX를 생성하지 않는다.

```bash
python3 .claude/skills/ppt-master/scripts/reference_intake.py .claude/skills/ppt-master/examples/photo_reference_intake/synthetic.png --observations .claude/skills/ppt-master/examples/photo_reference_intake/observations.json
python3 .claude/skills/ppt-master/scripts/presentation_brief.py .claude/skills/ppt-master/examples/photo_reference_intake/brief.json
python3 .claude/skills/ppt-master/scripts/photo_reconstruct.py .claude/skills/ppt-master/examples/photo_reference_orchestration/plan.json --check
```

실제 변환·렌더를 검토하려면 현재 호스트의 공유 Presentations skill을 먼저 읽고 지원 runtime·선택 폰트 파일을 확인한다. [연결 계약](PHOTO_MODEL_ORCHESTRATION.md)의 실행 절차를 따른다. 각 실행은 새로운 private workspace를 사용하며 공개 fixture의 확인 근거를 실제 사용자 입력에 복사하지 않는다. 완료 receipt의 `visual_source_comparison_pending:true`, `user_delivery_ready:false`는 원본 비교가 남았다는 뜻이다.

## 미실행과 운영 한계

실제 회사 사진의 관찰 인계·최종 원본 비교, 사진과 결과의 유사도, 실제 PowerPoint 앱 편집, 호스트 UI의 선택 표시·코드 호출·자료 전달은 미검증이다. 사진 원본 폰트·Master·theme 회복을 주장하지 않는다. 회전·복잡한 path·SmartArt·새 네이티브 table/chart·TTC는 현재 연결기의 지원 범위가 아니다.

이 변경은 의존 PR #10 위의 별도 Draft 검토용이다. main 통합, 운영 배포, ACTIVE 등록, 태그·릴리스, 플러그인 적용과 인증 변경은 수행하지 않는다. CI의 실제 실행 상태는 해당 PR에서 별도로 확인한다.
