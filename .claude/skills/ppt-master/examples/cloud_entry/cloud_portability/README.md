# 합성 클라우드 경로 이동 검증

2026-10-07, 기준 source `58a25cede9ebbaf44cd76a216ae522cdc2caf7fb`. 기존 검토를 통과한 기능과 공개 샘플을 그대로 사용했다. 문서/검증 JSON만 추가하며 새 엔진/의존성/샘플 디자인을 만들지 않았다.

[재현 실행 안내](../../../../../../docs/ppt-project/CLOUD_REPRODUCIBLE_START.md)는 사라질 수 있는 임시 파일에 의존하지 않도록 실제 실행 Python/JavaScript를 포함한다. [검증 JSON](validation-summary.json)은 두 경로의 19개 검사, 공유 finalization receipt, 폰트/런타임 버전, PPTX 및 렌더 해시를 기록한다. 체크아웃/공급 runtime 절대경로는 placeholder로 치환했다. 최종 PPTX는 private scratch에 남기고 공개 기존 샘플/이미지는 변경하지 않았다.

- 기본 2장: [기존 공개 합성 장문 샘플](../korean_fit/README.md). intake/catalog/direct selection/init + 기존 review exporter 범위. 전체 main 생산 workflow가 아니다.
- 사용자정의 6장: [기존 공개 원본 보존 샘플](../../template_fidelity/README.md). 표준 init/import, 별도 confirmed custom v2 brief + plan count/hash, native apply/exact readback, 공유 finalization/render 범위.
- 총 16장 렌더(각 경로 8장), 8쌍 픽셀 동일. 기존 공개 검토 이미지와도 8장 모두 픽셀 동일. primary 8장 육안 검토에서 잘림/누락 glyph/변경된 표·차트 배치를 발견하지 않았다. relocated 결과는 픽셀 비교 근거이며 별도 native 앱 검토가 아니다.
- 기존 font bytes/라이선스 및 소스 차트·embedded workbook·표 보존. 기본 ZIP 파트 차이는 created/modified 시각만, native ZIP 파트는 기존 및 경로 간 모두 동일하다. 전체 ZIP SHA 동일성을 매 실행 강제하지 않는다.
- missing runtime/font, stale catalog SHA, missing brief SHA, mismatched count는 기존 gate가 중단했다. 설치/fallback/force 우회를 추가하지 않았다.

OfficeCLI 없음. native PowerPoint/Edit Data, 실제 두 PC, 실제 picker UI 표시, 비공개 전달, 실제 회사자료/사진/사설 폰트는 미검증이다. synthetic approval fixture를 실제 사용자 승인으로 간주하지 않는다. 부모 작업에서 전달받은 67 PASS는 기능 기준의 별도 검토 결과이며 이번 19×2 실행과 합쳐서 독립 테스트 총수라고 주장하지 않는다. main/플러그인/운영 상태는 변경하지 않았다.
