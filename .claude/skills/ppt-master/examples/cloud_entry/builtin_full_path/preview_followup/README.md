# 합성 fixture 미리보기 누락 의존성 후속 검증

2026-10-07 실행 source는 `b832fe90d3e5e90886955b3e45f7b69cff79e9d8`이다. 저장소는 이미 `.claude/skills/ppt-master/requirements.txt`에 `flask>=3.0.0`을 선언했고 root requirements가 이를 참조한다. [Flask 공식 설치 지침](https://flask.palletsprojects.com/en/stable/installation/)의 가상환경 방식을 사용했다. 기존 제품 결함 수정이나 새 의존성 선언은 필요하지 않았다.

공식 PyPI에서 Flask 3.1.3과 필요한 6개 의존성을 gitignored 작업 전용 venv에 설치했다. 순수 venv의 첫 서버 실행은 기존 converter package import가 요구하는 `pptx` 부재로 실패했다. 공급 runtime의 기존 라이브러리를 읽는 `--system-site-packages`로 재구성해 해결했다. 기존 runtime/global package는 수정하지 않았다. 재현용 [버전·wheel 해시 lock](requirements.lock)은 이 검증 환경만 대상으로 하며 production requirements를 대체하지 않는다.

기존 프로젝트의 post-export 재진입이므로 routing의 `live-preview.md` Step1대로 `--daemon --no-browser` plain mode를 사용했다. `--live`는 main Step6 auto-startup 전용이며 이번 실행의 `/api/config`는 `live:false`다. 원래 전체 생성 시험과 당시 Flask 실패 기록을 다시 쓰거나 새로운 전체 생성 PASS로 바꾸지 않는다.

| 항목 | 실제 결과 |
| --- | --- |
| 시작 | 종료0, `127.0.0.1:5050` 루프백, health 200/1장 |
| 페이지 | 기존 Chromium 151 + 공급 Playwright 1.57; index 200, SVG 실제 visible, 합성 제목과 KPI 84/90 확인 |
| 오류 | browser pageerror 0, HTTP >=400 응답 0 |
| 시각검수 | [브라우저 화면](preview.png) 개별 확인; 합성 1장 표시, 한글 누락·잘림 미관찰. Pretendard 일치/실사용 UI 승인 인증은 아님 |
| 종료 | UI Exit preview와 확인 버튼 클릭, shutdown 200; 이후 health 연결 거절, project lock 제거 |
| 보존 | 적용/주석 저장/재출력 없음. 기존 SVG bytes와 PPTX SHA 동일 |

[정확한 설치 출처·패키지 해시·브라우저 결과](validation-summary.json). 서버는 검증 후 종료했다. 원격 공개/포트포워딩/네트워크 설정/보안 설정 변경, 새 로그인/권한/약관, 회사·개인자료 사용은 없다. 실제 사용자 선택·승인, PowerPoint/Edit Data, 두 PC와 사설 전달은 여전히 미실행이다. 기존 requests/시스템 Pretendard/OfficeCLI 경고는 이번 Flask 준비로 해결했다고 주장하지 않는다.

## 재현 범위

공급 Python runtime과 기존 합성 프로젝트가 있는 저장소 root에서 실행한다. `PREVIEW_VENV`는 신규 gitignored 작업 경로이며 global 환경을 가리키지 않는다.

```bash
PREVIEW_VENV=projects/_smoke_builtin_full/preview-venv
"$CODEX_PRIMARY_RUNTIME_PYTHON" -m venv --system-site-packages "$PREVIEW_VENV"
"$PREVIEW_VENV/bin/python" -m pip --isolated install --index-url https://pypi.org/simple --only-binary=:all: --require-hashes -r .claude/skills/ppt-master/examples/cloud_entry/builtin_full_path/preview_followup/requirements.lock
"$PREVIEW_VENV/bin/python" .claude/skills/ppt-master/scripts/svg_editor/server.py projects/_smoke_builtin_full/20261007_builtin_full_path --daemon --no-browser
```

실제 launcher URL로 `/api/health`, `/api/slides`와 브라우저 `/`의 SVG 표시를 확인한다. 변경을 저장하지 않고 **Exit preview → 확인**으로 종료한다. health 연결 거절과 `<PROJECT>/live_preview/lock.json` 제거를 확인한다. 브라우저 사용이 불가능하면 페이지 표시를 PASS로 기록하지 않는다. CLI의 `server.py <PROJECT> --shutdown`은 같은 프로젝트의 idempotent 정리 수단이다.
