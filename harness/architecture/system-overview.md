# System Overview

## 한 문장 정의

에이전트가 이 하네스를 읽으면, 설득 시뮬레이션 시스템을 코드로 생성하고,
200명 페르소나 대상 대화 시뮬레이션을 실행하고,
autoresearch 루프로 전략 프롬프트 자체를 밤새 진화시켜
최적 결과를 산출한다.

프롬프트 한 번 → 사람 개입 없이 전부 자율 완료.

---

## 2-레벨 루프 아키텍처

이 시스템은 **바깥 루프**와 **안쪽 루프**, 2개의 루프로 구성된다.

```
┌─────────────────────────────────────────────────────┐
│  외부 루프: autoresearch                            │
│                                                     │
│  strategy_prompt.md 수정                            │
│       │                                             │
│       ▼                                             │
│  ┌─────────────────────────────────────────────┐    │
│  │  내부 루프: RALPH (1회 시뮬레이션)          │    │
│  │                                             │    │
│  │  H (Hypothesize) → 전략 가설 생성          │    │
│  │  P (Plan)        → 페르소나 선택           │    │
│  │  A (Act)         → 대화 시뮬레이션         │    │
│  │  E (Evaluate)    → Judge 채점              │    │
│  │  R (Reason)      → 패턴 분석              │    │
│  │  L (Learn)       → 학습 추출              │    │
│  │                                             │    │
│  │  → avg_score, cluster_coverage 출력         │    │
│  └─────────────────────────────────────────────┘    │
│       │                                             │
│       ▼                                             │
│  점수 비교 → keep / discard                         │
│  results.tsv에 기록                                 │
│  다음 실험 (NEVER STOP)                             │
└─────────────────────────────────────────────────────┘
```

### 외부 루프 (autoresearch)

karpathy/autoresearch 패턴 적용.

- **수정 대상**: `strategy_prompt.md` (전략을 생성하는 프롬프트 자체)
- **고정 대상**: 평가 시스템, 페르소나 데이터, Judge 루브릭
- **판단 기준**: avg_score가 개선되면 keep, 아니면 discard (git reset)
- **핵심 규칙**: NEVER STOP. 사람에게 묻지 않는다. 아이디어가 없으면 더 생각한다.

이것이 "전략을 만드는 프롬프트 자체를 진화시키는" 메타 최적화 레이어다.

### 내부 루프 (RALPH)

nudge 프로젝트의 RALPH Loop을 참고.

- **H (Hypothesize)**: 비싼 모델. 이전 학습 기반으로 새 설득 전략 생성.
- **P (Plan)**: 코드. 200명 중 이번 실행 대상 페르소나 선택.
- **A (Act)**: 싼 모델. Sales Agent(LLM) ↔ Customer Agent(soul.md+LLM) 대화.
- **E (Evaluate)**: 비싼 모델. 4차원 Judge 평가 채점 (각 0-25, total 0-100).
- **R (Reason)**: 비싼 모델. 상위/하위 대화 비교, 패턴 발견.
- **L (Learn)**: 비싼 모델. 재사용 가능한 학습 포인트 추출.

1회 RALPH 실행 = 1회 시뮬레이션 실험.

### 루프 간 관계

```
autoresearch가 진화시키는 것 = strategy_prompt.md
  → 이 프롬프트가 RALPH의 H(Hypothesize) 단계에서 사용됨
  → H가 만든 전략으로 A(Act)에서 대화 실행
  → E(Evaluate)에서 채점
  → R+L에서 패턴 분석 + 학습
  → 결과를 autoresearch가 읽고, 프롬프트를 또 수정
```

즉:
- RALPH는 "주어진 프롬프트로 전략을 만들고 테스트하는" 실행자
- autoresearch는 "그 프롬프트 자체를 개선하는" 진화자

---

## 3단계 실행 흐름 (에이전트가 수행)

에이전트가 MASTER-PROMPT.md를 읽으면 이 3단계를 자율 수행한다.

### Phase 1: 코드 생성
- architecture/, reference/, contracts/ 읽고 전체 구조 이해
- 설득 시뮬레이션 시스템을 Python 코드로 구현
  - RALPH Loop (H→P→A→E→R→L)
  - 멀티프로바이더 LLM 클라이언트
  - 대화 엔진
  - Judge 평가
  - 결과 집계
- 의존성 설치, 기본 동작 확인

### Phase 2: 베이스라인 실행
- strategy_prompt.md 초기 버전으로 첫 시뮬레이션
- 기준 점수(avg_score, cluster_coverage) 확립
- results.tsv에 baseline 기록
- git commit

### Phase 3: autoresearch 루프 (NEVER STOP)
- program.md를 따라 무한 실험 루프
- strategy_prompt.md 수정 → 시뮬레이션 → 점수 비교 → keep/discard
- 사람이 수동 중단할 때까지 계속

---

## 핵심 개체 (Ontology)

| 개체 | 유형 | 설명 |
|------|------|------|
| Harness | 설계도 | 이 폴더 전체. 에이전트에게 주는 것. |
| Agent | 외부 실행자 | Claude Code, Codex 등. 하네스를 읽고 완성품을 생성. |
| Product | 생성물 | 에이전트가 만드는 코드 (src/, config/, scripts/). |
| RALPH Loop | 내부 루프 | 전략 생성 → 대화 → 평가 → 분석 → 학습. |
| Autoresearch Loop | 외부 루프 | 전략 프롬프트 자체를 진화시키는 메타 루프. |
| Persona | 고정 데이터 | 200명. profile.json + soul.md. 절대 수정 금지. |
| Strategy Prompt | 진화 대상 | autoresearch가 수정하는 유일한 파일. |

---

## 산출물 흐름

```
사용자 → [프롬프트 1개] → 에이전트

에이전트:
  Phase 1 → 코드 생성 (output/ 디렉토리)
  Phase 2 → 베이스라인 점수 확립 → results.tsv 첫 행
  Phase 3 → N회 실험 반복 → results.tsv N행 누적
           → 최종 산출물:
              - 최적 strategy_prompt.md
              - 최고 점수 전략
              - 진화 과정 로그 (results.tsv)
              - 클러스터별 분석
              - (선택) 웹 대시보드
```

---

## 하네스 ≠ 완성품

- **하네스**: 에이전트에게 주는 설계도. 문서 + 스키마 + 데이터 + 지시서.
- **완성품**: 에이전트가 하네스를 읽고 생성하는 코드 + 실행 결과.

이 폴더에는 코드가 (거의) 없다.
코드는 에이전트가 만든다.
