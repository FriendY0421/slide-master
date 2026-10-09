# 요청 선택 상태 회귀 검사

저장소 루트에서 실행한다.

```bash
python3 -m unittest discover -s tests -v
```

명시적으로 승인된 세 선택 상태 결함을 보호하는 좁은 회귀 검사다. 원래 복제 요청의 resume, 소비된 callback token의 재전송, 오래된 brief 거절 후 실제 state 파일 보존을 각각 독립 검사한다. 기존 요청 준비 함수와 파일 잠금·commit 경로를 실행한다.

합성 문자열과 최소 입력만 사용하며 임시 파일은 gitignored `projects/`에 만들고 정리한다. 외부 API, renderer, 회사자료, private 검토 묶음, 추가 패키지가 필요 없다. 이 검사 통과는 실제 호스트 UI/callback 인증·adapter·private 전달이나 PPTX 시각 품질의 검증을 의미하지 않는다.

`.github/workflows/request-state-regression.yml`이 관련 source/test 변경의 push와 PR에서 같은 명령을 실행한다. 호스트 연동과 광범위한 생성 검증은 별도 수용 검사 범위다.
