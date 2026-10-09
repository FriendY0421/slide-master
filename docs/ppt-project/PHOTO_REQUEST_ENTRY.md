# 요청과 선택 결과를 사진 검토 생성 경로에 연결하기

`presentation_request.py`는 실제 요청을 기존 task intake와 사진 검토 owner에 넘기는 로컬 실행 진입점이다. 새 생성 엔진·OCR·호스트 UI가 아니다. 이 소스만 준비했다고 설치된 플러그인이나 대화 메뉴가 연결됐다고 표시하지 않는다.

## 목적과 선택 근거

일반 PPT 요청은 **원본 그대로 복제 / 기존 자료 수정·보완 / 템플릿으로 새로 제작**의 세 가지 `purpose_menu_contract`를 반환한다. 호스트가 이 값을 실제 지원 UI로 표시하고 현재 선택 이벤트를 아래 인자로 돌려준다. UI를 표시하지 않은 CLI 결과는 `actually_rendered:false`다.

```bash
python3 .claude/skills/ppt-master/scripts/presentation_request.py <task-brief.json> --request-text 'PPT 만들어줘' --request-ref <actual-request> --state-file projects/<private-request>/session.json --output <request-intake.json>
python3 .claude/skills/ppt-master/scripts/presentation_request.py <task-brief.json> --request-text 'PPT 만들어줘' --request-ref <same-request> --state-file projects/<private-request>/session.json --purpose-choice copy_original --purpose-confirmation-ref <actual-current-selection-event> --selection-context-sha256 <returned-menu-context> --output <request-intake.json>
```

`복제해줘`, `똑같이`, `원본 그대로` 등 지원되는 직접 명령은 현재 사용자 메시지 근거인 `--request-ref`가 있을 때 그 메시지 자체를 원본 복제 선택으로 사용한다. 이미 명시한 목적을 다시 묻지 않는다. 긴 표현·질문·부정문을 단순 키워드로 승인하지 않는다. 호스트가 명확한 실제 요청을 판단했으면 `--purpose-choice copy_original --purpose-confirmation-ref <actual-message>`로 전달한다. 추천만 있는 요청에는 승인값을 만들지 않는다. 세 선택 중 수정·보완과 원본 복제는 custom 참조로 연결하며 builtin 충돌을 거절한다. 새 제작은 기존 builtin/custom 선택과 해당 owner의 gate를 계속 따른다.

## 선택의 취소와 입력 변경

새 호출은 brief에 남은 이전 `purpose_*` 승인값을 자동 재사용하지 않는다. 호스트의 실제 callback 경로에는 요청별로 하나의 private `--state-file`을 사용한다. 현재 메뉴의 `request_entry.selection_context_sha256`를 callback에 그대로 돌려준다. 메뉴 요청 ID와 실제 선택 이벤트 ID는 구분한다. 이 token은 요청 ID·입력 설정·첨부 파일 bytes·관찰 파일 bytes·revision을 묶으며 호스트 이벤트 인증을 대신하지 않는다.

동일한 현재 입력·요청에만 session 선택을 유지한다. 다른 이미지, 같은 경로의 변경된 이미지 bytes, 관찰값, 장수·폰트·내용 설정, 새 요청 ID는 이전 선택과 callback token을 무효화한다. `--cancel-selection` 또는 지원되는 명확한 취소 명령은 revision을 바꾸고 선택을 폐기한다. 취소 이전 callback은 재사용하지 못한다. 취소된 직접 요청의 같은 메시지 재전송도 다시 선택하지 않으며, 새 실제 메시지나 현재 revision의 명시적 선택만 허용한다.

현재 token으로 명시적 선택을 수락하면 revision을 올리고 응답에 새 token을 반환한다. 호스트는 다음 이벤트에 이 새 token을 사용한다. 그 뒤 새 선택 없는 resume은 최초 `복제해줘` 문구보다 session의 최신 명시적 선택을 우선한다. 이전 token의 중복·역순 callback과 현재 state에 맞지 않는 오래된 brief snapshot은 현재 선택을 변경하지 않고 거절한다. 실패한 callback 때문에 사용자에게 같은 선택을 다시 요구하지 않는다.

callback의 요청/입력 context와 현재 저장된 token을 검증한 뒤에만 변경 후보를 적용한다. 파일 state는 정상 처리 시에만 임시 파일 교체로 commit하며 예외에서는 원래 파일 bytes를 보존한다. 현재 입력 변경의 정상 intake가 새 revision을 만드는 것과 오래된 snapshot의 실패한 callback을 구분한다.

UI 취소 callback도 현재 token을 전달한다. 취소에 token이 제공되면 이를 검증하며, token 없는 현재 사용자 취소 명령의 인증은 호스트가 담당한다. 목적 선택 callback의 commit과 후속 생성 요청은 나눠 처리한다. 입력이 부족한 정상 intake JSON의 새 token도 반영하되, 예외로 거절된 callback에는 기존 선택/token을 유지한다.

동일 state 파일의 동시 요청은 잠금으로 차단한다. 성공한 같은 revision·model plan의 재호출은 실행 기록으로 막으며 이미 생성된 workspace를 덮어쓰지 않는다. 생성 도중 예외가 나면 session 변경은 rollback하고 기존 owner의 workspace/진단 자료를 먼저 확인한다. 실패한 시도의 state 기록을 자동 commit했다고 주장하지 않는다. 잠금 파일이 남은 비정상 종료는 호스트가 실행 종료를 확인한 뒤 복구해야 하며 이 CLI가 자동 삭제·재실행하지 않는다. state가 없는 호출은 명시적인 현재 요청의 단발 검사/실행용이며 호스트의 취소·중복 이벤트 처리를 대신하지 않는다.

## 사진 입력에서 편집형 검토본까지

호스트는 실제 이미지의 픽셀을 보고 [관찰 계약](PHOTO_ORIGINAL_RECONSTRUCTION.md)과 [모델 계획](PHOTO_MODEL_ORCHESTRATION.md)을 작성한다. 사용자에게 SVG나 내부 plan JSON 작성을 요구하지 않는다. `inputs_confirmed`, 참조 검토, 글꼴/pt/장수/작성 기준과 실제 현재 선택 근거가 준비돼야 한다.

```bash
python3 .claude/skills/ppt-master/scripts/presentation_request.py <task-brief.json> --request-text '복제해줘' --request-ref <actual-current-message> --state-file projects/<private-request>/session.json --build-photo-review <model-plan.json> --workspace-parent projects/<private-request> --presentations-skill-dir <verified-shared-Presentations-skill> --output <entry-result.json>
```

이 opt-in 실행은 현재 intake를 검사하고 제공 runtime·폰트 사용권을 확인한다. 모델 plan에 선택 필드가 없으면 현재 선택값을 인계한다. 이미 있는 선택값/근거가 다르면 덮어쓰지 않고 차단한다. 현재 이미지 SHA 집합·관찰 sidecar·장수·선택 family·허용 pt값이 다르면 생성하지 않는다. 역할별 위치와 문자별 크기의 충실도는 관찰값과 모델 계획의 element 검증·최종 시각 QA가 담당한다.

현재 입력과 묶인 plan snapshot만 기존 `photo_reconstruct.build_review`로 넘긴다. 원문/관찰값을 유지하며 필요한 파일 경로만 절대 경로로 해석한다. 기존 structured compiler→native readback→공유 finalizer→실제 all-page render→폰트 SHA 결합 검사를 그대로 사용한다. 전체 사진을 배경으로 붙이는 출력은 편집형 재구성 성공으로 취급하지 않는다.

`analysis/request-entry.json`은 실제 선택 근거·입력/인계 plan SHA·effective brief SHA·최종 PPTX SHA를 묶는다. `request-intake.json`은 실행 전 조건, `effective-task-brief.json`은 이번 요청의 실제 적용값이다. 작업 자료와 로그는 private `projects/` 안에만 둔다. CLI 종료값 대신 JSON의 `ready_for_plan`, `environment.ok`, `request_entry.execution_performed`, `photo_review`를 읽는다. `ready_for_generation:false`인 intake를 일반 신규 덱 생성 허가로 해석하지 않는다.

## 실제 호스트 수용 검증

선택 상태의 세 회귀는 저장소 루트에서 `python3 -m unittest discover -s tests -v`로 실행한다. 합성 입력으로 원래 복제 문구의 resume, 소비된 token 재전송, 오래된 brief 거절 후 실제 state 파일 보존을 검사한다. 관련 PR/push의 CI도 같은 명령을 실행하며 private 검토 자료에 의존하지 않는다. 이 좁은 검사는 아래 실제 호스트 수용 검증을 대신하지 않는다.

이 후보를 운영에 연결하기 전에는 실제 일반 요청에서 세 목적을 표시하고, 선택 이벤트가 현재 요청 근거로 돌아오는지 확인해야 한다. 직접 복제 명령은 불필요한 목적/등록 템플릿 질문 없이 실제 사진 참조로 이어져야 한다. 호스트의 현재 관찰 계획 작성·이 CLI 호출·private 결과 전달을 실제 지원 경로에서 확인해야 한다. builtin/수정 경로의 기존 선택·계획 확인 gate도 유지해야 한다. FAH 판정을 요구하는 호스트는 해당 실제 판정을 별도로 통과해야 한다.

검토본은 원본 font/Master/theme 회복이나 동일 재현을 보장하지 않는다. 폰트·간격·원문·이미지·배치를 각각 최종 렌더와 원본으로 비교한다. 실제 사진 비교·다른 PC·PowerPoint·운영 통합·지원 UI/전달을 실행하지 않았다면 미검증으로 남긴다. 이 문서와 로컬 소스 후보는 운영 플러그인 변경·push·main 병합·배포의 승인을 대신하지 않는다.
