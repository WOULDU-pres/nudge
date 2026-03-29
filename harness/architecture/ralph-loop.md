# RALPH Loop — 내부 루프 상세

RALPH = Hypothesize → Plan → Act → Evaluate → Reason → Learn

nudge 프로젝트의 RALPH Loop 구조를 참고하되, 우리 방식으로 개선한다.
1회 RALPH 실행 = 1회 시뮬레이션 실험.

---

## 전체 흐름

```
strategy_prompt.md (현재 버전)
    │
    ▼
H (Hypothesize) ──── 비싼 모델
    │  전략 N개 생성
    ▼
P (Plan) ──────────── 코드 (LLM 불필요)
    │  이번 실행 대상 페르소나 선택
    ▼
A (Act) ───────────── 싼 모델 × 2 (에이전트 + 고객)
    │  대화 시뮬레이션 (전략 × 페르소나)
    ▼
E (Evaluate) ──────── 비싼 모델
    │  Judge가 4차원 채점
    ▼
R (Reason) ─────────── 비싼 모델
    │  상위/하위 대화 비교, 패턴 발견
    ▼
L (Learn) ─────────── 비싼 모델
    │  재사용 학습 포인트 추출
    ▼
결과 출력: avg_score, cluster_coverage, best_strategy
```

---

## H (Hypothesize) — 전략 가설 생성

### 역할
strategy_prompt.md를 system prompt로 사용하여,
제품에 맞는 설득 전략 N개를 생성한다.

### 입력
- `strategy_prompt.md` (system prompt)
- `product.yaml` 또는 하드코딩된 제품 정보 (user message)
- 이전 RALPH 사이클의 학습 결과 (있는 경우)
- `strategy_ledger.json` (전 세대 전략 히스토리, 있는 경우)

### 출력
- `Strategy[]` — contracts/schemas/strategy.schema.json 준수

```json
[
  {
    "strategy_id": "strategy-roi-proof",
    "hypothesis": "가격 대비 가치를 숫자로 보여주면 합리적 구매자에게 효과적",
    "approach": "하루 500원, 커피 한 잔보다 싸다는 프레이밍",
    "opening_style": "건강 관련 최근 데이터 공유로 시작",
    "objection_handling": "30일 환불 보장 강조",
    "tone": "친절하지만 데이터 중심"
  }
]
```

### 사용 모델
비싼 모델 (RALPHTHON_MODEL_EXPENSIVE). 창의적 전략 생성에는 추론 능력 필요.

### 기본값
`STRATEGIES_PER_RUN=3` (환경변수로 조정 가능)

---

## P (Plan) — 페르소나 선택

### 역할
이번 실행에서 테스트할 페르소나를 선택한다.

### 입력
- `data/personas/` 전체 (최대 200명)
- 환경변수 `RALPHTHON_MODE` (DEV=10, TEST=50, DEMO=200)

### 출력
- 선택된 페르소나 목록 (ID 순 정렬)

### 구현
LLM 호출 불필요. 순수 코드.
- DEV: 처음 10명 (P001~P010)
- TEST: 처음 50명 (P001~P050)
- DEMO: 전체 200명

### 향후 확장 가능
- 클러스터별 균등 샘플링
- 이전 실험에서 점수가 낮았던 클러스터 페르소나 우선 선택
- 랜덤 샘플링

---

## A (Act) — 대화 시뮬레이션

### 역할
각 전략 × 각 페르소나 조합으로 세일즈 대화를 시뮬레이션한다.

### 입력
- 전략 1개 (H에서 생성)
- 페르소나 1명 (P에서 선택)
- 제품 정보

### 대화 구조

```
턴 0: Sales Agent → 첫 인사 + 제품 소개
턴 1: Customer Agent → 반응
턴 2: Sales Agent → 응답
턴 3: Customer Agent → 반응
턴 4: Sales Agent → 응답
턴 5: Customer Agent → 최종 반응
```

기본 3턴 왕복 (`CONVERSATION_TURNS=3`).

### Sales Agent
- system prompt: `prompts/sales-agent-system.md` + 전략 정보
- 모델: 싼 모델 (RALPHTHON_MODEL_CHEAP)

### Customer Agent
- system prompt: `prompts/customer-agent-system.md` + 해당 페르소나의 soul.md
- 모델: 싼 모델 (RALPHTHON_MODEL_CHEAP)

### 출력
- `ConversationSession` — contracts/schemas/conversation-session.schema.json 준수

```json
{
  "session_id": "conv-strategy-roi-P001",
  "strategy_id": "strategy-roi-proof",
  "persona_id": "P001",
  "turns": [
    {"role": "agent", "content": "안녕하세요! 건강 관리..."},
    {"role": "persona", "content": "음... 멀티비타민은..."},
    {"role": "agent", "content": "좋은 질문이세요..."},
    {"role": "persona", "content": "가격이 좀..."},
    {"role": "agent", "content": "하루 500원이면..."},
    {"role": "persona", "content": "그 정도면..."}
  ],
  "ended_by": "turn_limit"
}
```

### 동시성
`asyncio.Semaphore(MAX_CONCURRENT)` — 기본 20 (유료 Gemini 기준).
전략 3개 × 페르소나 10명 = 30건을 동시성 20으로 처리.

### 재시도
retry with exponential backoff (llm.py 레이어 + task-level 2회 재시도)

---

## E (Evaluate) — Judge 채점

### 역할
대화 transcript를 읽고 4차원으로 채점한다.

### 입력
- 대화 transcript (A에서 생성)
- 페르소나 프로필 (문맥 참고)

### 출력
- `EvaluationResult` — contracts/schemas/evaluation-result.schema.json 준수

```json
{
  "session_id": "conv-strategy-roi-P001",
  "strategy_id": "strategy-roi-proof",
  "persona_id": "P001",
  "scores": {
    "engagement": 18,
    "relevance": 22,
    "persuasion": 15,
    "purchase_intent": 12,
    "total": 67
  },
  "outcome": "interested",
  "reason": "가격 대비 가치 프레이밍이 예산 민감형 페르소나에게 효과적"
}
```

### 4차원 평가 기준

| 차원 | 범위 | 평가 내용 |
|------|------|----------|
| engagement | 0-25 | 고객이 대화에 관심을 보였는가? |
| relevance | 0-25 | 에이전트가 고객 상황에 맞게 대응했는가? |
| persuasion | 0-25 | 반론을 효과적으로 다뤘는가? |
| purchase_intent | 0-25 | 구매/관심 방향으로 기울었는가? |
| **total** | **0-100** | **합계** |

### outcome 분류

| 결과 | 의미 |
|------|------|
| converted | 구매 의사 표현 |
| interested | 관심 표현, 추가 질문 |
| neutral | 중립적 반응 |
| resistant | 명시적 거부 |
| lost | 대화 이탈 |

### 사용 모델
비싼 모델. temperature=0.1 (일관성 유지).

### Judge 시스템 프롬프트
`prompts/judge-system.md` 참조. `criteria/evaluation-rubric.md`의 기준을 반영.

---

## R (Reason) — 패턴 분석

### 역할
상위 점수 대화와 하위 점수 대화를 비교하여,
무엇이 잘 되었고 무엇이 안 되었는지 패턴을 발견한다.

### 입력
- E에서 나온 전체 EvaluationResult[]
- 상위 N개 + 하위 N개 대화 transcript

### 출력
- 패턴 분석 결과 (자연어 + 구조화)

```json
{
  "winning_patterns": [
    "ROI 프레이밍이 budget_practical 클러스터에서 20점 이상 높음",
    "첫 턴에서 공감 표현 후 데이터를 제시한 전략이 상위 점수"
  ],
  "losing_patterns": [
    "높은 압박 톤이 hard_sell_resistant 클러스터에서 일관되게 실패",
    "긴 오프닝이 low_attention 클러스터에서 이탈 유발"
  ],
  "cluster_insights": {
    "ROI": "숫자 기반 접근이 강하지만 감정적 연결 부족하면 천장 있음",
    "EMPATHY": "공감형 접근이 안정적이지만 최고 점수까지는 잘 안 감"
  }
}
```

### 사용 모델
비싼 모델. 비교 분석에는 추론 능력 필요.

### 시스템 프롬프트
`prompts/reason-system.md` 참조.

---

## L (Learn) — 학습 추출

### 역할
R의 패턴 분석에서 재사용 가능한 학습 포인트를 추출한다.
다음 RALPH 사이클의 H(Hypothesize)에서 참고할 수 있는 형태로.

### 입력
- R의 패턴 분석 결과
- 현재 strategy_prompt.md

### 출력
- 학습 포인트 목록

```json
{
  "learnings": [
    "budget_practical 클러스터에는 가격을 초반에 언급하면 engagement 상승",
    "hard_sell_resistant 클러스터에는 첫 턴에서 질문형 오프닝이 효과적",
    "모든 클러스터에서 2턴 이내에 핵심 가치를 전달해야 이탈 감소"
  ],
  "recommended_prompt_changes": [
    "전략 설계 원칙에 '고객 유형별 차별화' 항목 추가 제안",
    "톤 가이드에 '첫 턴은 가벼운 질문으로' 원칙 추가 제안"
  ]
}
```

### 사용 모델
비싼 모델.

### 시스템 프롬프트
`prompts/learn-system.md` 참조.

### autoresearch와의 연결

L의 출력은 autoresearch 외부 루프에서 strategy_prompt.md를
수정할 때 참고 자료로 사용된다.

---

## RALPH 1회 실행의 전체 산출물

```
runs/<run_id>/
├── summary.json           ← 전체 집계 (avg_score, cluster_coverage 등)
├── strategies.json        ← H가 생성한 전략들
├── transcripts/           ← A가 생성한 대화들
│   ├── strategy-roi/
│   │   ├── P001.json
│   │   ├── P002.json
│   │   └── ...
│   └── strategy-empathy/
│       ├── P001.json
│       └── ...
├── evaluations.json       ← E가 채점한 결과들
├── reason.json            ← R의 패턴 분석
└── learnings.json         ← L의 학습 포인트
```

---

## Strategy Ledger 연동

### 개요
RALPH 1회 실행 완료 시 `strategy_ledger.json`에 세대 결과를 append한다.

### L → H 연결 (ledger 경유)
L이 생성한 learnings가 ledger에 누적되고, H는 ledger에서 3-레이어 압축 컨텍스트를 받는다.
이를 통해 세대 간 학습이 유실되지 않고 축적된다.

### 3-레이어 압축 구조

| 레이어 | 내용 | 토큰 예산 |
|--------|------|-----------|
| Layer 1 | `cumulative_insights` — 전 세대 누적 통찰 | ~500 토큰 |
| Layer 2 | 최근 3세대 상세 결과 (전략, 점수, 패턴) | ~1500 토큰 |
| Layer 3 | 과거 세대 1줄 요약 | ~50 토큰/세대 |

### cumulative_insights 갱신 규칙

**never_repeat** (실패 패턴):
- 3세대 연속 하위 25%에 해당하는 전략/접근법
- 또는 특정 클러스터에서 3세대 연속 40점 미만

**proven_effective** (성공 패턴):
- 3세대 연속 상위 25%에 해당하는 전략/접근법
- 또는 특정 클러스터에서 3세대 연속 60점 이상

### 퍼널 단계별 전환율
`funnel_progress` 분포를 `strategies_tried` 내에 포함하여 퍼널 단계별 전환율을 기록한다.
(converted / interested / neutral / resistant / lost 비율)

### 스키마
`contracts/schemas/strategy-ledger.schema.json` 참조.

---

## 비용 추정 (참고)

| 모드 | 전략 수 | 페르소나 수 | 대화 API 호출 | Judge 호출 | 총 호출 |
|------|---------|-----------|-------------|-----------|--------|
| DEV | 3 | 10 | ~60 (싼) | ~30 (비싼) | ~100 |
| TEST | 3 | 50 | ~300 (싼) | ~150 (비싼) | ~500 |
| DEMO | 3 | 200 | ~1200 (싼) | ~600 (비싼) | ~2000 |

H, R, L은 각 1회 = 총 3회 (비싼).
DEMO 모드 1회 실행 ≈ 2000+ API 호출.
