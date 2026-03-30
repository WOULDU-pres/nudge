# NUDGE 🧪

**AI가 200명의 가상 고객과 대화하고, 세일즈 전략을 스스로 진화시키는 시뮬레이션 시스템**

> 영업사원이 10년 걸려 쌓는 멘탈맵을, AI 시뮬레이션으로 하루 만에 압축합니다.

[![GitHub](https://img.shields.io/badge/GitHub-WOULDU--pres%2Fnudge-181717?logo=github)](https://github.com/WOULDU-pres/nudge)

## v2 변경사항

- 저장소를 `ralphton-plz` 기준으로 정리하고, 설계 문서(`harness/`)를 루트 구조에 통합했습니다.
- `output/`은 `ralphton` 구현을 기준으로 재정렬했습니다. 즉, 실행 파이프라인/LLM 호출/루프 오케스트레이션은 `ralphton` 버전을 우선 반영했습니다.
- 실행 호환성을 위해 `output/config/default.yaml`, `output/frontend/`, 그리고 일부 typed compatibility 파일(`agents/base.py`, `conversation/turn.py`, `evaluation/schema.py`, `personas/schema.py`, `ralph/evaluate.py`)은 함께 유지했습니다.
- `output/config/settings.py`는 현재 루트 `harness/` 구조에 맞게 경로를 수정했고, 구형/신형 설정명 모두 읽을 수 있게 호환 alias를 추가했습니다.
- `output/scripts/run_simulation.py`는 `--dry-run`과 `--product` 옵션을 지원하도록 보강했습니다.

---

## 문제 정의

| 기존 세일즈 교육의 한계 | NUDGE의 해법 |
|---|---|
| 전략 검증이 느리다 — 실제 고객 반응을 수백 건 모아야 판단 가능 | 200명 가상 고객에게 병렬 시뮬레이션 → 수 분 내 검증 |
| 실패가 비가역적이다 — 한 번 이탈한 고객은 돌아오지 않음 | 가상 고객은 무한 재시도 가능, 실패 비용 = 0 |
| 노하우 전수가 안 된다 — 베테랑의 감(感)은 언어화하기 어려움 | AI가 성공/실패 패턴을 자동 추출하고 전략 문서로 코드화 |

---

## 핵심 아이디어

```
┌─────────────────────────────────────────────────────────────────────┐
│  바깥 루프 (Autoresearch)                                           │
│  strategy_prompt.md 수정 → 시뮬레이션 → 점수 비교 → keep/discard    │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  안쪽 루프 (RALPH)                                            │  │
│  │                                                               │  │
│  │  H(전략 생성) → P(페르소나 선택) → A(대화 실행)                │  │
│  │       → E(Judge 평가) → R(패턴 분석) → L(학습 추출)           │  │
│  │                                                               │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

- **안쪽 루프 (RALPH):** 전략을 생성하고, 가상 고객과 대화하고, 점수를 매기고, 패턴을 분석하여 학습 포인트를 추출
- **바깥 루프 (Autoresearch):** RALPH의 결과를 바탕으로 전략 프롬프트 자체를 수정하며 무한 반복 진화 ([karpathy/autoresearch](https://github.com/karpathy/autoresearch) 패턴)

---

## 프로젝트 구조

```
nudge/
├── harness/                    # 설계도 — 문서, 스키마, 데이터
│   ├── NUDGE-OVERVIEW.md       # 프로젝트 전체 설계 문서
│   ├── contracts/
│   │   ├── product-contract.md # 완성품 정의 (필수 기능, 산출물 형식)
│   │   └── schemas/            # JSON Schema (strategy, evaluation, session 등)
│   ├── criteria/
│   │   ├── evaluation-rubric.md    # 4차원 평가 루브릭
│   │   ├── quality-gates.md        # Phase별 통과 기준
│   │   └── autoresearch-rules.md   # 자율 진화 규칙
│   ├── data/
│   │   └── personas/           # 200명 가상 고객 데이터
│   │       ├── P001/
│   │       │   ├── profile.json    # 구조화 데이터 (성격, 반론 패턴, 트리거)
│   │       │   └── soul.md         # 자연어 캐릭터 시트
│   │       └── ...
│   ├── docs/                   # 이론적 근거 문서
│   ├── scripts/                # 페르소나 생성/변환 스크립트
│   └── specs/                  # 기획 인터뷰 문서
│
├── output/                     # AI가 생성한 실행 코드
│   ├── config/
│   │   ├── default.yaml        # 실행 설정 (모드, 동시성, 턴 수)
│   │   └── product.yaml        # 판매 제품 정보 (데일리 멀티비타민 플러스)
│   ├── src/
│   │   ├── ralph/
│   │   │   ├── evaluate_stage.py # E: Judge 평가 fan-out (ralphton 기준)
│   │   │   ├── evaluate.py       # v2 호환 레이어
│   │   │   ├── reason.py       # R: 상위/하위 대화 패턴 비교 분석
│   │   │   └── learn.py        # L: 학습 포인트 추출 + 전략 수정 권고
│   │   ├── conversation/
│   │   │   ├── engine.py       # 턴 기반 비동기 대화 엔진
│   │   │   ├── turn.py         # 개별 턴 처리
│   │   │   └── rules.py        # 대화 종료 조건 (턴 제한, 키워드 감지)
│   │   ├── evaluation/schema.py # v2 typed 결과 스키마 호환
│   │   ├── personas/schema.py   # v2 typed 페르소나 스키마 호환
│   │   └── llm.py              # 멀티프로바이더 LLM 클라이언트
│   ├── scripts/
│   │   └── run_simulation.py   # 시뮬레이션 실행 진입점
│   ├── frontend/               # React 대시보드
│   │   ├── src/App.tsx         # 대시보드 UI (7개 섹션)
│   │   └── ...
│   ├── runs/                   # 실험 결과 아카이브
│   ├── strategy_prompt.md      # 현재 전략 생성 프롬프트 (v3)
│   └── results.tsv             # 세대별 점수 추이 기록
│
├── decks/                      # 발표 자료
│   └── nudge-mid/              # 중간 발표 슬라이드
└── 발표자료.html               # 통합 발표 파일
```

---

## 핵심 메커니즘

### 1. 페르소나 시스템 (200명)

심리학 기반 **8개 클러스터**로 구성된 가상 고객 풀:

| 클러스터 | 설명 | 핵심 특성 |
|---|---|---|
| `budget_practical` | 예산 민감형 | ROI 계산 중심, 숫자 근거 요구 |
| `health_anxious` | 건강 불안형 | 전문가 권위와 안전성 중시 |
| `hard_sell_resistant` | 강매 거부형 | 압박 감지 시 즉시 이탈 |
| `impulse_curious` | 충동 호기심형 | 신선한 접근에 반응 |
| `evidence_driven` | 근거 중심형 | 논문/데이터 기반 설명 요구 |
| `social_follower` | 사회 추종형 | 후기/트렌드에 영향 |
| `routine_seeker` | 루틴 추구형 | 기존 습관과의 연결 중시 |
| `low_attention` | 주의력 낮음 | 핵심만 간결하게 |

각 페르소나는 `profile.json`(구조화 데이터)과 `soul.md`(자연어 캐릭터 시트)로 구성:

```json
// profile.json 예시 (P001 — 20대 학생, budget_practical)
{
  "cluster_tags": ["budget_sensitive", "roi_driven", "practical"],
  "trust_style": { "responds_to": ["numbers", "roi", "concrete_comparison"] },
  "likely_objections": [{ "trigger": "price", "example": "학생이라 돈이 없어요" }],
  "interest_signals": ["하루 섭취 비용과 며칠분인지 숫자로 재확인"]
}
```

### 2. AIDA 퍼널 기반 대화

3턴(6메시지) 대화에서 마케팅 퍼널 전체를 커버합니다:

```
Turn 1: 🤖 Agent (Attention — hook)      →  👤 Persona (반응)
Turn 2: 🤖 Agent (Interest — 가치 제안)  →  👤 Persona (반론 or 질문)
Turn 3: 🤖 Agent (Desire/Action — CTA)   →  👤 Persona (최종 반응)
```

각 전략은 퍼널 단계별 구체적 옵션을 정의합니다:
- **Attention:** hook_type 5종 (충격형, 데이터형, 일상연결형, 질문형, 스토리형)
- **Interest:** information_depth 5종 (맥락적프레이밍, 기술적우위, 비교데이터 등)
- **Desire:** proof_type 5종 (전문가권위, 사용자후기, ROI계산 등)
- **Action:** cta_style 4종 (시험제안, 한정제안, 소프트CTA, 사회적증거)

### 3. 4차원 평가 시스템

Judge LLM이 각 대화를 독립적으로 채점합니다:

| 차원 | 점수 | 평가 기준 |
|---|---|---|
| Engagement (참여도) | 0-25 | 고객이 대화에 적극적으로 참여했는가? |
| Relevance (적합성) | 0-25 | 페르소나 특성에 맞는 접근이었는가? |
| Persuasion (설득력) | 0-25 | 반론 처리와 가치 전달이 효과적이었는가? |
| Purchase Intent (구매의향) | 0-25 | 실제 구매로 이어질 가능성이 있는가? |
| **Total** | **0-100** | |

보조 지표:
- **Outcome:** converted / interested / neutral / resistant / lost
- **Funnel Progress:** 0(Attention 이탈) ~ 3(Action 도달)
- **한국어 문화 맥락:** "생각해볼게요" = 거절, "괜찮은데요" ≠ 긍정

### 4. 진화 알고리즘 (Autoresearch)

```
1. strategy_prompt.md 수정 (학습 포인트 반영)
2. 시뮬레이션 실행 (전략 3개 × 페르소나 N명)
3. 점수 비교 (이전 best vs 현재)
4. 판정: keep (개선) or discard (퇴보)
5. → 1로 돌아가서 반복
```

누적 학습은 **Strategy Ledger**(전략 원장)에 3-레이어 압축으로 기록되어, LLM context 폭발을 방지합니다.

---

## 빠른 시작

### 사전 요구사항

- Python 3.11+
- Node.js 18+ (대시보드)
- LLM API 키 (Gemini / OpenAI / Anthropic 중 하나 이상)

### 설치

```bash
git clone https://github.com/WOULDU-pres/nudge.git
cd nudge

# 백엔드 (시뮬레이션)
cd output
pip install -r requirements.txt

# 프론트엔드 (대시보드)
cd frontend
npm install
```

### 환경 설정

```bash
# output/.env
GEMINI_API_KEY=your_key_here
# 또는
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

### 실행

```bash
# 1. 단일 시뮬레이션 실행
cd output
RALPHTHON_MODE=DEV python scripts/run_simulation.py

# 2. Dry Run (import 확인 + 설정 출력만)
python scripts/run_simulation.py --dry-run

# 3. 대시보드 실행
cd output/frontend
npm run dev
# → http://localhost:5173
```

### 설정 조정

```yaml
# output/config/default.yaml
mode: TEST              # DEV(10명) / TEST(30명) / DEMO(200명)
strategies_per_run: 3   # 한 번에 생성할 전략 수
conversation_turns: 3   # 대화 라운드 수 (3턴 = 6메시지)
max_concurrent: 20      # 동시 API 호출 수
rate_limit_delay: 0.05  # API 호출 간 대기 시간(초)
```

---

## 대시보드

React + Recharts + Tailwind CSS 기반의 인터랙티브 대시보드입니다.

| 섹션 | 설명 |
|---|---|
| **Executive Hero** | 핵심 발견 한 줄 + KPI 4개 (평균점수, 전환율 병목, 최고 전략, 커버리지) |
| **01 퍼널 분석** | AIDA 퍼널 시각적 깔때기 + 전략별 전환율 비교 + 병목 경고 |
| **02 전략 비교** | 레이더 차트(4차원 비교) + 종합 점수 순위 + 전략별 결과 분포 |
| **03 기법 효과성** | 설득 기법별 사용/미사용 점수 비교 (업그레이드 프레이밍, 위험 제거 등) |
| **04 실험 진화** | 라인 차트 + keep/discard 타임라인 (각 실험의 변경사항과 결과) |
| **05 승패 패턴** | 성공/실패 패턴 분석 + 전략별 인사이트 |
| **06-07 상세 보기** | 접을 수 있는 대화 뷰어 + 평가 테이블 |

---

## 실험 결과 (현재)

```
Baseline:  63.80점 → 최고점: 64.66점 (실험 5)
전략 3개:  건강전문가형(66.4) > 가성비강조형(64.8) > 바쁜직장인형(60.2)
핵심 병목: Desire → Action 전환율 0% (모든 전략 공통)
가장 효과적 기법: 업그레이드 프레이밍 (+20.28점)
미활용 기회: risk_removal (환불보장 기법, 0회 사용)
```

---

## 이론적 기반

| 이론 | 적용 |
|---|---|
| **AIDA 모델** | 퍼널 구조 (Attention → Interest → Desire → Action) |
| **Cialdini 설득 6원칙** | 전략 설계 (상호성, 희소성, 권위, 일관성, 호감, 사회적 증거) |
| **진화 알고리즘** | 전략의 keep/discard 자연선택 메커니즘 |
| **LLM-as-Judge** | 일관된 4차원 채점 시스템 |
| **karpathy/autoresearch** | 프롬프트 자기수정 루프 패턴 |

---

## 비용 추정

| 모드 | 페르소나 수 | 1회 비용 | 용도 |
|---|---|---|---|
| DEV | 10명 | ~$0.05-0.10 | 개발/디버깅 |
| TEST | 30명 | ~$0.15-0.30 | 검증 |
| DEMO | 200명 | ~$1-2 | 발표/데모 |
| Autoresearch 30회(DEMO) | 200명 × 30 | ~$30-60 | 자율 진화 |

---

## 팀

| 이름 | 역할 |
|---|---|
| 주현우 | |
| 임승현 | |
| 이재윤 | |

---

## 라이선스

이 프로젝트는 학술 연구 목적으로 개발되었습니다.
