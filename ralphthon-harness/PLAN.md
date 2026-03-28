# Ralphthon Harness — 설계 계획서 v2

> Deep Interview Spec 기반 재설계 (2026-03-27)
> Spec: specs/deep-interview-ralphthon-harness.md

---

## 한 문장 정의

> 하네스 = 에이전트가 이 폴더 하나만 읽고,
> 설득 시뮬레이션 완성품을 만들고 → 실행하고 → 밤새 전략을 진화시켜
> 최적 결과까지 산출하는 "프롬프트 한 번 → 자율 완료" 설계도

---

## 핵심 원칙

1. **하네스 ≠ 코드** — 에이전트에게 주는 설계도. 코드는 에이전트가 생성.
2. **3단계 자율 실행** — 코드 생성 → 시뮬레이션 실행 → autoresearch 진화
3. **nudge 참고, 복사 아님** — nudge 구조를 예시로 보여주되 그대로 쓰지 않음
4. **2-레벨 루프** — RALPH 내부 루프 + autoresearch 외부 루프
5. **프롬프트 한 번 → 끝** — 중간에 사람 개입 없이 전부 자율 완료

---

## 에이전트가 하네스를 받으면 하는 일 (실행 흐름)

```
에이전트가 MASTER-PROMPT.md를 읽음
  │
  ▼
Phase 1: 코드 생성 ─────────────────────────────────────
  │  architecture/ 읽고 전체 구조 이해
  │  reference/nudge-patterns.md 읽고 구현 패턴 파악
  │  contracts/schemas/ 읽고 입출력 규격 파악
  │  data/personas/ 복사 (이건 이미 있음)
  │
  │  → src/ 코드 생성 (RALPH Loop + 대화엔진 + 평가 + LLM 클라이언트)
  │  → config/ 설정 생성
  │  → scripts/ 실행 스크립트 생성
  │  → frontend/ 대시보드 생성 (선택)
  │  → tests/ 최소 테스트 생성
  │
  │  → 의존성 설치, 기본 동작 확인
  │
  ▼
Phase 2: 베이스라인 실행 ────────────────────────────────
  │  strategy_prompt.md (초기 버전) 확인
  │  python scripts/run_simulation.py > run.log 2>&1
  │  결과 확인: grep "^avg_score:" run.log
  │  results.tsv에 baseline 기록
  │  git commit
  │
  ▼
Phase 3: autoresearch 루프 (NEVER STOP) ────────────────
  │  LOOP FOREVER:
  │    1. strategy_prompt.md 수정 (가설 기반)
  │    2. git commit
  │    3. python scripts/run_simulation.py > run.log 2>&1
  │    4. 결과 확인
  │    5. 개선이면 keep, 아니면 git reset --hard
  │    6. results.tsv 기록
  │    7. 다음 실험
  │
  └─ 사람이 수동 중단할 때까지 무한 반복
```

---

## 하네스 폴더 구조 (에이전트에게 주는 것)

```
ralphthon-harness/
│
├── MASTER-PROMPT.md            ← ① 에이전트 진입점 (이것만 읽으면 시작)
│
├── architecture/               ← ② 시스템 설계 문서
│   ├── system-overview.md      ← 전체 그림 + 2-레벨 루프 구조
│   ├── execution-phases.md     ← 3단계 실행 흐름 상세
│   ├── ralph-loop.md           ← RALPH 내부 루프 (H→P→A→E→R→L) 상세
│   ├── autoresearch-loop.md    ← autoresearch 외부 루프 상세
│   └── tech-stack.md           ← 기술 스택 + 제약사항
│
├── reference/                  ← ③ nudge 참고 자료
│   ├── nudge-patterns.md       ← nudge 코드에서 추출한 구현 패턴
│   ├── nudge-schemas.md        ← nudge 데이터 구조 정리
│   └── nudge-vs-ours.md        ← nudge와 우리 차이점 명시
│
├── contracts/                  ← ④ 입출력 계약
│   ├── product-contract.md     ← 최종 산출물 정의
│   └── schemas/                ← JSON Schema
│       ├── strategy.schema.json
│       ├── conversation-session.schema.json
│       ├── evaluation-result.schema.json
│       ├── ralph-iteration.schema.json
│       └── experiment-result.schema.json
│
├── prompts/                    ← ⑤ 프롬프트 템플릿
│   ├── strategy_prompt.md      ← autoresearch가 수정하는 파일 (초기 버전)
│   ├── sales-agent-system.md   ← 판매 에이전트 시스템 프롬프트
│   ├── customer-agent-system.md← 고객 에이전트 시스템 프롬프트 템플릿
│   ├── judge-system.md         ← Judge 평가 프롬프트
│   ├── hypothesize-system.md   ← 전략 가설 생성 프롬프트
│   ├── reason-system.md        ← 패턴 분석 프롬프트
│   └── learn-system.md         ← 학습 추출 프롬프트
│
├── data/                       ← ⑥ 고정 데이터
│   └── personas/               ← 200명 페르소나 (이미 존재)
│       ├── P001/
│       │   ├── profile.json
│       │   └── soul.md
│       ├── P002/ ...
│       └── P200/
│
├── criteria/                   ← ⑦ 품질 기준
│   ├── evaluation-rubric.md    ← 4차원 평가 루브릭
│   ├── quality-gates.md        ← 단계별 통과 기준
│   └── autoresearch-rules.md   ← keep/discard 판단 기준
│
├── examples/                   ← ⑧ 예시 데이터 (에이전트 참고용)
│   ├── sample-conversation.json
│   ├── sample-evaluation.json
│   ├── sample-ralph-iteration.json
│   └── sample-results.tsv
│
├── program.md                  ← ⑨ autoresearch 실험 루프 지시서
│
└── specs/                      ← 메타 (사람용)
    └── deep-interview-ralphthon-harness.md
```

---

## 에이전트가 생성할 완성품 구조 (하네스가 아님, 에이전트가 만드는 것)

```
output/                         ← 에이전트가 생성하는 코드
├── config/
│   ├── settings.py             ← 환경 설정 (Pydantic Settings)
│   ├── default.yaml            ← 기본 설정값
│   └── product.yaml            ← 판매 제품 정보
│
├── src/
│   ├── llm.py                  ← 멀티 프로바이더 LLM 클라이언트
│   ├── agents/
│   │   ├── base.py             ← 에이전트 기반 클래스
│   │   ├── sales_agent.py      ← 판매 에이전트 (LLM)
│   │   └── customer_agent.py   ← 고객 에이전트 (soul.md 기반 LLM)
│   │
│   ├── conversation/
│   │   ├── engine.py           ← 턴 기반 대화 오케스트레이션
│   │   ├── turn.py             ← Turn, ConversationSession 모델
│   │   └── rules.py            ← 종료 조건 판정
│   │
│   ├── evaluation/
│   │   ├── evaluator.py        ← LLM-as-Judge 4차원 평가
│   │   ├── dimensions.py       ← 평가 루브릭 정의
│   │   ├── aggregator.py       ← 점수 집계
│   │   └── schema.py           ← 평가 결과 모델
│   │
│   ├── ralph/                  ← RALPH 내부 루프
│   │   ├── loop.py             ← 메인 루프 오케스트레이터
│   │   ├── hypothesize.py      ← H: 전략 가설 생성
│   │   ├── plan.py             ← P: 페르소나 선택
│   │   ├── act.py              ← A: 대화 배치 실행
│   │   ├── reason.py           ← R: 패턴 분석
│   │   ├── learn.py            ← L: 학습 추출
│   │   └── strategy.py         ← Strategy/StrategyResult 모델
│   │
│   ├── personas/
│   │   ├── loader.py           ← soul.md + profile.json 로더
│   │   └── schema.py           ← 페르소나 모델
│   │
│   └── api/                    ← (선택) 웹 대시보드
│       └── main.py             ← FastAPI + SSE
│
├── scripts/
│   ├── run_simulation.py       ← RALPH Loop 1회 실행
│   └── run_autoresearch.py     ← autoresearch 외부 루프 실행
│
├── frontend/                   ← (선택) 대시보드 HTML
│   └── index.html
│
├── strategy_prompt.md          ← autoresearch가 수정하는 파일
├── results.tsv                 ← 실험 로그
└── requirements.txt
```

---

## Phase별 상세 설계

### Phase 0: 하네스 문서 작성 (우리가 하는 것)

이건 에이전트가 아니라 우리가 만드는 것.

| # | 작업 | 산출물 | 의존 |
|---|------|--------|------|
| 0-1 | MASTER-PROMPT.md 작성 | MASTER-PROMPT.md | 전체 설계 확정 후 |
| 0-2 | 시스템 개요 작성 | architecture/system-overview.md | — |
| 0-3 | 실행 흐름 작성 | architecture/execution-phases.md | 0-2 |
| 0-4 | RALPH 내부 루프 상세 | architecture/ralph-loop.md | 0-2 |
| 0-5 | autoresearch 외부 루프 상세 | architecture/autoresearch-loop.md | 0-2 |
| 0-6 | 기술 스택 정리 | architecture/tech-stack.md | — |
| 0-7 | nudge 패턴 추출 | reference/nudge-patterns.md | nudge 분석 완료 |
| 0-8 | nudge 스키마 정리 | reference/nudge-schemas.md | 0-7 |
| 0-9 | nudge vs 우리 차이 정리 | reference/nudge-vs-ours.md | 0-7, 0-8 |
| 0-10 | JSON Schema 정의 | contracts/schemas/*.json | 0-4 |
| 0-11 | 제품 계약서 | contracts/product-contract.md | 0-3 |
| 0-12 | 프롬프트 템플릿 작성 | prompts/*.md (7개) | 0-4 |
| 0-13 | 평가 루브릭 작성 | criteria/evaluation-rubric.md | nudge 5차원 참고 |
| 0-14 | 품질 게이트 작성 | criteria/quality-gates.md | 0-3 |
| 0-15 | autoresearch 규칙 작성 | criteria/autoresearch-rules.md | 0-5 |
| 0-16 | 예시 데이터 생성 | examples/*.json + .tsv | 0-10 |
| 0-17 | program.md 작성 | program.md | 0-5, 0-15 |
| 0-18 | MASTER-PROMPT.md 최종화 | MASTER-PROMPT.md | 0-1 ~ 0-17 전부 |

### 작업 우선순위 (의존성 기반)

```
병렬 가능 ─── 0-2, 0-6, 0-7
                │
        ┌───────┼───────┐
        ▼       ▼       ▼
      0-3     0-6     0-7 → 0-8 → 0-9
        │       │
   ┌────┼────┐  │
   ▼    ▼    ▼  ▼
  0-4  0-5  0-11  0-6
   │    │
   ▼    ▼
  0-10 0-15 → 0-17
   │
   ▼
  0-12, 0-13, 0-14, 0-16
   │
   ▼
  0-18 (MASTER-PROMPT 최종화 — 마지막)
```

---

## 각 문서의 핵심 내용 요약

### MASTER-PROMPT.md

에이전트가 읽는 첫 번째이자 유일한 진입점.

```
너는 이 하네스를 읽고 3단계를 자율적으로 완료한다:

1. 코드 생성: architecture/, reference/, contracts/ 읽고
   설득 시뮬레이션 시스템을 구현하라.
2. 베이스라인 실행: 구현한 코드로 첫 시뮬레이션을 돌려라.
3. autoresearch: program.md를 따라 밤새 전략을 진화시켜라.

읽어야 할 파일 순서:
  architecture/system-overview.md → execution-phases.md → ...

절대 규칙:
  - 사람에게 묻지 마라
  - 중간에 멈추지 마라
  - 코드가 안 돌아가면 고쳐라
  - autoresearch 루프에 들어가면 NEVER STOP
```

### architecture/system-overview.md

2-레벨 루프 구조의 전체 그림.

```
외부 루프 (autoresearch):
  strategy_prompt.md 수정 → 내부 루프 실행 → 점수 비교 → keep/discard

내부 루프 (RALPH):
  Hypothesize → Plan → Act → Evaluate → Reason → Learn → 다음 Hypothesize
  (nudge의 RALPH Loop과 동일 구조, 우리 개선 적용)
```

### architecture/ralph-loop.md

RALPH 6단계 각각의 입력/출력/사용 모델.

```
H (Hypothesize): 비싼 모델. 학습 기반 새 전략 생성.
P (Plan): 코드. 200명 중 이번 실행 대상 선택.
A (Act): 싼 모델. Sales(LLM) ↔ Customer(soul.md+LLM) 대화.
E (Evaluate): 비싼 모델. 4차원 평가 채점.
R (Reason): 비싼 모델. 상위/하위 대화 비교, 패턴 발견.
L (Learn): 비싼 모델. 재사용 학습 포인트 추출.
```

### reference/nudge-patterns.md

nudge 코드에서 추출한 구현 패턴. 에이전트가 "이런 식으로 만들어라"
참고하는 용도. 핵심:

```
- OpenAI SDK로 OpenRouter 연결하는 패턴 (src/llm.py)
- asyncio.Semaphore로 동시성 제어 (src/ralph/act.py)
- Pydantic BaseModel로 Strategy/StrategyResult 정의
- 규칙 기반 고객 에이전트 상태 머신 (우리는 LLM으로 대체)
- 키워드 기반 대화 종료 판정 (conversation/rules.py)
- JSON 파싱 + ```코드블록 제거 패턴
```

### reference/nudge-vs-ours.md

nudge와 우리의 차이를 명확히 해서, 에이전트가 헷갈리지 않게.

```
| 항목 | nudge | 우리 |
|------|-------|------|
| 고객 에이전트 | 규칙 기반 (RuleCustomerAgent) | soul.md 기반 LLM |
| 페르소나 | 6 enum 조합 (YAML) | profile.json + soul.md 자연어 |
| 전략 진화 | RALPH 내부만 | + autoresearch 외부 메타 루프 |
| 제품 | VitaForest 49,900원 | 바이탈케어 29,900원 |
| 평가 점수 | 1-10 (5차원) | 1-10 (5차원, 루브릭 커스텀) |
| LLM | OpenRouter 고정 | 멀티 프로바이더 (Gemini/OpenAI/Anthropic/Ollama) |
```

### prompts/ (7개 프롬프트 템플릿)

에이전트가 코드에 삽입할 시스템 프롬프트의 "원본".
nudge의 prompts/를 참고하되 우리 방식으로 개선.

- strategy_prompt.md: autoresearch가 수정하는 유일한 파일
- 나머지 6개: 코드에 고정 삽입

### contracts/schemas/

에이전트가 생성하는 코드의 데이터 구조를 강제.
"이 JSON 형태를 따르는 코드를 만들어라".

### program.md

autoresearch 실험 루프 지시서.
기존에 만든 것을 유지하되, Phase 1(코드 생성) 이후에
자동으로 Phase 2→3으로 넘어가는 흐름을 추가.

---

## 기존 자산 활용 계획

| 기존 파일 | 처리 | 상태 |
|-----------|------|------|
| data/personas/P001~P220/ (soul.md + profile.json) | 그대로 유지 | ✅ 완료 |
| docs/persona-theoretical-grounding.md | 유지 (배경 자료) | ✅ 완료 |
| scripts/generate_souls.py 등 | 유지 (유틸리티, 하네스 본체 아님) | ✅ 완료 |
| evaluate.py, simulate.py, config.py | 삭제 완료 (프로토타입이었음) | ✅ 삭제됨 |
| program.md | 리라이트 완료 | ✅ 완료 |
| strategy_prompt.md | prompts/로 이동 완료, 루트 삭제 | ✅ 완료 |
| results.tsv | 유지 (헤더만) | ✅ 완료 |
| specs/ | 유지 (메타 문서) | ✅ 완료 |
| PLAN.md | 이 파일 | ✅ 완료 |

---

## 정리: 지금부터 만들어야 하는 파일 목록

총 18개 작업, 약 20개 파일 생성/수정.

### 새로 만들 파일 (14개)
```
MASTER-PROMPT.md
architecture/system-overview.md
architecture/execution-phases.md
architecture/ralph-loop.md
architecture/autoresearch-loop.md
architecture/tech-stack.md
reference/nudge-patterns.md
reference/nudge-schemas.md
reference/nudge-vs-ours.md
contracts/product-contract.md
contracts/schemas/ (5개 JSON Schema)
criteria/evaluation-rubric.md
criteria/quality-gates.md
criteria/autoresearch-rules.md
examples/ (4개 예시 파일)
```

### 리라이트할 파일 (2개)
```
program.md (Phase 1→2→3 자동 전환 추가)
prompts/strategy_prompt.md (기존 strategy_prompt.md 이동)
```

### 프롬프트 템플릿 (6개 새로 작성)
```
prompts/sales-agent-system.md
prompts/customer-agent-system.md
prompts/judge-system.md
prompts/hypothesize-system.md
prompts/reason-system.md
prompts/learn-system.md
```

### 삭제된 파일 (완료)
```
evaluate.py, simulate.py, config.py, requirements.txt — 삭제 완료
strategy_prompt.md (루트) — prompts/로 이동 후 루트에서 삭제 완료
```

---

## 작업 순서 추천

```
1차 (기반)     → 0-2, 0-6, 0-7  (system-overview, tech-stack, nudge-patterns)
2차 (구조)     → 0-3, 0-4, 0-5, 0-8, 0-9  (execution, ralph, autoresearch, nudge비교)
3차 (계약)     → 0-10, 0-11  (schemas, product-contract)
4차 (프롬프트)  → 0-12  (prompts 7개)
5차 (기준)     → 0-13, 0-14, 0-15  (rubric, quality-gates, autoresearch-rules)
6차 (예시)     → 0-16  (examples)
7차 (루프)     → 0-17  (program.md 리라이트)
8차 (진입점)   → 0-18  (MASTER-PROMPT.md 최종화)
```

---

상태: 설계 계획 확정
작성일: 2026-03-27
다음 단계: Phase 0 실행 (1차부터 순서대로)
