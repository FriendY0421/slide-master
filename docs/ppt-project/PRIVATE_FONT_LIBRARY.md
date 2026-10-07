# 비공개 글꼴 보관함과 요청별 확인

글꼴 보관과 실제 설치·렌더 활성화는 별도다. 공개 저장소에는 schema와 허용된 합성/기존 배포
폰트의 검증 metadata만 둔다. 사용자 폰트 binary, 실제 Drive ID, 사용자 경로 mapping은 올리지 않는다.
다른 HOME 작업이 만든 보관함은 별도 사용자별 mapping으로 연결한다. 그 보관 완료를 이 클라우드의
폰트 활성화 완료로 표현하지 않는다.

## 사용자에게 보이는 구분

- **글꼴 보관함**: 사용자가 소유한 비공개 원본과 검증 기록의 보관 위치.
- **새 글꼴 추가**: 파일과 사용 라이선스를 받는 작업. 자동 설치나 공개 업로드를 의미하지 않는다.
- **사용 가능**: 필요한 endpoint에서 family/style/version/hash와 해당 사용권한을 확인한 상태.
- **라이선스 확인 필요**: 파일이 있어도 cloud 사용·복제·embedding 범위가 확인되지 않은 상태.

이 문서는 위 메뉴의 연결 계약이다. 실제 대화형 보관함 UI를 이번 작업에서 표시하거나 설치하지 않았다.
상시 감시·자동 설치는 없다. 다음 PPT 요청 때마다 registry/시스템 파일과 private cache를 다시 확인한다.
한글 localized family와 별칭은 실제 내부 이름 또는 확인된 private metadata에서 찾는다.
Unicode/공백 정규화로 ‘견고딕·궁서·바탕’ 같은 한글 요청도 후보를 찾는다.
일반 ‘고딕/견고딕’은 특정 폰트로 자동 확정하지 않는다. 여러 vendor/face/version이 있으면
실제 후보 미리보기와 첫 확인이 필요하다. private index의 `personal_aliases`에 사용자 확인과
정확한 SHA가 기록된 개인 별칭만 다음 요청에 재사용한다. search_aliases는 검색용이며 승인이 아니다.
같은 파일명이라도 다른 hash/version이면 같은 글꼴로 자동 대체하지 않는다.
registry의 `verification_level`은 파일명·크기 후보(`filename_size_candidate`)와 실제
원본 바이트·내부 metadata를 읽은 `hash_verified`를 구분한다. 후보는 available로 올리지 않는다.
TTC는 정확한 face/renderer 지원 확인이 필요하고 FON은 현재 cloud 지원 미확인이다.
현 cache inspector는 TTF/OTF만 받으며 임의 변환·설치하지 않는다.

## 요청마다 확인하는 데이터

`workflow_version: 2` brief에서 `font_requests`로 실제 필요한 face를 선언한다.
원본 기준이면 원본의 직접 지정 family/pt와 theme/inherited 구분부터 확인한다. 상속값을 추측하지 않는다.
이미지에서 추정한 글꼴·pt는 추정값을 표시하고 사용자 확인 또는 지정값을 받는다.
`font_matching`에 confidence, selected family/style/hash, 실제 후보 preview 파일/hash,
그 preview에 사용한 rendered_font_sha256, 허용된 사용권, preview_reviewed,
user_confirmed와 similarity_approved를 기록한다. 확정되지 않은 후보는 자동 사용하지 않는다.
신뢰도가 높아도 동일 원본 폰트/pt의 증거가 아니며 actual_render_match_verified는 별도다.
이미 사용자 지정 글꼴을 확인했다면 후보를 고르라는 질문을 반복하지 않는다.
원본 명시 폰트가 없으면 파일 추가를 요청하거나 실제 승인된 유사 폰트만 사용한다.

```json
{
  "endpoint": "cloud",
  "font_requests": [{"family": "Pretendard", "style": "Regular"}],
  "font_cache_roots": ["../private-fonts/pretendard-entry"]
}
```

`presentation_brief.py ... --check-environment`는 binary의 family/style/version/SHA256을 확인한다.
Windows는 기존 읽기 전용 registry probe와 시스템 font 파일 경로도 조회한다. registry 이름 또는
파일명이 존재한다는 사실만으로 실제 face/version/hash를 검증했다고 하지 않는다.
파일·정확한 face·권한을 확인하지 못하면 폰트 파일과 라이선스를 요청하며 대체하지 않는다.
직접 제공한 파일은 `font_license_review`의 reviewed, cloud_use, copy, embedding 범위와
`evidence_file`/`evidence_sha256`/`font_sha256`의 바이트 연결을 확인한다. private cache는 저장 당시
라이선스 증거를 함께 보존하고 재검증한다. 복제는 cache 저장 전에 반드시 allowed이어야 한다.
embedding의 allowed/denied/unknown은 별도 표시한다. 현재 도구는 PPTX에 폰트를 embedding하지 않는다.
OS/2 fsType은 기술 정보이며 라이선스 검토를 대신하지 않는다.

## 받은 폰트를 재사용하기

1. `private_font_cache.py inspect <폰트파일>`로 정확한 metadata를 읽는다.
2. 사용자 재사용 허용과 해당 파일의 라이선스를 확인한다. 제공자가 사용자라는 이유만으로 허용하지 않는다.
   확인 정책은 각 파일 hash 및 라이선스 증거 hash에 연결하며, 실제 내용은 private 작업공간에 둔다.
3. 사용자 소유 private 원본 경로와 각 endpoint의 project-private cache 경로를 지정한다.
4. 승인한 파일과 라이선스만 복사한다. 기존 cache는 덮어쓰지 않고 `verify`/`sync`로 재사용한다.
   새 글꼴은 새 entry root에 저장하고 사용자별 비공개 library index에 추가한다.
5. 렌더 담당자가 cache manifest의 상대 경로를 현재 root에서 찾아 지원 런타임에 등록한다.
   등록 후 실제 페이지 렌더·글꼴/오버플로 검수를 수행해야 활성화 완료가 된다.

```bash
python3 .claude/skills/ppt-master/scripts/private_font_cache.py store <폰트파일...> \
  --license-file <라이선스원문> --license-policy <확인정책.json> --reuse-confirmed \
  --owner-root <사용자private_entry_root> --endpoint-root <project_private_cache> --endpoint cloud
python3 .claude/skills/ppt-master/scripts/private_font_cache.py verify \
  --root <현재cache_root> --endpoint cloud
python3 .claude/skills/ppt-master/scripts/private_font_cache.py sync \
  --owner-root <현재private_entry_root> --endpoint-root <새project_private_cache> --endpoint local
```

라이선스 확인 정책은 최소 reviewed=true, copy=allowed, cloud_use=allowed(클라우드일 때),
embedding=allowed/denied/unknown, 정확한 evidence_sha256과 조건 기록을 갖는다.
검토된 라이선스가 해당 파일들에 적용되는지도 사람이 확인한다. SIL OFL fixture는 기존 원문을
읽고 저작권·라이선스 동봉, 단독 판매 금지와 reserved-name 조건을 유지했다. 실제 상용폰트의
라이선스를 OFL로 간주하지 않는다. 전체 OS 설치나 새 권한 요청은 수행하지 않는다.

`font-manifest.json`은 fonts/license 파일의 상대 경로, exact hash/metadata, 재사용 허용과 라이선스
검토를 담는다. 새로운 root를 전달하면 같은 파일을 찾고 재검증한다. `sync`는 로컬 private 파일
복사 기능이며 Drive에서 내려받는 연결은 구현하지 않았다. 폰트 수가 늘면 entry별 cache를
`font_cache_roots`에 연결한다. `font_library_file`과 현재 `font_library_root`를 제공하면
private registry의 hash_verified/available entry만 실제 cache 검증으로 연결한다.
파일명·크기 후보는 별도 목록으로 표시하고 사용하지 않는다. 실제 library index와 endpoint root mapping은
[사용자 비공개 library schema](../../.claude/skills/ppt-master/schemas/private_font_library.v1.json)를 따른다.
Drive backend/opaque ID는 private mapping에만 넣는다. 이 schema 자체에는 실제 사용자 ID가 없다.

## 현재 증거와 남은 연결

기존 배포 Pretendard Regular/Bold로 local/cloud endpoint label 검사, 버전/hash 불일치,
라이선스 미확인·cloud unknown·copy denied, 재사용 비동의, 경로 변경, 반복 sync,
cache 변조와 root 탈출 거부를 검사했다. 실제 테스트 머신은 Linux다. HOME-PC/Windows를
실행했다거나 Drive 보관 폰트를 다운로드·활성화했다고 주장하지 않는다.

[합성 회귀 결과](../../.claude/skills/ppt-master/examples/cloud_entry/current-intake-regression.json)를 참조한다.
실제 사용자별 private library mapping, 다음 요청의 승인된 파일 조회/다운로드, 해당 runtime 등록과
렌더는 남아 있다. 필요한 실제 font와 사용자별 private ID가 확정될 때 그 연결을 검증한다.
