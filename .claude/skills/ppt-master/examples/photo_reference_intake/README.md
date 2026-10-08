# 사진 참조 입력 계약의 합성 fixture

모든 파일과 선택/확인 값은 신규 코드의 입력 계약을 시험하는 합성자료다. 실제 회사사진·사용자 승인·UI 표시·PPT 복원 성공 기록이 아니다. 실제 제작에 이 fixture의 confirmed/ref를 재사용하지 않는다.

[사용 계약](../../../../../docs/ppt-project/PHOTO_ORIGINAL_RECONSTRUCTION.md) · [공개 검증 요약](../../../../../docs/ppt-project/PHOTO_REVIEW_VALIDATION.md)

`synthetic.png`는 160×100의 새 합성 이미지다. `observations.json`은 원본 hash, 화면 영역/추정 화면비, 문구·pt·미확인 폰트·geometry의 source/certainty/editability 목표를 기록한다. `brief.json`은 사진 원본 선택과 별도 승인 근거를 결합하는 빈 양식의 합성 입력이다. 단일 사진 입력으로 요청한 count2의 intake만 점검하며 2장 출력이 생성됐다는 의미는 없다.

```bash
python3 .claude/skills/ppt-master/scripts/reference_intake.py .claude/skills/ppt-master/examples/photo_reference_intake/synthetic.png --observations .claude/skills/ppt-master/examples/photo_reference_intake/observations.json
python3 .claude/skills/ppt-master/scripts/presentation_brief.py .claude/skills/ppt-master/examples/photo_reference_intake/brief.json
```

intake가 ready_for_plan이어도 ready_for_generation은 false다. 회사파일·폰트 설치·네이티브 앱·호스트 UI·PPTX export/render·Library 저장을 실행하지 않았다. 기존 완료된 합성 한 장 PPT 시험도 반복하지 않았다. 실행별 원문 로그와 비공개 작업 경로는 공개 fixture에 포함하지 않는다.
