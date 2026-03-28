# Autoresearch Loop — 외부 루프 상세

karpathy/autoresearch 패턴을 설득 시뮬레이션에 적용한 메타 최적화 루프.

핵심 통찰: RALPH 내부 루프는 "주어진 프롬프트로 전략을 만들고 테스트"한다.
autoresearch는 "그 프롬프트 자체를 진화시킨다."

---

## autoresearch 원본과의 대응

| autoresearch (Karpathy) | Ralphthon |
|------------------------|-----------|
| prepare.py (고정) | 평가 시스템(고정) + personas + judge rubric |
| train.py (에이전트가 수정) | strategy_prompt.md |
| program.md (사람이 수정) | program.md |
| val_bpb (메트릭) | avg_score + cluster_coverage |
| results.txt | results.tsv |
| git branch + keep/discard | 동일 |

---

## 루프 구조

```
autoresearch/<tag> 브랜치에서:

LOOP FOREVER:

  1. 현재 상태 파악
     - git log --oneline -5
     - tail -10 results.tsv
     - cat strategy_prompt.md

  2. 가설 수립
     - 이전 실험 결과에서 약한 부분 파악
     - "이렇게 바꾸면 이 클러스터 점수가 오를 것" 가설 설정

  3. strategy_prompt.md 수정
     - 가설에 따라 프롬프트 변경
     - 변경 사항을 commit message에 기록

  4. git commit
     - git add strategy_prompt.md
     - git commit -m "experiment: <가설 설명>"

  5. 시뮬레이션 실행
     - python scripts/run_simulation.py > run.log 2>&1

  6. 결과 확인
     - grep "^avg_score:" run.log → 새 점수
     - grep이 비어있으면 crash → tail run.log → 수정

  7. 판정
     - 새 avg_score > 이전 avg_score → keep
     - 새 avg_score ≤ 이전 avg_score → discard

  8. 후처리
     - keep: 브랜치 전진. "이 방향이 맞다."
     - discard: git reset --hard HEAD~1. "이 시도는 실패."

  9. results.tsv에 기록
     - commit hash, avg_score, cluster_coverage, best_strategy, status, description

  10. 다음 실험으로
```

---

## 수정 가능 / 수정 불가

### 수정 가능 (에이전트가 실험마다 바꾸는 것)

**`strategy_prompt.md`** — 이것이 유일한 수정 대상.

수정 가능한 내용:
- 전략 설계 원칙
- 전략 유형 가이드
- 프레이밍 기법 지시
- 심리학적 메커니즘 지시
- 고객 유형별 접근 지시
- 대화 톤/스타일 지시
- 반론 대응 프레임워크
- 예시 추가/제거

수정 불가한 내용:
- JSON 출력 형식 (evaluate가 파싱해야 하므로)

### 수정 불가 (고정된 것)

| 파일 | 이유 |
|------|------|
| 코드 (src/, scripts/) | Phase 1에서 생성 후 고정 |
| data/personas/ | 평가 일관성 |
| prompts/judge-system.md | Judge 기준 일관성 |
| criteria/evaluation-rubric.md | 채점 기준 일관성 |
| results.tsv 형식 | 파싱 호환성 |

---

## 메트릭

### 주 메트릭: avg_score
- 전체 페르소나 평균 설득 점수 (0-100)
- keep/discard 판단의 기준

### 보조 메트릭: cluster_coverage
- 8개 클러스터 중 평균 60점 이상인 비율 (0-100%)
- 특정 클러스터만 잘하고 나머지는 못하는 전략을 걸러냄

### 참고 메트릭: best_strategy_score
- 가장 높은 점수를 받은 개별 전략의 평균
- 전략 간 편차 파악

---

## keep/discard 기준 (상세)

`criteria/autoresearch-rules.md` 참조. 요약:

| 상황 | 판정 | 이유 |
|------|------|------|
| avg_score 상승 | keep | 개선됨 |
| avg_score 동일, cluster_coverage 상승 | keep | 클러스터 균형 개선 |
| avg_score 동일, cluster_coverage 동일 | discard | 변화 없음 = 의미 없음 |
| avg_score 하락 | discard | 악화됨 |
| crash (결과 없음) | discard | 프롬프트가 JSON 깨뜨림 |

---

## 실험 아이디어 단계별 가이드

에이전트가 autoresearch 루프에서 시도할 실험 방향.

### 초기 (1~5번 실험)
- 전략 유형 가이드를 더 구체적으로
- 고객 유형별 맞춤 접근 추가
- "하지 마라" 목록 (안 좋은 패턴) 추가

### 중급 (6~15번 실험)
- Cialdini 6원칙 직접 프롬프트에 포함
- 반론 대응 프레임워크 (FEEL-FELT-FOUND 등)
- 한국 소비자 문화적 특성 반영

### 고급 (16~30번 실험)
- 클러스터별 차별화 전략 지시
- 멀티턴 흐름 설계 (턴별 목표 지시)
- 프레이밍 효과 실험
- 앵커링 기법 지시

### 급진적 (30번 이후)
- 프롬프트 구조 자체 변경 (목록 → 서사, 규칙 → 예시)
- 전략 개수 조정 실험
- 반전략 실험 (일부러 실패할 전략으로 Judge 반응 학습)
- 이전 실험 결과를 프롬프트에 직접 삽입

---

## autoresearch vs RALPH: 진화 대상 차이

```
RALPH 내부 루프:
  "이 프롬프트로 전략 3개를 만들면, 어떤 게 제일 잘 먹히나?"
  → 전략 자체를 비교

autoresearch 외부 루프:
  "이 프롬프트를 이렇게 바꾸면, 더 좋은 전략이 나오나?"
  → 전략을 만드는 프롬프트를 비교
```

이게 메타 최적화의 핵심이다.
전략의 품질은 프롬프트의 품질에 달려 있고,
프롬프트의 품질은 autoresearch가 진화시킨다.

---

## 노이즈 관리

autoresearch 원본(val_bpb)은 수학적으로 결정론적이지만,
우리의 avg_score는 LLM-as-Judge이므로 노이즈가 있다.

### 노이즈 완화 방법

1. **Judge temperature=0.1**: 채점 일관성 유지
2. **200명 평균**: 개별 편차가 평균에서 상쇄
3. **고정 페르소나**: 같은 입력 → 비슷한 결과 (완전 동일은 아님)
4. **(선택) 2-3회 반복 평균**: 동일 실험을 여러 번 돌려 평균

### 허용 노이즈 범위

avg_score ±2 이내의 변동은 의미 없는 것으로 간주.
→ keep 기준을 "개선"이 아니라 "2점 이상 개선"으로 설정하는 것도 가능.
(`criteria/autoresearch-rules.md`에서 정의)
