> **Ralphthon — AI 설득 전략 자동 진화 시스템**
>
> 신약은 사람에게 투여하기 전에 시뮬레이션을 수천 번 돌린다.
> 세일즈 전략은? 실제 고객에게 바로 실험한다.
> 실패한 전략에 노출된 고객은 돌아오지 않는다.
>
> Ralphthon은 200명의 심리학 기반 가상 페르소나에게
> AIDA 퍼널 구조의 세일즈 전략을 자동 시뮬레이션하고,
> LLM-as-Judge가 대화를 평가한 뒤,
> 상위/하위 패턴을 비교 분석하여 다음 세대 전략을 스스로 개선한다.
> 이 루프(RALPH: Hypothesize→Plan→Act→Evaluate→Reason→Learn)를
> 세대마다 누적되는 Strategy Ledger와 함께 반복하면,
> 사람 개입 없이 전략이 세대를 거듭하며 진화한다.
>
> 즉, 진화 알고리즘의 선택압을 가상 고객 시뮬레이션으로 구현한 것이다.

---

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

## 개선 과제 A: 병렬 실행 강화 + Retry 메커니즘

> 현황 진단 (2026-03-29)

### 현재 상태

act.py와 evaluate.py가 `asyncio.Semaphore` + `asyncio.gather`로 이미 병렬 실행 중.
하지만 아래 3가지 문제가 있다:

```
문제 1: retry 없음
  - act.py: return_exceptions=True로 에러 캐치하지만, 실패 대화는 버림
  - engine.py: sales/customer 에러 시 "[에러]" 텍스트로 대체 → 쓸모없는 대화가 평가로 넘어감
  - evaluate.py: 동일하게 실패 건 버림
  → API rate-limit, 네트워크 일시장애 시 데이터 유실

문제 2: max_concurrent=5 너무 보수적
  - Gemini 유료 Pro: 256 RPM
  - Gemini Flash Lite: 4,000 RPM
  - 5 동시실행이면 Flash Lite RPM의 ~1%만 사용

문제 3: 에러 보고가 불투명
  - 몇 건이 실패했는지, 어떤 페르소나/전략 조합이 빠졌는지 추적 불가
  - 결과 신뢰도를 판단할 수 없음
```

### 변경 계획

#### A-1. llm.py에 retry with exponential backoff 추가

모든 LLM 호출의 근본 레이어에서 retry를 처리한다.
개별 단계(act, evaluate 등)마다 retry를 넣는 것보다 근본적.

```
call_llm() 내부:
  max_retries = 3
  base_delay = 1.0초

  for attempt in range(max_retries + 1):
    try:
      response = await _call_provider(...)
      return response
    except RateLimitError:
      delay = base_delay * (2 ** attempt) + random_jitter(0~0.5s)
      await asyncio.sleep(delay)
    except TransientError (5xx, timeout, connection):
      delay = base_delay * (2 ** attempt)
      await asyncio.sleep(delay)
    except FatalError (4xx auth, invalid model):
      raise immediately  ← retry 하지 않음

  raise MaxRetriesExceeded(...)
```

핵심: 모든 단계(H, A, E, R, L)가 자동으로 retry 혜택을 받음.

#### A-2. act.py / evaluate.py에 task-level retry 추가

llm.py retry가 실패한 경우(3회 연속 실패)에 대비한 2차 방어선.

```
async def run_one(strategy, persona, max_task_retries=2):
    for attempt in range(max_task_retries + 1):
        try:
            session = await run_conversation(...)
            # 에러 텍스트가 아닌 정상 대화인지 검증
            if session["ended_by"] != "error":
                return session
            if attempt < max_task_retries:
                await asyncio.sleep(2 ** attempt)
        except Exception as e:
            if attempt < max_task_retries:
                await asyncio.sleep(2 ** attempt)
            else:
                return FailedSession(strategy, persona, error=e)
```

evaluate.py도 동일 패턴.

#### A-3. max_concurrent 동적 조정

```
settings.py 변경:
  max_concurrent 기본값: 5 → 20

  + 환경변수 RALPHTHON_MAX_CONCURRENT로 오버라이드 가능 (이미 존재)

  + 향후: 429 응답 빈도에 따라 런타임에 자동 조절하는
    adaptive concurrency controller 고려 (backpressure 패턴)
```

#### A-4. 실패 보고서 생성

```
run_all_conversations() 리턴값 변경:
  기존: list[dict]  (성공만)
  변경: {
    "sessions": list[dict],      ← 성공
    "failures": list[dict],      ← 실패 (어떤 조합이, 왜 실패했는지)
    "stats": {
      "total": 600,
      "succeeded": 594,
      "failed": 6,
      "retry_count": 12,         ← 총 재시도 횟수
      "success_rate": 99.0
    }
  }

→ summary.json에 포함되어 결과 신뢰도 판단 가능
```

### 변경 대상 파일

| 파일 | 변경 내용 |
|------|-----------|
| `src/llm.py` | retry + exponential backoff + jitter |
| `src/ralph/act.py` | task-level retry + 실패 보고 |
| `src/ralph/evaluate.py` | task-level retry + 실패 보고 |
| `config/settings.py` | max_concurrent 기본값 20으로 |
| `src/ralph/loop.py` | 실패 stats를 summary에 포함 |

### 영향받는 하네스 문서

| 문서 | 추가 내용 |
|------|-----------|
| `architecture/ralph-loop.md` | A, E 단계에 retry 스펙 명시 |
| `architecture/tech-stack.md` | retry 정책, concurrency 가이드 |
| `criteria/quality-gates.md` | success_rate 기준 추가 (e.g. 95% 미만이면 재실행) |

---

## 개선 과제 B: 세대 간 전략 히스토리 누적 (Strategy Ledger)

> 현황 진단 (2026-03-29)

### 현재 상태 — 문제점

```
세대 1: H→P→A→E→R→L → learnings_1 생성
세대 2: H(learnings_1 참조)→P→A→E→R→L → learnings_2 생성
세대 3: H(learnings_2 참조)→...
  ...
세대 10: H(learnings_9만 참조)

문제:
  세대 10이 직전 세대(9)의 학습만 본다.
  세대 1~8의 학습/전략/패턴은 완전히 소실.
  → 이미 실패한 전략을 다시 시도할 수 있음
  → 초기 세대에서 발견한 강력한 패턴이 유실됨
  → 세대가 많아질수록 "학습 망각" 발생
```

### 목표

10세대를 돌렸을 때, 세대 10의 Hypothesize가:
- 전 세대(1~9)에서 시도된 전략과 결과를 전부 참조
- 이미 실패한 접근을 반복하지 않음
- 세대 초기에 발견된 핵심 인사이트가 보존됨
- BUT: context가 폭발하지 않음 (세대당 원문이 아닌 압축 요약)

### 설계: Strategy Ledger (전략 원장)

세대마다 누적되는 압축된 전략 기록부.
회계의 "원장(ledger)" 개념 — 모든 거래(=전략 시도)가 기록되되,
각 항목은 핵심만 남긴 요약.

#### 데이터 구조

```
output/strategy_ledger.json
{
  "generations": [
    {
      "generation": 1,
      "run_id": "run_1743300000",
      "timestamp": "2026-03-29T10:00:00Z",
      "strategies_tried": [
        {
          "strategy_id": "strategy-01",
          "hypothesis": "ROI 프레이밍으로 합리적 구매자 공략",
          "avg_score": 58.3,
          "outcome_distribution": {"interested": 40, "neutral": 120, "resistant": 40},
          "best_cluster": "budget_practical (avg 72.1)",
          "worst_cluster": "hard_sell_resistant (avg 38.5)"
        },
        ...
      ],
      "overall_avg_score": 55.7,
      "cluster_coverage": 40.0,
      "key_learnings": [
        "budget_practical에 가격 초반 언급 시 engagement +15",
        "hard_sell_resistant에 압박 톤 일관 실패"
      ],
      "winning_patterns": ["첫 턴 공감 → 데이터 제시 패턴이 상위"],
      "losing_patterns": ["긴 오프닝이 이탈 유발"]
    },
    {
      "generation": 2,
      ...
    }
  ],
  "cumulative_insights": {
    "never_repeat": [
      "hard_sell_resistant 클러스터에 고압적 톤 사용 금지 (세대1,3,5에서 반복 실패)"
    ],
    "proven_effective": [
      "budget_practical에 하루 비용 프레이밍 — 세대 1~10 일관 60+ (5세대 연속 검증)"
    ],
    "best_score_ever": 78.5,
    "best_strategy_ever": { "generation": 7, "strategy_id": "...", "avg_score": 78.5 }
  }
}
```

#### context 폭발 방지: 3-레이어 압축

```
Layer 1: cumulative_insights (항상 전달)
  ├── never_repeat: 확실히 실패한 접근들 (짧은 리스트)
  ├── proven_effective: 확실히 성공한 접근들 (짧은 리스트)
  └── best_score_ever + best_strategy_ever
  → 크기: 고정, 세대가 늘어도 ~500 토큰 이내

Layer 2: 최근 3세대 상세 (항상 전달)
  ├── 각 세대의 strategies_tried (전략별 1줄 요약 + 점수)
  ├── key_learnings
  └── winning/losing_patterns
  → 크기: ~1500 토큰 (3세대 x ~500 토큰)

Layer 3: 과거 세대 요약 (조건부 전달)
  ├── 세대 1~(N-3)의 1줄 요약만
  │   "세대 1: avg 55.7, ROI 전략 시도, budget_practical에서만 효과"
  └── 전략 ID + 점수 테이블
  → 크기: ~50 토큰/세대 × 세대수

총 context 추정 (세대 10 기준):
  Layer 1: ~500 토큰
  Layer 2: ~1500 토큰 (세대 8,9,10 상세)
  Layer 3: ~350 토큰 (세대 1~7 각 50토큰)
  합계: ~2,350 토큰 ← 관리 가능
```

### Hypothesize 프롬프트 변경

```
현재 hypothesize.py:
  if previous_learnings:
      user_prompt = f"## 이전 학습 내용\n{previous_learnings}\n..."

변경 후:
  if strategy_ledger:
      ledger_context = format_ledger_for_prompt(strategy_ledger)
      user_prompt = f"""## 전략 히스토리 (전 세대 누적)

### 절대 반복 금지 (검증된 실패)
{ledger_context.never_repeat}

### 검증된 성공 패턴
{ledger_context.proven_effective}

### 최근 3세대 상세
{ledger_context.recent_details}

### 과거 세대 요약
{ledger_context.past_summary}

### 현재 최고 기록: {ledger_context.best_score_ever}점 (세대 {N})

위 히스토리를 참고하여:
- 이미 실패한 접근은 반복하지 말 것
- 성공 패턴은 유지하되 새로운 변형을 시도할 것
- 아직 시도하지 않은 접근을 우선 탐색할 것

{num_strategies}개의 서로 다른 설득 전략을 생성하세요.
"""
```

### Ledger 업데이트 타이밍

```
RALPH Loop 1회 완료 시 (loop.py의 마지막):

  1. 현재 세대 결과를 ledger entry로 압축
  2. strategy_ledger.json에 append
  3. cumulative_insights 재계산:
     - 3세대 이상 연속 실패한 패턴 → never_repeat에 추가
     - 3세대 이상 연속 60+ 유지한 패턴 → proven_effective에 추가
     - best_score_ever 갱신

autoresearch 외부 루프에서:
  - 매 RALPH 실행 전에 ledger를 읽어서 strategy_ledger 파라미터로 전달
  - keep/discard 판단에도 ledger의 best_score_ever 참조
```

### 변경 대상 파일

| 파일 | 변경 내용 |
|------|-----------|
| `src/ralph/loop.py` | ledger 읽기/쓰기 + 파라미터 전달 |
| `src/ralph/hypothesize.py` | ledger 기반 프롬프트 구성 |
| `src/ralph/learn.py` | ledger entry 포맷 생성 |
| `scripts/run_simulation.py` | ledger 경로 설정 + 전달 |
| 신규: `src/ralph/ledger.py` | Strategy Ledger CRUD + 압축 로직 |

### 영향받는 하네스 문서

| 문서 | 추가 내용 |
|------|-----------|
| `architecture/ralph-loop.md` | L→H 연결에 ledger 경유 명시 |
| `architecture/autoresearch-loop.md` | ledger 기반 keep/discard + 히스토리 참조 |
| `contracts/schemas/` | `strategy-ledger.schema.json` 신규 |
| `prompts/hypothesize-system.md` | ledger 참조 가이드 |

### cumulative_insights 자동 갱신 규칙

```
never_repeat 추가 조건:
  - 특정 접근이 3세대 연속 하위 25% 점수
  - 또는 특정 클러스터에서 3세대 연속 40점 미만

proven_effective 추가 조건:
  - 특정 접근이 3세대 연속 상위 25% 점수
  - 또는 특정 클러스터에서 3세대 연속 60점 이상

갱신 주체: src/ralph/ledger.py의 update_cumulative_insights()
갱신 시점: 매 세대 완료 후
```

---

## 개선 과제 C: 세일즈 퍼널(Funnel) 기반 전략 구성

> 분석 (2026-03-29)

### 세일즈 퍼널이란

퍼널(깔때기)은 고객이 "존재도 모름" → "구매 완료"까지 거치는 단계적 여정.
각 단계에서 이탈이 발생하므로 깔때기 모양이 된다.

전통적으로 가장 많이 쓰이는 모델은 AIDA (1898, E. St. Elmo Lewis):

```
┌─────────────────────────────────────────────────┐
│  A — Attention (인지)                           │
│      "이게 뭐지?" → 관심을 끄는 단계             │
│      고객이 제품/브랜드의 존재를 처음 인식         │
├─────────────────────────────────────────────────┤
│  I — Interest (관심)                            │
│      "좀 더 알아볼까?" → 정보 탐색 단계          │
│      고객이 자기와 관련 있다고 느끼고 더 들으려 함  │
├─────────────────────────────────────────────────┤
│  D — Desire (욕구)                              │
│      "이거 갖고 싶다" → 감정적 연결 단계          │
│      혜택을 체감하고, "나에게 필요하다" 확신       │
├─────────────────────────────────────────────────┤
│  A — Action (행동)                              │
│      "사겠습니다" → 구매 결정 단계                │
│      실제 구매 행동 또는 구체적 다음 행동 약속     │
└─────────────────────────────────────────────────┘
```

더 정교한 현대 변형들:

```
TOFU-MOFU-BOFU (Top/Middle/Bottom of Funnel):
  TOFU: 인지 + 관심 → 넓은 대상에게 가치 제공
  MOFU: 고려 + 비교 → 신뢰 구축, 경쟁 우위 제시
  BOFU: 결정 + 행동 → 긴급성, 보증, CTA

Buyer's Journey (HubSpot):
  Awareness → Consideration → Decision

Forrester 비선형 모델:
  고객이 단계를 왔다갔다 하며, 반드시 순서대로 진행하지 않음
```

### 현재 Ralphthon 시스템과 퍼널의 관계

현재 시스템의 대화 구조를 퍼널 관점에서 매핑하면:

```
현재 대화 흐름 (3턴 왕복 = 6메시지):
  턴 0: 세일즈 → 첫 인사 + 제품 소개      ← Attention
  턴 0: 고객   → 첫 반응                   ← Attention → Interest 전환점
  턴 1: 세일즈 → 반론 대응 / 관심 확대     ← Interest → Desire
  턴 1: 고객   → 추가 반응                 ← Desire 수용 여부
  턴 2: 세일즈 → 클로징                    ← Action 유도
  턴 2: 고객   → 최종 반응                 ← Action 여부 결정

현재 전략 구조 (strategy 필드):
  approach           → 전체 퍼널에 걸친 접근법 (모호)
  opening_style      → Attention 단계만 담당
  objection_handling → Interest→Desire 전환 시 방어
  tone               → 전체 퍼널에 걸친 분위기
```

핵심 문제: 현재 전략은 "퍼널의 어디에서 무엇을 해야 하는지" 의식하지 않고
전체를 하나의 덩어리(approach)로 취급한다.

### 퍼널 도입 시 전략 구조 변경안

```
현재 Strategy 스키마:
{
  "strategy_id": "...",
  "hypothesis": "...",
  "approach": "...",           ← 퍼널 무시, 통째 접근
  "opening_style": "...",
  "objection_handling": "...",
  "tone": "..."
}

퍼널 기반 Strategy 스키마:
{
  "strategy_id": "...",
  "hypothesis": "...",

  "funnel": {
    "attention": {
      "hook_type": "질문형 | 데이터형 | 공감형 | 충격형",
      "opening_line_guide": "첫 문장에서 고객의 관심을 끄는 방법",
      "target_emotion": "호기심 | 걱정 | 공감"
    },
    "interest": {
      "value_framing": "고객이 '나와 관련 있다'고 느끼게 하는 방법",
      "information_depth": "핵심 1개만 | 비교 데이터 | 스토리텔링",
      "engagement_trigger": "고객이 질문하게 만드는 장치"
    },
    "desire": {
      "emotional_driver": "안전 | 절약 | 건강불안 | 소속감 | 자기관리",
      "proof_type": "사회적증거 | 전문가권위 | ROI계산 | 체험후기",
      "objection_preempt": "예상 반론을 선제적으로 해소하는 방법"
    },
    "action": {
      "cta_style": "직접제안 | 소프트CTA | 시험제안 | 한정제안",
      "urgency_type": "없음 | 시간한정 | 수량한정 | 가격변동",
      "fallback": "거부 시 대안 행동 제안 (샘플, 정보 전송 등)"
    }
  },

  "tone": "...",
  "persona_adaptation": "퍼널 각 단계를 고객 유형에 맞게 조정하는 원칙"
}
```

### 세일즈 에이전트 프롬프트 변경

```
현재:
  system prompt에 approach/opening_style/objection_handling을 통째로 넘김
  → 에이전트가 암묵적으로 "대충 순서대로" 대화

퍼널 기반:
  system prompt에 퍼널 단계별 가이드를 명시

  ## 대화 진행 가이드 (퍼널)

  ### 턴 0 (Attention → Interest)
  - 목표: 고객의 관심을 3초 안에 확보
  - 방법: {funnel.attention.hook_type}
  - 첫 문장: {funnel.attention.opening_line_guide}
  - 전환 신호: 고객이 "뭔데요?", "어떤 건데요?" 같은 반응을 보이면 성공

  ### 턴 1 (Interest → Desire)
  - 목표: "나에게도 필요하다"는 감정 형성
  - 정보 제시: {funnel.interest.value_framing}
  - 욕구 자극: {funnel.desire.emotional_driver}
  - 증거: {funnel.desire.proof_type}
  - 전환 신호: "얼마예요?", "어디서 살 수 있어요?" → Desire 형성됨

  ### 턴 2 (Desire → Action)
  - 목표: 구체적 다음 행동 이끌어내기
  - CTA: {funnel.action.cta_style}
  - 거절 대비: {funnel.action.fallback}
  - 절대 금지: 강압적 클로징, 감정적 압박

  ### 퍼널 역행 대응
  - 고객이 Interest에서 다시 Attention으로 돌아가면 (관심 없어진 신호)
    → 새로운 hook으로 재시도, 같은 이야기 반복하지 말 것
  - Desire에서 거절하면
    → fallback 행동 제안, 무리하게 밀지 말 것
```

### 평가(Judge) 루브릭 변경

현재 4차원 평가를 퍼널 진행도와 연계:

```
기존 4차원은 유지하되, 해석 기준에 퍼널 맵핑 추가:

  engagement (참여도)
    → 퍼널에서 Attention→Interest 전환 성공 여부와 직결
    → 고객이 질문을 시작했다 = Interest 진입 성공

  relevance (적합성)
    → 퍼널의 각 단계에서 고객 유형에 맞는 접근을 했는가
    → Interest 단계에서 고객의 실제 pain point에 연결했는가

  persuasion (설득력)
    → Interest→Desire 전환 품질
    → 반론 해소가 Desire를 강화했는가, 약화했는가

  purchase_intent (구매의향)
    → Desire→Action 전환 성공 여부
    → 단, 3턴 대화에서 Action까지 가는 건 어려움을 감안

추가 고려: funnel_progress 보조 지표 (0~3)
  0: Attention에서 이탈 (관심 끌기 실패)
  1: Interest까지 도달 (질문/반응 있었으나 욕구 미형성)
  2: Desire까지 도달 ("괜찮네요", "얼마예요?" 수준)
  3: Action까지 도달 (구매의사 또는 구체적 다음 행동)
```

### 의견: 긍정적 결과가 나올 것인가?

#### 긍정적 효과 (높은 확률)

```
1. 전략의 구체성이 대폭 향상
   현재: "ROI 중심 접근으로 합리적 구매자를 공략"
   퍼널: "턴0에서 하루 500원 데이터로 hook → 턴1에서 경쟁제품 비교로
         desire 형성 → 턴2에서 30일 환불보장 소프트CTA"
   → LLM이 더 구체적인 가이드를 받으므로 대화 품질 상승

2. 턴 활용 효율 극대화
   현재: 3턴을 "대충 자연스럽게" 사용 → 턴 낭비 발생
   (예: 턴 2에서 아직 Interest 단계 대화를 하고 있으면 클로징 기회 놓침)
   퍼널: 턴별 명확한 목표 → 매 턴이 다음 단계로 전환을 시도

3. 실패 원인 진단이 정밀해짐
   현재 Reason 단계: "이 전략은 점수가 낮다" (왜?)
   퍼널 기반: "Attention→Interest는 성공하지만 Desire 형성에서 실패"
   → 학습이 더 구체적 → 다음 세대 전략이 더 정교

4. 페르소나 클러스터별 퍼널 최적화 가능
   - budget_practical 클러스터: Interest 단계에서 ROI 데이터가 핵심
   - hard_sell_resistant 클러스터: Attention에서 소프트 hook 필수
   - health_anxious 클러스터: Desire에서 건강불안이 강력한 드라이버
   → 클러스터별 "어디서 이탈하는가"가 보이면 정밀 타격 가능

5. Strategy Ledger(과제B)와 시너지
   Ledger에 "이 전략은 attention→interest 전환율 80%지만
   desire→action 전환율 20%"가 기록되면,
   다음 세대는 action 단계만 집중 개선 가능
```

#### 부정적 효과 / 리스크

```
1. 과도한 구조화로 자연스러움 저하 (중간 리스크)
   세일즈 에이전트가 "퍼널 스크립트를 따르는 로봇"처럼 행동할 수 있음.
   실제 대화는 비선형 — 고객이 턴0에서 바로 "얼마예요?"(=Desire 스킵)
   하면 에이전트가 혼란할 수 있음.

   완화: 프롬프트에 "퍼널은 가이드일 뿐, 고객 반응에 따라 단계를
   건너뛰거나 돌아가는 것이 자연스럽다" 명시.
   + "퍼널 역행 대응" 가이드 포함 (위에 이미 설계됨).

2. 전략 스키마 복잡도 증가 (낮은 리스크)
   필드가 6개 → ~15개로 증가.
   Hypothesize 단계에서 LLM이 더 긴 JSON을 생성해야 함.
   → 파싱 실패율 약간 증가 가능.

   완화: extract_json()이 이미 robust함.
   + 필수 필드만 강제, 나머지는 선택.

3. 3턴으로 AIDA 전체를 커버하기 어려움 (현실적 제약)
   실제 세일즈에서 AIDA는 며칠~몇 주에 걸침.
   3턴(6메시지)에 A→I→D→A를 압축하면 각 단계가 1메시지뿐.
   → "Action 도달"을 기대하기보다 "최대한 깊이 진행"이 현실적 목표.

   완화: 평가 기준에서 "3턴 안에 converted 되는 것"을
   최고점의 필수 조건으로 보지 않음.
   funnel_progress=2(Desire 도달)이면 충분히 좋은 대화로 평가.

4. 현재 evaluation rubric과의 호환 (낮은 리스크)
   기존 4차원(engagement, relevance, persuasion, purchase_intent)이
   사실 이미 퍼널 단계와 자연스럽게 매핑됨 (위 분석 참조).
   → rubric 자체를 바꿀 필요 없고, 해석 가이드만 추가하면 됨.
```

#### 종합 판단

```
결론: 긍정적 효과가 압도적으로 클 것으로 예상한다.

근거:
  1. 현재 시스템의 가장 큰 약점이 "전략의 모호함"이다.
     approach 필드 하나에 모든 것을 담으니, LLM이 매 턴
     무엇을 해야 할지 명확하지 않음.
     퍼널은 이 모호함을 구조적으로 해결한다.

  2. 3턴 제약이 오히려 퍼널을 유리하게 만든다.
     턴이 적을수록 "각 턴에서 반드시 달성해야 할 것"이 명확해야 한다.
     퍼널 없이 3턴 = 방향 없는 대화.
     퍼널 있는 3턴 = 매 턴이 계단을 오르는 구조.

  3. 이미 평가 체계와 자연 호환된다.
     evaluation rubric의 4차원이 AIDA 4단계와 거의 1:1 매핑.
     큰 구조 변경 없이 도입 가능.

  4. 학습(Ledger)이 퍼널 단계별로 세분화되면
     "어느 단계에서 실패하는가"라는 진단이 가능해져
     세대 간 전략 진화의 효율이 크게 올라감.

리스크 중 가장 큰 것(#1 자연스러움 저하)은
프롬프트 가이드로 완화 가능.
```

### 변경 대상 파일

| 파일 | 변경 내용 |
|------|-----------|
| `contracts/schemas/strategy.schema.json` | funnel 서브스키마 추가 |
| `prompts/strategy_prompt.md` | 퍼널 기반 전략 생성 가이드 |
| `prompts/sales-agent-system.md` | 턴별 퍼널 가이드 템플릿 |
| `prompts/hypothesize-system.md` | 퍼널 단계별 학습 반영 가이드 |
| `prompts/judge-system.md` | funnel_progress 보조 지표 추가 |
| `criteria/evaluation-rubric.md` | 퍼널 매핑 해석 가이드 추가 |
| `prompts/reason-system.md` | 퍼널 단계별 패턴 분석 가이드 |
| `architecture/ralph-loop.md` | 퍼널 기반 전략 구조 명시 |

### 영향받는 코드 (Phase 1에서 에이전트가 구현)

| 코드 | 변경 내용 |
|------|-----------|
| `src/agents/sales_agent.py` | system prompt에 퍼널 가이드 삽입 |
| `src/ralph/hypothesize.py` | funnel 필드 포함 전략 생성 |
| `src/evaluation/evaluator.py` | funnel_progress 보조 지표 추출 |
| `src/ralph/reason.py` | 퍼널 단계별 패턴 분석 |
| `src/ralph/ledger.py` (과제B) | 퍼널 단계별 전환율 기록 |

---

## 개선 과제 A+B+C 통합 작업 순서

```
Phase 0 (하네스 문서) — 기존 계획과 병행

  과제 A (병렬 + retry):
    0-19: architecture/ralph-loop.md에 retry 스펙 추가
    0-20: architecture/tech-stack.md에 retry 정책, concurrency 가이드
    0-21: criteria/quality-gates.md에 success_rate 기준 추가

  과제 B (Strategy Ledger):
    0-22: strategy-ledger.schema.json 작성 (contracts/schemas/)
    0-23: architecture/ralph-loop.md에 ledger 스펙 추가 (0-19와 합침)
    0-24: architecture/autoresearch-loop.md에 ledger 참조 추가
    0-25: prompts/hypothesize-system.md에 ledger 활용 가이드 추가

  과제 C (퍼널):
    0-26: contracts/schemas/strategy.schema.json에 funnel 서브스키마 추가
    0-27: prompts/strategy_prompt.md에 퍼널 기반 전략 생성 가이드 추가
    0-28: prompts/sales-agent-system.md에 턴별 퍼널 가이드 추가
    0-29: prompts/judge-system.md에 funnel_progress 보조 지표 추가
    0-30: criteria/evaluation-rubric.md에 퍼널 매핑 해석 가이드 추가
    0-31: prompts/reason-system.md에 퍼널 단계별 패턴 분석 가이드 추가

  의존성:
    0-19~0-21 (A)     → 독립, 즉시 착수 가능
    0-22~0-25 (B)     → 0-19 이후 (ralph-loop.md 공유)
    0-26 (C 스키마)    → 독립
    0-27~0-31 (C 프롬프트) → 0-26 이후 + 기존 0-12(프롬프트 작성) 이후

Phase 1 (코드 생성) 에서 에이전트가 구현할 것:

  과제 A:
    - llm.py: retry + exponential backoff + jitter
    - act.py: task-level retry + 실패 보고
    - evaluate.py: task-level retry + 실패 보고
    - settings.py: max_concurrent 기본값 20
    - loop.py: 실패 stats를 summary에 포함

  과제 B:
    - 신규 ledger.py: Strategy Ledger CRUD + 3-레이어 압축
    - loop.py: ledger 읽기/쓰기 + 세대 결과 append
    - hypothesize.py: ledger 기반 프롬프트 구성
    - learn.py: ledger entry 포맷 생성

  과제 C:
    - hypothesize.py: funnel 필드 포함 전략 생성
    - sales_agent.py: system prompt에 턴별 퍼널 가이드 삽입
    - evaluator.py: funnel_progress 보조 지표 추출
    - reason.py: 퍼널 단계별 패턴 분석
    - ledger.py (과제B): 퍼널 단계별 전환율 기록

  → 이 모든 것이 하네스 문서에 스펙으로 명시되어 있으면
    에이전트가 자동으로 구현함
```

---

상태: 설계 계획 확정 + 개선 과제 A/B/C 추가
작성일: 2026-03-27 (초판), 2026-03-29 (개선 과제 A/B/C 추가)
다음 단계: Phase 0 실행 (1차부터 순서대로, 0-19~0-31 병행)
