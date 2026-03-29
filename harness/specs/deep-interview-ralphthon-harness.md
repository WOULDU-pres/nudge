# Deep Interview Spec: Ralphthon Harness (autoresearch + nudge 참고)

## Metadata
- Rounds: 10
- Final Ambiguity: 17%
- Type: greenfield (nudge를 참고하되 독립 프로젝트)
- Status: PASSED
- Generated: 2026-03-27

## Clarity Breakdown

| Dimension        | Score | Weight | Weighted |
|------------------|-------|--------|----------|
| Goal             | 0.95  | 40%    | 0.380    |
| Constraints      | 0.70  | 30%    | 0.210    |
| Success Criteria | 0.80  | 30%    | 0.240    |
| **Total Clarity**|       |        | **0.830**|
| **Ambiguity**    |       |        | **17.0%**|

## Goal

에이전트에게 프롬프트 하나를 주면, 에이전트가 자율적으로:
1. nudge를 참고한 설득 시뮬레이션 시스템을 코드로 구현하고
2. 실제로 실행해서 200명 페르소나와 대화 시뮬레이션을 돌리고
3. autoresearch 패턴으로 세대별 전략(프롬프트 자체)을 진화시키고
4. 최종 결과(점수 개선 추이 + 최적 전략 + 분석)를 산출

이 전부가 "프롬프트 한 번 → 사람 개입 없이 자율 완료"로 끝난다.

### 한 문장 정의

> 하네스 = "에이전트가 읽고, 설득 시뮬레이션 완성품을 만들고,
> 밤새 autoresearch로 전략을 진화시켜 최적 결과까지 산출하는 설계도"

## Constraints

### nudge에서 참고하는 것 (전부 참고, 우리 방식으로 개선)

| nudge 요소 | 참고 방식 | 우리 개선 |
|-----------|----------|----------|
| A. 디렉토리 구조 (config/src/scripts/frontend/) | 구조 유지 | 하네스 문서 디렉토리 추가 |
| B. RALPH Loop 6단계 (H→P→A→E→R→L) | 루프 구조 참고 | + autoresearch 외부 루프 (메타 진화) |
| C. 모델 분리 (싼 모델=대화, 비싼 모델=분석) | 패턴 채택 | 멀티 프로바이더 지원 |
| D. 규칙 기반 고객 에이전트 | 참고 | soul.md 기반 LLM 고객 에이전트로 대체/선택 |
| E. 5차원 평가 체계 | 체계 참고 | 우리 Judge 루브릭으로 조정 |
| F. OpenRouter LLM 라우팅 | 참고 | 직접 API + OpenRouter 둘 다 지원 |
| G. 페르소나 스키마 (enum 조합) | 참고 | 200명 soul.md 깊은 캐릭터로 대체 |

### 하네스 자체의 제약

- 하네스는 코드가 아니라 "문서 + 스키마 + 데이터 + 지시서"
- 에이전트(Claude Code, Codex 등)가 이것만 읽고 완성품을 생성
- 생성된 완성품이 자율적으로 실험까지 수행
- API 키는 환경변수로 제공 (하네스에 하드코딩 X)

## Non-Goals

- nudge를 fork하거나 PR을 보내는 것이 아님
- nudge와 동일한 코드를 만드는 것이 아님
- 수동으로 실험을 돌리는 시스템이 아님 (자율 완료 필수)

## Acceptance Criteria

- [ ] 에이전트가 하네스만 읽고, 사람 개입 없이 완성품 코드를 생성
- [ ] 생성된 코드가 실제로 실행되어 대화 시뮬레이션 동작
- [ ] RALPH Loop (전략생성→대화→평가→분석→학습) 동작
- [ ] autoresearch 외부 루프 동작 (전략 프롬프트 자체 진화)
- [ ] 200명 soul.md 페르소나 기반 깊은 대화
- [ ] 세대별 점수 개선 추이 기록 (results.tsv 또는 동등)
- [ ] 최종 산출물: 최적 전략 + 진화 과정 + 분석 결과
- [ ] 웹 대시보드 (히트맵, 전략 비교 등) — 선택적이지만 목표에 포함

## Assumptions Exposed & Resolved

| Assumption | Challenge | Resolution |
|-----------|-----------|------------|
| nudge에 PR을 올린다 | "완성품을 만드는 게 아니라 하네스를 만드는 것 아닌가?" | 맞다. PR이 아니라 독립 하네스. nudge는 참고만. |
| autoresearch가 필요한가? | "RALPH Loop도 이미 세대별 학습하지 않나?" | RALPH는 전략만 진화. autoresearch는 전략을 만드는 프롬프트 자체를 진화. |
| 코드 생성까지가 하네스 범위 | "시뮬레이션 실행도 포함?" | 예. 코드 생성 + 실행 + 진화 + 결과 산출 전부 자율 완료. |
| 사람이 단계별 확인 | "프롬프트 한 번이면 끝?" | 예. 프롬프트 한 번 → 끝. 사람 개입 없음. |

## Key Entities (Ontology)

| Entity | Type | Fields | Relationships |
|--------|------|--------|---------------|
| Harness | core | MASTER-PROMPT.md, architecture/, loops/, contracts/, data/, criteria/ | → Agent가 읽음 |
| Agent | external | Claude Code, Codex 등 | Harness를 읽고 → Product를 생성 |
| Product | core | src/, config/, scripts/, frontend/ | Agent가 생성, Simulation이 실행 |
| Simulation | core | 대화 엔진, 전략 실행, 페르소나 매칭 | Product의 일부, 결과를 Evaluation에 전달 |
| Autoresearch Loop | core | program.md, results.tsv, keep/discard | Simulation을 반복 실행, 프롬프트 진화 |
| Persona Soul | data | soul.md, profile.json (200명) | Simulation에서 고객 역할 |
| Nudge | reference | src/ralph/, src/agents/, config/personas.yaml | 구조 참고용, 코드 복사 아님 |

## 2-레벨 아키텍처

```
하네스 (설계도)
  │
  ▼
에이전트 (실행자)
  │
  ├─ 1단계: 코드 생성
  │   └─ nudge 참고하여 시뮬레이션 시스템 구현
  │      ├─ RALPH 내부 루프 (H→P→A→E→R→L)
  │      ├─ 200명 soul.md 페르소나
  │      ├─ 멀티 프로바이더 LLM 클라이언트
  │      └─ 평가 + 분석 시스템
  │
  ├─ 2단계: 베이스라인 실행
  │   └─ 첫 시뮬레이션으로 기준 점수 확립
  │
  └─ 3단계: autoresearch 루프 (밤새)
      └─ strategy_prompt.md 수정 → 시뮬 실행 → 점수 비교
         → keep/discard → 반복 (NEVER STOP)
```

## Interview Transcript

<details>
<summary>Full Q&A (10 rounds)</summary>

### Round 1 — Goal
Q: nudge 레포와 당신의 관계가 정확히 뭔가요?
A: nudge = 팀 공동 레포. 내가 담당 파트를 PR로 올려서 합침

### Round 2 — Goal
Q: nudge에서 당신이 담당하는 파트는?
A: autoresearch 외부 루프 + 페르소나 심화 둘 다

### Round 3 — Constraints
Q: 기존 코드 수정 범위는?
A: 기존 코드를 많이 바꿔도 OK — 더 좋은 버전을 제시하는 것

### Round 4 — Goal (Contrarian)
Q: nudge의 RALPH Loop만으로 부족한 게 정확히 뭔가요?
A: RALPH는 전략만 진화. autoresearch는 전략을 만드는 '프롬프트 자체'를 진화시킴

### Round 5 — Success Criteria + 방향 전환
Q: PR 성공 기준?
A: (방향 전환) PR이 아니라 나만의 하네스를 만들되, nudge 구조를 참고.
   완성품을 만드는 게 아니라 완성품을 만드는 프롬프트가 들어갈 하네스.

### Round 6 — Goal
Q: 하네스가 존재하면 에이전트는 뭘 하게 되나요?
A: 우리가 개발하고자 했던 계획 방향에 맞는 코드. nudge 구조 참고 가능.

### Round 7 — Goal (Simplifier)
Q: 완성품이란 정확히?
A: nudge 수준의 완성품 (코드+UI+대시보드)

### Round 8 — Constraints
Q: nudge에서 참고할 것과 버릴 것은?
A: 전부 참고하되, 우리 방식으로 개선해서 적용

### Round 9 — Success Criteria
Q: 완성품의 최소 요건?
A: 코드뿐 아니라 시뮬레이션까지 전부 진행. 세대별 진화 작업까지 모두 완료.

### Round 10 — Success Criteria
Q: 프롬프트 한 번 → 끝?
A: 예. 중간에 사람 개입 없이 전부 자율 완료.

</details>
