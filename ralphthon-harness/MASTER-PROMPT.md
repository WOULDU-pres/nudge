# MASTER PROMPT — Ralphthon Harness

---

## 재진입 프로토콜 (새 세션 / 새 에이전트가 읽는 첫 번째 섹션)

**CHECKPOINT.json을 먼저 읽어라.**

```
if CHECKPOINT.json 존재:
  phase = CHECKPOINT.json → phase
  if phase == "init":        → Phase 1부터 시작
  if phase == "phase1":      → phase1.current_task 확인 → 이어서 진행
  if phase == "phase2":      → Phase 2 이어서 진행
  if phase == "phase3":      → Phase 3 루프 이어서 진행
                               phase3.current_score, experiment_count 확인
                               results.tsv 읽고 → 다음 실험
  if phase == "phase4":      → Phase 4 대시보드 이어서 진행
                               phase4.current_task 확인

if CHECKPOINT.json 없음:
  → 초기 상태로 생성 후 Phase 1부터 시작
```

**모든 단계 전환 시 CHECKPOINT.json을 업데이트하라.**
이것이 세션 간 연속성을 보장한다.

---

## 오케스트레이터 패턴

이 하네스는 **오케스트레이터 + 코더** 2계층으로 실행된다.

```
┌─────────────────────────────────┐
│  오케스트레이터 (너)            │
│  - 전체 흐름 관리               │
│  - 하네스 문서 읽기/해석        │
│  - CHECKPOINT 관리              │
│  - Phase 전환 판단              │
│  - Phase 2~3 직접 실행          │
│  - results.tsv 읽기/쓰기        │
│  - strategy_prompt.md 수정      │
│  - keep/discard 판정            │
├─────────────────────────────────┤
│  코더 (Codex CLI 등)            │
│  - Phase 1 코드 생성 전담       │
│  - 코드 수정/리팩토링           │
│  - 버그 수정                    │
│  - 오케스트레이터가 시킨 것만   │
└─────────────────────────────────┘
```

### 코더 사용법

코드를 생성/수정할 때는 Codex CLI를 사용한다:

```bash
# 단일 태스크 (코드 생성/수정) — output/은 하네스 바깥
codex exec --full-auto '<구체적 지시>' --workdir ../output/

# 큰 태스크 (background)
codex exec --full-auto '<지시>' --workdir ../output/ &
```

**코더 사용 규칙:**
1. 코드 생성/수정만 시킨다. 판단/결정은 오케스트레이터가 한다.
2. 한 번에 하나의 모듈만 시킨다. 전체를 한 번에 시키지 않는다.
3. 결과를 반드시 검증한 후 다음으로 넘어간다.
4. 실패 시 에러 메시지와 함께 재시도 지시한다.

### 코더 없이 직접 하는 것

- terminal로 `python scripts/run_simulation.py` 실행
- results.tsv 읽기/쓰기
- strategy_prompt.md 수정 (Phase 3)
- CHECKPOINT.json 업데이트
- keep/discard 판정

---

## 전체 흐름

```
CHECKPOINT.json 읽기
    │
    ▼ (phase에 따라 분기)
┌─────────────────────────────────────────────────────┐
│ Phase 1: 코드 생성                                  │
│   코더에게 모듈별로 위임                             │
│   모듈: llm → personas → agents → conversation      │
│         → evaluation → ralph → scripts → config      │
│   각 모듈 완료 시 CHECKPOINT 업데이트                │
│   전체 완료 → Phase 2로 전환                         │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│ Phase 2: 베이스라인 실행                             │
│   python scripts/run_simulation.py 직접 실행         │
│   결과 확인 → 실패 시 코더에게 수정 시킴             │
│   성공 → results.tsv 기록 → git commit               │
│   CHECKPOINT 업데이트 → Phase 3으로 전환             │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│ Phase 3: Autoresearch (최대 5회 실험)                │
│   LOOP (최대 5회):                                    │
│     1. CHECKPOINT 읽기 (이어가기 지점 확인)          │
│     2. results.tsv 읽기 (이전 실험 패턴 분석)        │
│     3. 가설 수립 → strategy_prompt.md 수정            │
│     4. git commit                                    │
│     5. python scripts/run_simulation.py 실행          │
│     6. 결과 추출 → keep/discard 판정                  │
│     7. results.tsv 기록                               │
│     8. CHECKPOINT 업데이트                            │
│     9. 다음 실험 (5회 완료 시 Phase 4로 전환)         │
│   5회 실험 후 자동으로 Phase 4로 전환                 │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│ Phase 4: 웹 대시보드                                  │
│   architecture/visualization-spec.md 참조             │
│   HeroUI v3 + Tailwind CSS v4 + Recharts             │
│   runs/ 데이터를 시각화하는 웹 대시보드 구현          │
│   완료 → CHECKPOINT 업데이트                          │
└─────────────────────────────────────────────────────┘
```

---

## CHECKPOINT 업데이트 시점

| 이벤트 | 업데이트 내용 |
|--------|-------------|
| Phase 1 모듈 완료 | phase1.completed_modules에 추가 |
| Phase 1 전체 완료 | phase → "phase2" |
| Phase 2 시뮬 성공 | phase2.baseline_score 기록, phase → "phase3" |
| Phase 2 시뮬 실패 | phase2.errors에 추가 |
| Phase 3 실험 완료 | experiment_count++, 점수/가설 갱신 |
| Phase 3 keep | keep_count++, current_score 갱신, consecutive_discards=0 |
| Phase 3 discard | discard_count++, consecutive_discards++ |
| Phase 3 crash | crash_count++ |
| Phase 3 역대 최고 | best_score/best_experiment 갱신 |
| Phase 3 5회 완료 | phase → "phase4" |
| Phase 4 모듈 완료 | phase4.completed_modules에 추가 |
| Phase 4 전체 완료 | phase → "done" |
| 세션 종료 전 | next_action에 "다음에 해야 할 일" 기록 |

---

## 읽어야 할 파일

### Phase 1 준비 — 설계 이해

```
1. architecture/system-overview.md       ← 전체 그림. 2-레벨 루프 구조.
2. architecture/ralph-loop.md            ← RALPH 내부 루프 (H→P→A→E→R→L) 상세.
3. architecture/autoresearch-loop.md     ← 외부 루프 (전략 프롬프트 진화) 상세.
4. architecture/execution-phases.md      ← Phase 1/2/3 실행 흐름.
5. architecture/tech-stack.md            ← Python, aiohttp, Pydantic. 기술 제약.
```

### Phase 1 준비 — 계약 & 시각화

```
6. contracts/product-contract.md         ← 완성품 사양. 뭘 만들어야 하는지.
7. contracts/schemas/*.json              ← JSON Schema. 데이터 구조.
8. architecture/visualization-spec.md    ← 대시보드 UI 상세 설계.
```

### Phase 1 준비 — 프롬프트 & 기준

```
9. prompts/*.md                          ← 7개 프롬프트 템플릿. 코드에 삽입할 원본.
10. criteria/evaluation-rubric.md        ← Judge 채점 기준 상세.
11. criteria/quality-gates.md            ← Phase별 통과 기준.
12. criteria/autoresearch-rules.md       ← keep/discard 판단 규칙.
```

### 참고 (필수는 아님)

```
13. examples/                            ← 예시 대화, 평가, 반복, 실험 로그.
```

---

## Phase 1: 코드 생성

위 문서를 읽은 후, 코더에게 모듈별로 위임한다.

### 모듈 순서 (의존성 기반)

```
1. config/settings.py      ← 환경변수, Pydantic Settings
2. src/llm.py              ← 멀티프로바이더 LLM 클라이언트
3. src/personas/loader.py  ← profile.json + soul.md 로더
4. src/agents/             ← sales_agent.py + customer_agent.py
5. src/conversation/       ← engine.py + rules.py
6. src/evaluation/         ← evaluator.py + aggregator.py
7. src/ralph/             ← loop.py + 6개 단계 파일
8. scripts/run_simulation.py ← RALPH 1회 실행 스크립트
```

### 코더 위임 프롬프트 템플릿

각 모듈마다 이 형식으로 코더에게 지시:

```
"ralphton-harness/ 아래 하네스 문서를 참고하여
 ../output/{모듈 경로}를 구현하라.

 참고할 하네스 문서:
 - architecture/{관련 문서}
 - contracts/schemas/{관련 스키마}
 - prompts/{관련 프롬프트}

 요구사항:
 - {구체적 요구사항}

 검증 방법:
 - {import 확인 또는 테스트 명령}"
```

### 모듈별 검증

각 모듈 완료 후 오케스트레이터가 직접 확인:

```bash
# 예: llm 모듈 검증
cd output && python -c "from src.llm import call_llm; print('OK')"

# 예: 전체 import 검증
cd output && python -c "from src.ralph.loop import run_ralph_loop; print('OK')"
```

검증 통과 → CHECKPOINT 업데이트 → 다음 모듈
검증 실패 → 에러 메시지와 함께 코더에게 수정 지시

---

## Phase 2: 베이스라인 실행

```bash
cd ../output
RALPHTHON_MODE=DEV python scripts/run_simulation.py > run.log 2>&1
grep "^avg_score:\|^cluster_coverage:\|^best_strategy:" run.log
```

결과가 있으면:
```bash
# results.tsv에 기록
echo "<commit>\t<score>\t<coverage>\t<strategy>\tkeep\tbaseline" >> results.tsv
git add -A && git commit -m "phase2: baseline avg_score=<score>"
```

CHECKPOINT 업데이트:
```json
{
  "phase": "phase3",
  "phase2": {"status": "completed", "baseline_score": <score>, ...},
  "next_action": "Phase 3 autoresearch 루프를 시작하라."
}
```

결과가 없으면:
```bash
tail -n 50 run.log
```
→ 에러 파악 → 코더에게 수정 지시 → 재실행

---

## Phase 3: Autoresearch (최대 5회 실험)

`program.md`를 따른다. 핵심만 여기 요약:

### 시작 시

```bash
# 첫 시작이면 브랜치 생성
git checkout -b autoresearch/$(date +%b%d | tr '[:upper:]' '[:lower:]')
```

이어가기면 CHECKPOINT에서 git_branch 확인 → 해당 브랜치로 checkout.

### 루프

```
LOOP (최대 5회 — experiment_count가 5에 도달하면 종료):

  1. CHECKPOINT.json 읽기
     → experiment_count, current_score, consecutive_discards 확인
     → experiment_count >= 5이면 루프 종료 → Phase 4로 전환

  2. results.tsv 읽기
     → 이전 실험 패턴 분석

  3. 가설 수립
     → 약한 클러스터 파악
     → "이렇게 바꾸면 이 점수가 오를 것" 가설

  4. strategy_prompt.md 수정
     → 가설에 따라 변경
     → git add strategy_prompt.md
     → git commit -m "experiment: <가설>"

  5. 시뮬레이션 실행
     → python scripts/run_simulation.py > run.log 2>&1

  6. 결과 추출
     → grep "^avg_score:" run.log
     → 비어있으면 crash 처리

  7. 판정 (criteria/autoresearch-rules.md 기준)
     → avg_score 2점+ 상승 → keep
     → 동일, coverage 5%+ 상승 → keep
     → 그 외 → discard (git reset --hard HEAD~1)

  8. results.tsv에 기록

  9. CHECKPOINT.json 업데이트
     → experiment_count++
     → current_score, keep/discard/crash count
     → consecutive_discards
     → best_score 갱신 여부
     → next_action

  10. experiment_count < 5 → 다음 실험으로
      experiment_count >= 5 → Phase 4로 전환
```

### Phase 3 완료 시

```
CHECKPOINT 업데이트:
  phase → "phase4"
  phase3.status → "completed"
  next_action → "Phase 4 웹 대시보드를 구현하라."
```

### 규칙

1. **5회 제한**: 최대 5회 실험 후 Phase 4로 자동 전환.
2. **NEVER ASK**: 사람에게 묻지 마라.
3. **ONE FILE**: Phase 3에서는 strategy_prompt.md만 수정.
4. **CHECKPOINT ALWAYS**: 매 실험 후 CHECKPOINT.json 업데이트.
5. **THINK HARDER**: 연속 discard면 방향을 바꿔라.
6. **FIX IT**: crash면 코더에게 수정 시키고 이어가라.

---

## Phase 4: 웹 대시보드

`architecture/visualization-spec.md`를 따른다. 핵심만 여기 요약:

### 목적

Phase 2~3의 시뮬레이션 결과(runs/ 데이터)를 시각화하는 웹 대시보드를 구현한다.

### 기술 스택

- **React 19 + TypeScript**
- **HeroUI v3** (`@heroui/react` + `@heroui/styles`)
- **Tailwind CSS v4**
- **Recharts** (차트)
- Vite 빌드

### 구현할 패널 (visualization-spec.md 참조)

```
A. Strategy Leaderboard  — 전략 순위표 (Table)
B. Heatmap               — 전략 × 클러스터 점수 행렬 (CSS Grid, 5단계 색상)
C. Cell Explanation       — 히트맵 셀 클릭 시 상세 (Card)
D. Cluster Insight        — 클러스터별 분석 (Accordion)
E. Persona Drilldown      — 대표 페르소나 3명 (best/median/failure)
F. Experiment Trend       — 점수 추이 그래프 (Recharts LineChart)
G. Conversation Viewer    — 대화 원문 열람 (채팅 UI)
```

### 데이터 소스

- `../output/runs/<run_id>/summary.json` — 집계 데이터
- `../output/runs/<run_id>/evaluations.json` — 개별 채점
- `../output/runs/<run_id>/strategies.json` — 전략 목록
- `../output/runs/<run_id>/transcripts/<strategy>/<persona>.json` — 대화 원문
- `../output/runs/<run_id>/reason.json` — 패턴 분석
- `../output/runs/<run_id>/learnings.json` — 학습 포인트
- `../output/results.tsv` — 실험 로그 (Experiment Trend용)

### 구현 순서

```
1. 프로젝트 초기화 (Vite + React + TS + HeroUI + Tailwind + Recharts)
2. 데이터 로딩 레이어 (runs/ JSON 파싱)
3. Layout + Header
4. Strategy Leaderboard (A)
5. Heatmap (B) — 핵심 시각화
6. Cell Explanation (C) + Cluster Insight (D)
7. Persona Drilldown (E) + Experiment Trend (F)
8. Conversation Viewer (G)
9. 빌드 + 동작 확인
```

### Phase 4 완료 조건

- [ ] `npm run build` 성공
- [ ] `npm run dev`로 로컬 서버 실행 가능
- [ ] 히트맵이 실제 runs/ 데이터를 표시
- [ ] 셀 클릭 → Cell Explanation 업데이트
- [ ] Experiment Trend가 results.tsv 데이터를 그래프로 표시

### Phase 4 실패 시

코드가 빌드되지 않으면:
1. 에러 메시지 읽기
2. 수정
3. 다시 빌드
4. 반복 (사람에게 묻지 않음)

### Phase 4 완료 시

```
CHECKPOINT 업데이트:
  phase → "done"
  phase4.status → "completed"
  next_action → "완료. 대시보드는 npm run dev로 실행."
```

---

## 절대 규칙 (전체)

1. **CHECKPOINT.json이 진실의 원천이다.** 모든 상태는 여기에 기록.
2. **세션이 끝나기 전에 반드시 CHECKPOINT를 업데이트하라.**
3. **새 세션은 CHECKPOINT를 먼저 읽고 이어간다.**
4. **코드 생성은 코더에게, 실행/판단은 직접 한다.**
5. **Phase 3는 최대 5회 실험. 완료 시 Phase 4로 전환.**
6. **페르소나(data/personas/)를 절대 수정하지 마라.**

---

## 디렉토리 분리 원칙

**하네스(설계도)와 output(생성물)은 별도 디렉토리다.**

```
ralphton/
├── ralphthon-harness/    ← 하네스. git에 올림. 깨끗하게 유지.
│   ├── MASTER-PROMPT.md
│   ├── CHECKPOINT.json
│   ├── architecture/
│   ├── contracts/
│   ├── prompts/
│   ├── criteria/
│   ├── examples/
│   ├── data/personas/
│   ├── program.md
│   └── ...
│
└── output/               ← 에이전트가 생성하는 코드. 하네스 바깥.
    ├── src/
    ├── scripts/
    ├── config/
    ├── frontend/          ← Phase 4에서 생성. React + HeroUI 대시보드.
    ├── strategy_prompt.md  (prompts/에서 복사)
    ├── results.tsv
    └── runs/
```

하네스 안에 output/을 만들지 않는다.
output/은 하네스와 같은 레벨(형제 디렉토리)에 생성한다.

### 경로 규칙

- 하네스 문서 참조: 하네스 기준 상대경로 (예: `architecture/system-overview.md`)
- output 코드: 하네스 기준 `../output/` (예: `../output/src/llm.py`)
- 페르소나 데이터: output에서 참조 시 `../../ralphthon-harness/data/personas/` 또는 심볼릭 링크

## 데이터 위치

| 데이터 | 경로 (하네스 기준) |
|--------|-------------------|
| 페르소나 200명 | `data/personas/P001~P200/` |
| 전략 프롬프트 초기 버전 | `prompts/strategy_prompt.md` |
| 제품 정보 | `program.md`에 기재 |
| 상태 파일 | `CHECKPOINT.json` |
| 생성 코드 | `../output/` |
| 실험 로그 | `../output/results.tsv` |
| 시뮬 결과 | `../output/runs/` |

---

## 시작하라.

1. CHECKPOINT.json을 읽어라.
2. phase에 따라 분기하라.
3. Phase 1 → 2 → 3(5회) → 4(대시보드) 순서로 끝까지 자율로 완료하라.
