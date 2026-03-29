# Product Contract — 에이전트가 만들 완성품 정의

에이전트가 하네스를 읽고 생성해야 하는 완성품의 최종 사양.

---

## 완성품이란

에이전트가 Phase 1에서 생성하는 코드 + 설정 + 스크립트.
이 코드가 Phase 2에서 실행되고, Phase 3에서 autoresearch에 사용된다.

---

## 필수 기능

### 1. RALPH Loop (내부 루프)

전략 생성 → 대화 시뮬레이션 → 평가 → 분석 → 학습의 순환.

- H: strategy_prompt.md 기반 전략 N개 생성 (LLM)
- P: 페르소나 선택 (코드)
- A: Sales Agent ↔ Customer Agent 대화 (LLM × 2)
- E: Judge 4차원 채점 (각 0-25, total 0-100) (LLM)
- R: 상위/하위 비교 패턴 분석 (LLM)
- L: 학습 포인트 추출 (LLM)

1회 실행 시 출력:
```
avg_score: <0-100>
cluster_coverage: <0-100>
best_strategy: <strategy-id>
```

### 2. 멀티프로바이더 LLM 클라이언트

환경변수로 프로바이더/모델 선택:
- Gemini (기본)
- OpenAI
- Anthropic
- Ollama (로컬)

싼 모델 / 비싼 모델 분리 지원.

### 3. soul.md 기반 고객 에이전트

- `data/personas/P001/soul.md`를 system prompt에 삽입
- LLM이 해당 인물처럼 반응
- 규칙 기반이 아닌 LLM 기반

### 4. 대화 엔진

- 턴 기반 (기본 3턴 왕복)
- 종료 조건: 턴 수 제한 / 키워드 감지
- asyncio 기반 병렬 실행

### 5. Judge 평가

- 4차원 채점 (engagement, relevance, persuasion, purchase_intent)
- 각 0-25, total 0-100
- outcome 분류 (converted/interested/neutral/resistant/lost)
- 판정 근거 문장
- JSON 출력

### 6. 결과 집계

- avg_score: 전체 평균
- cluster_coverage: 60점 이상 클러스터 비율
- 클러스터별 평균
- outcome 분포

### 7. 실험 실행 스크립트

- `scripts/run_simulation.py`: RALPH 1회 실행
  - stdout에 grep 가능한 형식으로 결과 출력
  - `runs/<run_id>/`에 상세 결과 저장

### 8. autoresearch 실행 스크립트

- `scripts/run_autoresearch.py` 또는 에이전트가 직접 루프
  - strategy_prompt.md 수정 → 시뮬 실행 → 비교 → keep/discard
  - results.tsv 기록

---

## 선택적 기능

### 웹 대시보드 (있으면 좋음)

- FastAPI + HTML 또는 정적 HTML
- 히트맵: 전략 × 클러스터 점수
- 전략 비교
- 대화 transcript 열람
- 실험 로그 (results.tsv) 시각화

### Reason/Learn 보고서

- R/L 출력을 정리된 markdown으로 저장
- 다음 실험에서 참고 가능한 형태

---

## 산출물 구조

```
output/
├── config/
│   ├── settings.py
│   ├── default.yaml
│   └── product.yaml
├── src/
│   ├── llm.py
│   ├── agents/ (sales_agent.py, customer_agent.py)
│   ├── conversation/ (engine.py, turn.py, rules.py)
│   ├── evaluation/ (evaluator.py, aggregator.py, schema.py)
│   ├── ralph/ (loop.py, hypothesize.py, plan.py, act.py, reason.py, learn.py)
│   └── personas/ (loader.py, schema.py)
├── scripts/
│   ├── run_simulation.py
│   └── run_autoresearch.py
├── frontend/ (선택)
├── strategy_prompt.md
├── results.tsv
└── requirements.txt
```

---

## 데이터 형식 준수

에이전트가 생성하는 코드의 입출력은 `contracts/schemas/`의 JSON Schema를 준수해야 한다.

| 스키마 | 사용 위치 |
|--------|----------|
| strategy.schema.json | H → A 사이 |
| conversation-session.schema.json | A → E 사이 |
| evaluation-result.schema.json | E 출력 |
| ralph-iteration.schema.json | RALPH 1회 전체 결과 |
| experiment-result.schema.json | results.tsv 1행 |

---

## 실행 확인 명령

Phase 1 완료 후 이것들이 동작해야 한다:

```bash
# 의존성 설치
pip install -r requirements.txt

# import 확인
python -c "from src.ralph.loop import run_ralph_loop; print('OK')"

# DEV 모드 시뮬레이션
RALPHTHON_MODE=DEV python scripts/run_simulation.py > run.log 2>&1

# 결과 확인
grep "^avg_score:" run.log
```

---

## 완성품이 아닌 것

- UI 없어도 됨 (CLI로 충분)
- 완벽한 코드 품질이 아니어도 됨 (동작이 우선)
- 모든 에러를 graceful하게 처리하지 않아도 됨 (치명적 crash만 방지)
- 테스트 코드가 없어도 됨 (동작 확인이 곧 테스트)

핵심:
**동작하는 시뮬레이션 + autoresearch 루프가 돌아가는 것.**
