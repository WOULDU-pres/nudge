# Autoresearch Rules — Keep/Discard 판단 기준

autoresearch 외부 루프에서 실험 결과를 keep할지 discard할지 판단하는 규칙.

---

## 기본 규칙

### Keep (브랜치 전진)

| 조건 | 판정 |
|------|------|
| avg_score가 이전보다 2점 이상 상승 | **keep** |
| avg_score 동일(±2), cluster_coverage가 5% 이상 상승 | **keep** |

### Discard (git reset --hard HEAD~1)

| 조건 | 판정 |
|------|------|
| avg_score가 이전보다 하락 (2점 초과) | **discard** |
| avg_score 동일(±2), cluster_coverage도 동일(±5%) | **discard** |
| 실행 crash (결과 없음) | **discard** |

### 노이즈 마진

LLM-as-Judge 특성상 동일 입력에도 ±2점 편차가 발생할 수 있다.
따라서:

- **avg_score ±2 이내 변동**은 "동일"로 간주
- **cluster_coverage ±5% 이내 변동**은 "동일"로 간주

이 마진은 DEV 모드(10명)에서는 더 클 수 있다.
DEMO 모드(200명)에서는 평균 효과로 노이즈가 줄어든다.

---

## results.tsv 기록 형식

```
commit	avg_score	cluster_coverage	best_strategy	status	description
a1b2c3d	45.30	62.5	strategy-roi	keep	baseline prompt
b2c3d4e	52.10	75.0	strategy-empathy	keep	added empathy-first approach
c3d4e5f	41.20	50.0	strategy-pressure	discard	loss aversion too aggressive
d4e5f6g	0.00	0.0	none	crash	JSON parse error in strategy gen
```

모든 실험을 기록한다. keep이든 discard든 crash든.
이력이 있어야 에이전트가 패턴을 파악할 수 있다.

---

## Crash 처리

실행이 crash하면:

1. `tail -n 50 run.log`로 에러 확인
2. strategy_prompt.md의 문제인 경우:
   - JSON 출력 형식을 깨뜨리는 지시가 있는지 확인
   - git reset --hard HEAD~1
   - 다른 방향으로 수정
3. 코드의 문제인 경우:
   - Phase 1으로 돌아가 코드 수정 (비상시에만)
   - 일반적으로는 strategy_prompt.md만 수정

---

## 정체 (Plateau) 처리

5회 연속 discard가 되면:

1. results.tsv 전체를 다시 읽는다
2. keep된 실험들의 공통점을 분석한다
3. 아직 시도하지 않은 급진적 변경을 시도한다:
   - 프롬프트 구조 자체 변경
   - 완전히 새로운 전략 유형 추가
   - "반전략" 실험 (일부러 다른 방향)
4. 그래도 5회 더 실패하면:
   - 가장 높았던 keep 버전으로 돌아간다
   - 다른 축으로 최적화 (cluster_coverage 중심)

---

## git 브랜치 운용

```bash
# 실험 시작 전
git checkout -b autoresearch/<tag>

# keep 시
# (아무것도 안 함 — 이미 커밋됨, 브랜치가 전진)

# discard 시
git reset --hard HEAD~1

# 최종 결과를 main에 반영하고 싶으면 (사람이 수동으로)
git checkout main
git merge autoresearch/<tag>
```

---

## 메트릭 우선순위

1. **avg_score** — 주 최적화 대상
2. **cluster_coverage** — 보조 (avg_score 동일 시 tiebreaker)
3. **best_strategy_score** — 참고용 (최적화 대상 아님)

avg_score가 높아도 cluster_coverage가 극히 낮으면
특정 클러스터만 잘하는 편향된 전략일 수 있다.
이상적으로는 둘 다 높은 것.
