# 파이프라인 속도 개선 full cold A/B 및 최종 통합 — 2026-08-01

- 실험 ID: `learning-strategies-full-agent-cold-ab-r2`
- 실행일: 2026-08-01 (KST)
- 주제: 인지과학이 밝힌 효과적인 학습 기술
- 순서: ABBA, 직렬, arm당 2회
- 기준군: `6c0bbe08ebe3ddfb7ea5a91a25ec4ed6f2c99830`
- 처리군: `0bb7a94f17da6c2890d4c8ef09f2e4faac2009bb`
- 최종 판정: **전체 처리군 REJECT_OR_REWORK — 안전한 계측·위생 변경만 선택 통합**

## 결론

처리군은 사전등록된 저분산 공동 1급 지표인 초기 Executor 입력량 30% 절감을 두 번 모두 달성하지 못했다.
첫 처리군은 execution packet이 발동하지 않아 기준군과 거의 같은 입력량이었고, 두 번째 처리군은 같은 조건에서
full Executor 참조를 선택해 139,082 bytes까지 증가했다. 두 처리군 모두
`visualization_declaration_not_empty`로 packet을 생성하지 못했다.

최종 산출물 품질은 네 실행 모두 통과했지만, 중간 QC non-pass가 각각 3/1/2/4건 기록되어
사전등록 observer 기준으로 네 실행 모두 `Comparable: NO`다. 따라서 벽시계는 진단값으로만 보고한다.
진단 벽시계도 처리군 중앙값 개선이 외부 전체 프로세스 기준 1.34%, 내부 telemetry 기준 5.83%에 그쳤고,
두 pairing의 방향이 서로 반대였다.

## 고정 조건과 cold 범위

- 동일 prompt: SHA-256 `9323f2ea38306b4d07bb0c6055be9b9280e2d98150d8ec9dab7ea533a31276ac`, 12,219 bytes
- 동일 fixture: SHA-256 `653e582c027ee1b7c20d25c10ac9a37055397901642f3f76ce32592fe84e2188`, 3,535 bytes
- 동일 승인 payload: semantic SHA-256 `6a1e2c2fa38d69e2b560b18b6ae874e2996cb4c7c617b05245f6d1045b83c71f`
- 8장, ppt169, narrative/editorial/free, 이미지·차트·노트 없음
- 실행마다 새 detached worktree, 새 project, 새 `codex exec --ephemeral`, 별도 `CODEX_SQLITE_HOME`
- multi-agent와 memory/history 비활성화, 기존 spec/SVG/PPTX 재사용 금지
- cold 의미: agent-context/artifact/process cold
- OS page cache와 provider prompt cache는 초기화하지 못함

## 실행별 결과

| Slot | Arm | Packet | Bootstrap unique files | Contract-adjusted initial | Telemetry | Full CLI proxy | Input tokens | QC non-pass | Rewrites | Final |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Control | N/A | 33,919 B | 33,919 B | 1,210,082.928 ms | 1,512,309.088 ms | 23,551,841 | 3 | 1 | PASS |
| 2 | Treatment | NOOP | 33,283 B | 34,404 B | 1,336,511.752 ms | 1,698,203.581 ms | 24,793,436 | 1 | 0 | PASS |
| 3 | Treatment | NOOP | 139,082 B | 140,322 B | 1,133,024.776 ms | 1,489,945.738 ms | 24,122,277 | 2 | 1 | PASS |
| 4 | Control | N/A | 34,328 B | 34,328 B | 1,412,399.674 ms | 1,719,065.065 ms | 23,380,624 | 4 | 3 | PASS |

`Contract-adjusted initial`은 실제 transcript에서 확인된 초기 planning representation, 필수 Executor 참조,
P01 시점까지의 필수 `spec_lock.md` read를 포함한다. Slot 1과 Slot 4는 initial planning load 자체가
P01 cadence read였기 때문에 unique 값과 같다. Slot 2와 Slot 3은 Markdown pair를 읽은 뒤 P01 lock을
한 번 더 읽어 각각 1,121 B와 1,240 B를 가산했다. P05 lock 재독은 이 열에서 제외했다.

### Bootstrap 판정

고유 파일 합만 사용해 처리군에 가장 유리하게 보더라도:

- Pair 1: 33,919 B → 33,283 B, **1.88% 절감** — 30% MCID 실패
- Pair 2: 34,328 B → 139,082 B, **305.16% 증가** — 30% MCID 실패
- Arm 중앙값: Control 34,123.5 B, Treatment 86,182.5 B — 처리군 **152.56% 증가**

사전등록 정의대로 P01 lock 재독까지 포함하면:

- Pair 1: 33,919 B → 34,404 B, **1.43% 증가**
- Pair 2: 34,328 B → 140,322 B, **308.77% 증가**
- Arm 중앙값: Control 34,123.5 B, Treatment 87,363 B — 처리군 **156.02% 증가**

따라서 `retain_treatment` 조건은 벽시계와 무관하게 실패한다.

### 벽시계 진단값

모든 실행이 observer 기준 non-comparable이므로 아래 값은 효과 추정치가 아니라 분산 진단이다.

| 지표 | Control median | Treatment median | 처리군 개선 | Pair 1 | Pair 2 |
|---|---:|---:|---:|---:|---:|
| Full CLI proxy | 1,615,687.077 ms | 1,594,074.660 ms | 1.34% | -12.29% | +13.33% |
| Internal telemetry | 1,311,241.301 ms | 1,234,768.264 ms | 5.83% | -10.45% | +19.78% |

- 10% directional speed MCID 미달
- 두 pairing의 방향이 반대
- 외부 시간은 JSONL/last/stderr 파일 timestamp 기반 proxy이며 정확한 process stopwatch가 아님

### 토큰 진단값

| 지표 | Control median | Treatment median | 처리군 변화 |
|---|---:|---:|---:|
| Input tokens | 23,466,232.5 | 24,457,856.5 | +4.23% |
| Derived uncached input | 327,800.5 | 338,432.5 | +3.24% |
| Output tokens | 72,345 | 74,188 | +2.55% |
| Reasoning output | 25,651 | 26,682 | +4.02% |

각 실행의 input token 중 약 98.6%가 provider cache hit로 기록되어, model/server-cache cold라고 볼 수 없다.

## 품질 가드

네 PPTX를 독립적으로 ZIP/XML 재검사했다.

| Slot | PPTX bytes | ZIP entries | Slide XML | Read errors | 다섯 전략 범위 | SHA-256 |
|---:|---:|---:|---:|---:|---|---|
| 1 | 53,806 | 52 | 8 | 0 | PASS | `a983adf5caa55409d238300d0d8ba9aeaaa3083728ec68d53162dde6ccc831bb` |
| 2 | 53,423 | 52 | 8 | 0 | PASS | `addf41e2dd17a196fc9b1c51cee4838d9dbf69d1b3592abfcbf9b934bddd34fa` |
| 3 | 52,064 | 52 | 8 | 0 | PASS | `18464e779fdac6dbe394057b9614df3002c10e73b356366e736c10ca28de2ec1` |
| 4 | 52,079 | 52 | 8 | 0 | PASS | `1ab03a6a763d550a41c6f88bc76af5fc73c424ed2999b57e43138454d8dc01d0` |

모든 실행에서:

- source/payload/HEAD/clean worktree 무결성 통과
- `validate_spec.py` PASS, 8 pages
- 마지막 SVG QC error 0, warning 처분 완료
- export 8/8
- `verify_deck.py --no-render` PASS
- 능동적 회상, 분산 학습, 인터리빙, 정교화, 이중 부호화 키워드 범위 확인

다만 observer는 중간 QC 실패도 comparability 실패로 처리한다. 실제 수정 루프와 CLI token 오류를 포함해
Slot 1/2/3/4가 각각 3/1/2/4 non-pass를 기록했으므로, 네 벽시계 모두 사전등록상 비교 불가다.

## 원인

1. **Packet 적격성 실패**
   - 처리군 2/2가 `visualization_declaration_not_empty`로 NOOP.
   - validator는 동시에 `0 §VII rows`를 보고했다.
   - 구조화된 visualization row가 0이어도 선언부 prose/icon 계획이 적격성을 막는다.

2. **Executor branch가 deterministic하지 않음**
   - Control 2/2: cheatcard
   - Treatment Slot 2: cheatcard
   - Treatment Slot 3: full `executor-base.md + shared-standards.md`
   - 동일 조건에서 처리군 bootstrap이 33 KB와 139 KB로 갈렸다.
   - 처리군의 speed 계약이 MUST가 아니라 MAY라 실행 선택이 모델에 남아 있었다.

3. **공통 실행 마찰**
   - observer 복사본은 `console_encoding` import를 위해 매번 수동 `PYTHONPATH` 복구가 필요했다.
   - `visual_review.py --pages`의 numeric/comma token 계약을 네 실행 모두 처음에 잘못 사용했다.
   - 이 두 항목은 코드 CPU보다 agent/tool 왕복을 늘리는 실제 병목이다.

4. **현재 comparability 규칙이 실제 rework를 전부 제외**
   - 최종 품질 실패와 중간 수정·잘못된 CLI token을 모두 같은 non-pass로 취급한다.
   - 다음 실험에서는 최종 품질 guard와 rework count를 분리하되, 이번 결과를 사후 변경해 구제하지 않는다.

## 최종 선택 통합

full treatment `0bb7a94f`는 로컬 `main`에 한 번 머지됐지만 원격에는
푸시되지 않았다. 최종 정리는 `origin/main`의 기준점 `6c0bbe08`에서
안전한 변경만 다시 적용하는 방식으로 수행한다. 전체 treatment 상태는
`backup/pipeline-speed-full-r2` 브랜치에 보존하고, 검증 완료 후 로컬
`main`을 선택 통합 브랜치로 교체한다. `origin/main`은 변경하지 않는다.

| 분류 | 원래 커밋 | 선택 통합 커밋 | 처리 |
|---|---|---|---|
| P0 계측과 A/B harness | `d65fa3a1` | `3cbc5d4a` | 보존 |
| route-first | `e642f5f6` | `3bb0ab26` | 보존 |
| route owner discovery | `43283375` | `74d3636c` | 보존 |
| runtime contract 문서 | `5e2a0de1` | `f58ee986` | 보존 |
| runtime contract 정렬 | `c76d6d47` | `d796a40f` | 보존 |
| benchmark 문맥 축약 | `398d77b2` | `178e033c` | 보존 |
| execution packet 구현 | `886ca880` | — | 제외 |
| packet 통합 조정 | `e458b055` | — | 제외 |
| packet runtime 축약 | `b618b7d8` | — | 제외 |
| 이전 조건부-GO 문서 | `d3d9eaed` | — | 폐기하고 이 문서로 대체 |
| 전체 treatment merge | `0bb7a94f` | — | 백업 브랜치에만 보존 |

선택 보존분의 의미는 **전체 슬라이드 생성 속도 개선 입증**이 아니다.
계측 기반, route-first로 불필요한 owner 로드 제거, 계약 드리프트 방지,
runtime에서 benchmark 상세를 치우는 독립적인 안전 개선으로 한정한다.
packet 구현을 제외한 뒤 `AGENTS.md`에 남아 있던 post-packet P01 문장도
제거해 계약을 일치시켰다.

## 한계

- arm당 2회라 population-level 통계적 우월성을 주장할 수 없다.
- OS page cache와 provider prompt cache는 통제되지 않았다.
- 전체 Office 렌더/contact-sheet를 네 arm 모두 수행한 것은 아니며, 선택 페이지 render와 구조 검증을 사용했다.
- 그럼에도 deterministic-byte MCID 실패와 packet 0/2 발동은 벽시계 분산과 무관한 명확한 reject/rework 근거다.

## 증거와 보존

저장소에 재현용 소형 증거를 함께 보존한다.

| 파일 | SHA-256 |
|---|---|
| `docs/handoff/evidence/2026-08-01-pipeline-speed-full-cold-ab/summary.json` | `98F32355780B31EA39F751FDD7EE141B8DAC432352174551243B696E544741E0` |
| `docs/handoff/evidence/2026-08-01-pipeline-speed-full-cold-ab/contract.json` | `21472199ED60DB19BB134E62CD696A74D2328F8A440E4CA6E0E84A1C6187FA3A` |
| `docs/handoff/evidence/2026-08-01-pipeline-speed-full-cold-ab/prompt.txt` | `9323F2EA38306B4D07BB0C6055BE9B9280E2D98150D8EC9DAB7EA533A31276AC` |
| `docs/handoff/evidence/2026-08-01-pipeline-speed-full-cold-ab/learning_source.md` | `653E582C027EE1B7C20D25C10AC9A37055397901642F3F76CE32592FE84E2188` |

대용량 원시 증거는
`C:\tmp\slide-master-full-cold-ab-evidence-r2`에 보존한다. 원본 최종
보고서 SHA-256은
`F6D80DCB8855E603E7EEA2C95D70F0516BF095459E2B511A3F51AD7B8B948DAC`다.
유효한 네 실행의 전체 프로젝트는 worktree 제거 전에 다음 ZIP으로
아카이브했으며, 각 ZIP은 최종 PPTX, SVG, spec, telemetry를 포함한다.

| 실행 | 아카이브 | SHA-256 |
|---|---|---|
| Slot 1 control | `artifacts/slot1-control.zip` | `1B6A12C88B10190FDC6A07B3399D593D2711C97F48FF98EB990E62949DB54D64` |
| Slot 2 treatment | `artifacts/slot2-treatment.zip` | `508F903CE56F822F628C4218BA6BB4283256A4A85EDF4A20A6F17D286B7CE514` |
| Slot 3 treatment | `artifacts/slot3-treatment.zip` | `DAD1E2CAAB7E8BD786B6DB3BEDCCF684FEAB704C2B80048925A5C844EC8FFC91` |
| Slot 4 control | `artifacts/slot4-control.zip` | `DA69302DEFD7DEF1A480A829E0E834658A52ED27B7EDFE1D94A61A5A08FE6D87` |

원시 `slot1r.jsonl`부터 `slot4.jsonl` 로그와 stderr/last 기록도 같은
외부 증거 폴더에 남긴다. 보고서에 기록된 기존 프로젝트 worktree 경로는
정리 후 복구 경로가 아니며, 위 ZIP이 정식 보존본이다.
