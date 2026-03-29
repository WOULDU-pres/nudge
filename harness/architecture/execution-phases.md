# Execution Phases

에이전트가 MASTER-PROMPT.md를 읽은 후 수행하는 3단계.
각 Phase는 이전 Phase가 완료되어야 시작한다.

---

## Phase 1: 코드 생성

### 목적
하네스 문서를 읽고, 설득 시뮬레이션 시스템을 Python 코드로 구현한다.

### 읽어야 할 파일 (순서대로)

1. `architecture/system-overview.md` → 전체 구조 이해
2. `architecture/ralph-loop.md` → RALPH 6단계 입출력
3. `architecture/autoresearch-loop.md` → 외부 루프 구조
4. `architecture/tech-stack.md` → 기술 스택 제약
5. `contracts/product-contract.md` → 산출물 규격
6. `contracts/schemas/*.json` → 데이터 구조
7. `prompts/*.md` → 시스템 프롬프트 원본
8. `criteria/evaluation-rubric.md` → 평가 기준

### 생성할 코드 구조

```
output/
├── config/
│   ├── settings.py             ← Pydantic Settings (환경변수 기반)
│   ├── default.yaml            ← 기본 설정값
│   └── product.yaml            ← 판매 제품 정보
│
├── src/
│   ├── llm.py                  ← 멀티프로바이더 LLM 클라이언트
│   ├── agents/
│   │   ├── base.py             ← 에이전트 기반 클래스
│   │   ├── sales_agent.py      ← 판매 에이전트 (LLM)
│   │   └── customer_agent.py   ← 고객 에이전트 (soul.md + LLM)
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
│   ├── ralph/
│   │   ├── loop.py             ← RALPH 메인 루프
│   │   ├── hypothesize.py      ← H: 전략 가설 생성
│   │   ├── plan.py             ← P: 페르소나 선택
│   │   ├── act.py              ← A: 대화 배치 실행
│   │   ├── reason.py           ← R: 패턴 분석
│   │   ├── learn.py            ← L: 학습 추출
│   │   └── strategy.py         ← Strategy/StrategyResult 모델
│   │
│   └── personas/
│       ├── loader.py           ← soul.md + profile.json 로더
│       └── schema.py           ← 페르소나 모델
│
├── scripts/
│   ├── run_simulation.py       ← RALPH Loop 1회 실행
│   └── run_autoresearch.py     ← autoresearch 외부 루프
│
├── strategy_prompt.md          ← autoresearch 수정 대상 (초기 버전 복사)
├── results.tsv                 ← 실험 로그 (헤더만)
└── requirements.txt
```

### Phase 1 완료 조건

- [ ] 모든 파일이 생성됨
- [ ] `pip install -r requirements.txt` 성공
- [ ] `python -c "from src.ralph.loop import run_ralph_loop"` 에러 없음
- [ ] `python scripts/run_simulation.py --dry-run` 성공 (LLM 호출 없이 구조 확인)

### Phase 1 실패 시

코드가 실행되지 않으면:
1. 에러 메시지 읽기
2. 수정
3. 다시 확인
4. 반복 (사람에게 묻지 않음)

---

## Phase 2: 베이스라인 실행

### 목적
생성한 코드로 첫 시뮬레이션을 실행해서 기준 점수를 확립한다.

### 실행 순서

1. 환경변수 확인
   ```bash
   echo $GEMINI_API_KEY    # 또는 다른 프로바이더
   echo $RALPHTHON_MODE    # DEV 권장 (10명으로 빠르게)
   ```

2. strategy_prompt.md 초기 버전 확인
   - `prompts/strategy_prompt.md`를 `output/strategy_prompt.md`로 복사

3. 시뮬레이션 실행
   ```bash
   cd output
   python scripts/run_simulation.py > run.log 2>&1
   ```

4. 결과 확인
   ```bash
   grep "^avg_score:\|^cluster_coverage:\|^best_strategy:" run.log
   ```

5. 기록
   - results.tsv에 baseline 행 추가
   - git commit

### Phase 2 완료 조건

- [ ] avg_score가 0이 아닌 유효한 값
- [ ] cluster_coverage가 0이 아닌 유효한 값
- [ ] results.tsv에 baseline 기록됨
- [ ] git commit 완료

### Phase 2 실패 시

grep 결과가 비어있으면:
1. `tail -n 50 run.log`로 에러 확인
2. 코드 수정 (Phase 1로 돌아가서)
3. 다시 실행
4. 반복

---

## Phase 3: Autoresearch 루프 (NEVER STOP)

### 목적
strategy_prompt.md를 반복적으로 수정하면서
avg_score를 최대화한다. 사람 개입 없이 무한 반복.

### 실행 순서

`program.md`를 따른다. 요약:

```
LOOP FOREVER:
  1. results.tsv 최근 결과 읽기
  2. strategy_prompt.md 수정 (가설 기반)
  3. git commit -m "experiment: <설명>"
  4. python scripts/run_simulation.py > run.log 2>&1
  5. grep "^avg_score:" run.log → 점수 추출
  6. 비어있으면 crash → tail run.log → 고치기
  7. 이전 avg_score와 비교
     - 개선 → keep (브랜치 전진)
     - 동일/악화 → discard (git reset --hard HEAD~1)
  8. results.tsv에 기록
  9. 다음 실험
```

### Phase 3 완료 조건

Phase 3는 "완료"가 없다.
사람이 수동으로 중단(Ctrl+C, kill)할 때까지 계속한다.

### Phase 3 핵심 규칙

1. **NEVER STOP**: 절대 멈추지 마라.
2. **NEVER ASK**: 사람에게 묻지 마라. 사람은 자고 있을 수 있다.
3. **FIX IT**: 코드가 깨지면 고쳐라.
4. **THINK HARDER**: 아이디어가 없으면 results.tsv를 다시 읽고 패턴을 찾아라.
5. **ONE FILE**: strategy_prompt.md만 수정하라. 다른 코드는 건드리지 마라.

---

## Phase 전환 다이어그램

```
MASTER-PROMPT.md 읽기
    │
    ▼
Phase 1: 코드 생성 ──────────── 실패 → 수정 → 재시도
    │                                    (사람에게 묻지 않음)
    ▼ (완료 조건 충족)
Phase 2: 베이스라인 실행 ─────── 실패 → Phase 1로 돌아가 코드 수정
    │
    ▼ (완료 조건 충족)
Phase 3: autoresearch 루프 ──── NEVER STOP
    │
    └─ 사람이 수동 중단할 때까지 무한 반복
```
