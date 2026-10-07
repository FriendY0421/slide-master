# 한글 실측·최종 렌더 검증

글자 수나 CJK 전각/0.58em 근사만으로 한글 장문의 최종 적합성을 확정하지 않는다.
[기존 OFL 폰트와 합성 검증 예시](../../.claude/skills/ppt-master/examples/cloud_entry/korean_fit/README.md)는
실제 glyph advance/ink bbox를 사전 측정하고, 기존 변환기의 최종 PPTX를 공유 Presentations/Skia로
렌더해 모든 페이지를 개별 확인했다. 실제 PowerPoint와 실회사 사진 재현은 검증하지 않았다.

## 실행 계약

`korean_text_fit.py`는 확인된 작업 brief의 family/role pt와 실제 font hash/사용권을 검사한다.
문단을 합치지 않고 어절과 영문·숫자·% 단위를 보존한다. 제공된 상자와 좌우/상하 여백,
pt 줄간격, 문단 전후 간격, 명시 자간으로 실제 폰트 폭과 잉크 높이를 측정한다.
넘치는 어절, 높이, 줄간 겹침, 누락 glyph를 보고한다. 글꼴 축소·텍스트 삭제·장수 변경을 하지 않는다.
수용이 안 되면 폰트/glyph 지원 또는 사용자 요약·분할·상자/간격 변경 확인이 필요하다.

```bash
python3 .claude/skills/ppt-master/scripts/korean_text_fit.py <fit-contract.json> \
  --brief <확인한 작업brief.json> --output <실측결과.json>
```

양성 사전검사가 최종 QA를 대신하지 않는다. 전체 PPTX 최종 렌더를 보고 원문·장수·객체·줄바꿈을
확인한다. native 표의 문단·강조 run은 OOXML에서도 원문과 대조한다. 원본 native fill의
혼합 서식·문단/run topology·spacing은 기존 fidelity 잠금으로 보존하며, 측정 때문에 평탄화하지 않는다.

현재 helper는 한 계약당 한 face/pt다. 혼합 native run은 별도의 최종 렌더 검사로 확인했다.
tracking은 명시 값을 보존한다. 분해 자모/combining 문자에 자간이 있으면 실제 shaping 검토가 필요하다.
Pillow의 실제 glyph 측정도 native PowerPoint 줄바꿈의 증명이 아니다. 실제 사진·기울어진 crop,
모호한 글꼴·pt·표/차트 구조는 아직 실사용 검증 대상이다.

## 확인한 공식 코드 근거

각 URL과 blob을 GitHub에서 읽어 확인했다. 실행 결과는 이 저장소의 합성 검증으로 구분한다.
외부 코드나 전체 엔진을 가져오거나 upstream을 merge하지 않았다.

- [ppt-master 한글 어절 측정, commit 2d72da6](https://github.com/hugohe3/ppt-master/blob/2d72da616cf9fa40d4dcaf59fd4c980ecf534b7d/skills/ppt-master/scripts/text_measure.py#L186-L315)
  (blob `11e2ae77d6690c2feb4bcf3102ba2320c004cbe7`): 문단별 어절 유지와 oversized 보고 원칙을 참고했다.
- [OfficeCLI overflow, commit 8d079c7](https://github.com/iOfficeAI/OfficeCLI/blob/8d079c777ed6bea35b922c3d893758d3c2081137/src/officecli/Handlers/Pptx/PowerPointHandler.ShapeProperties.cs#L3957-L4143)
  (blob `d69f323ee80d39680d6af478100e5c4b3b60d362`): 일부 autofit 상태는 크기 검사를 건너뛴다.
  이 검사만으로 최종 QA를 판정하지 않는다. 전달받은 `PowerPointHandler.Set.ShapeProperties.cs`
  경로 대신 실제 tree의 `PowerPointHandler.ShapeProperties.cs`를 확인했다.
- [Presenton capacity, commit 35bf442](https://github.com/presenton/presenton/blob/35bf44290f821323e003da854f78ffcb0e918167/servers/fastapi/templates/v2/certified_generation.py#L2375-L2510)
  (blob `37263277b98bdfa5baa1c3e926d1be2bab3c1d1b`): 0.58/0.62 문자폭 계수는 한글 실측으로 이식하지 않았다.
- [ppt-master 이미지 재구성 profile, commit 2d72da6](https://github.com/hugohe3/ppt-master/blob/2d72da616cf9fa40d4dcaf59fd4c980ecf534b7d/skills/ppt-master/workflows/profiles/image-to-pptx.md)
  (blob `32661630ec2df433b170bd627d686e540caa1502`): 원문·bbox·confidence·z-order·hash inventory와
  불명확한 영역의 중단, 전체 raster 평탄화 금지를 참고한다. 이 workflow 자체가 OCR 정확도 보장은 아니다.

fork의 한국어 폰트 override와 기존 배포 font 파일을 유지했다. 현재 예시의 최종 사용 font는
Pretendard로 확인했고, native text를 outline이나 전체 슬라이드 이미지로 바꾸지 않았다.
