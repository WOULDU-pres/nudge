# Ralphthon Autoresearch — Program

오케스트레이터가 하네스를 실행하는 상세 프로그램.
MASTER-PROMPT.md → 이 파일로 연결된다.

---

## 재진입 (새 세션이 시작되면)

```
1. CHECKPOINT.json 읽기
2. phase 확인
3. 해당 Phase의 마지막 지점부터 이어가기
4. next_action 필드가 있으면 그것부터 수행
```

---

## Phase 1: 코드 생성

### 코더 위임 방식

Codex CLI를 사용한다:

```bash
# output/은 하네스와 형제 디렉토리 (../output/ 하네스 기준)
codex exec --full-auto '<지시>' --workdir ../output/
```

또는 pty 모드로:
```bash
# terminal에서 pty=true, workdir는 output/ 절대경로
codex exec --full-auto '...'
```

### 모듈별 위임 + 검증

각 모듈을 순서대로 코더에게 시키고, 완료 후 검증한다.

#### 1-1. 프로젝트 초기화

코더 지시:
```
../output/ 디렉토리(하네스 바깥, 형제 디렉토리)에 Python 프로젝트를 초기화하라.
- requirements.txt: aiohttp, pydantic, pydantic-settings, pyyaml
- config/settings.py: Pydantic Settings 기반 환경변수 설정
  - RALPHTHON_PROVIDER (기본 gemini)
  - RALPHTHON_MODEL_CHEAP (기본 gemini-2.0-flash)
  - RALPHTHON_MODEL_EXPENSIVE (기본 gemini-2.5-pro)
  - RALPHTHON_MODE (DEV/TEST/DEMO, 기본 DEV)
  - MAX_CONCURRENT (기본 5)
  - CONVERSATION_TURNS (기본 3)
  - API 키들 (GEMINI_API_KEY 등)
- config/product.yaml: 바이탈케어 제품 정보 (program.md 참고)
- 디렉토리: src/agents/, src/conversation/, src/evaluation/, src/ralph/, src/personas/
```

검증:
```bash
cd ../output && pip install -r requirements.txt
python -c "from config.settings import Settings; s = Settings(); print(s.RALPHTHON_MODE)"
```

CHECKPOINT 업데이트: `phase1.completed_modules += ["config"]`

#### 1-2. LLM 클라이언트

코더 지시:
```
../output/src/llm.py를 구현하라.
참고: architecture/tech-stack.md의 멀티프로바이더 섹션.

- async def call_llm(system_prompt, user_message, temperature, model_tier) → str
- model_tier: "cheap" 또는 "expensive"
- cheap → settings.RALPHTHON_MODEL_CHEAP
- expensive → settings.RALPHTHON_MODEL_EXPENSIVE
- 프로바이더별 분기: gemini, openai, anthropic, ollama
- aiohttp 사용
- ```json 블록 추출 패턴 포함
- 에러 시 "[LLM ERROR] ..." 반환 (crash 방지)
```

검증:
```bash
python -c "from src.llm import call_llm; print('OK')"
```

CHECKPOINT 업데이트: `phase1.completed_modules += ["llm"]`

#### 1-3. 페르소나 로더

코더 지시:
```
../output/src/personas/loader.py를 구현하라.
- def load_personas(count, personas_dir) → list[dict]
- ../data/personas/P001~P200에서 profile.json + soul.md 로딩
- ID 순 정렬
- 반환: [{"id": "P001", "profile": {...}, "soul": "...", "cluster_tags": [...]}]
```

검증:
```bash
python -c "from src.personas.loader import load_personas; ps = load_personas(10); print(len(ps), ps[0]['id'])"
```

CHECKPOINT 업데이트: `phase1.completed_modules += ["personas"]`

#### 1-4. 에이전트

코더 지시:
```
../output/src/agents/sales_agent.py, customer_agent.py를 구현하라.
참고: prompts/sales-agent-system.md, prompts/customer-agent-system.md

- SalesAgent: 전략 정보 + 제품 정보로 system prompt 생성, call_llm(tier="cheap") 호출
- CustomerAgent: soul.md로 system prompt 생성, call_llm(tier="cheap") 호출
```

검증:
```bash
python -c "from src.agents.sales_agent import SalesAgent; from src.agents.customer_agent import CustomerAgent; print('OK')"
```

#### 1-5. 대화 엔진

코더 지시:
```
../output/src/conversation/engine.py를 구현하라.
참고: architecture/ralph-loop.md의 Act 섹션.

- async def run_conversation(sales_agent, customer_agent, product_brief, turns=3) → ConversationSession
- 턴 기반: agent → persona → agent → persona → ...
- asyncio.Semaphore 동시성 제어
- conversation-session.schema.json 형태로 반환
```

#### 1-6. Judge 평가

코더 지시:
```
../output/src/evaluation/evaluator.py를 구현하라.
참고: prompts/judge-system.md, criteria/evaluation-rubric.md

- async def judge_conversation(transcript, persona_profile) → EvaluationResult
- call_llm(tier="expensive", temperature=0.1)
- evaluation-result.schema.json 형태로 반환
- JSON 파싱 실패 시 0점 fallback
```

#### 1-7. RALPH Loop

코더 지시:
```
../output/src/ralph/loop.py를 구현하라.
참고: architecture/ralph-loop.md 전체.

- async def run_ralph_loop(strategy_prompt, product_brief, personas) → RALPHIteration
- H: strategy_prompt 기반 전략 생성 (call_llm expensive)
- P: 페르소나 선택 (코드)
- A: 전략 × 페르소나 대화 실행 (call_llm cheap, 병렬)
- E: Judge 채점 (call_llm expensive)
- R: 패턴 분석 (call_llm expensive)
- L: 학습 추출 (call_llm expensive)
- 결과 집계: avg_score, cluster_coverage, best_strategy
- stdout에 grep 가능 형식 출력
```

#### 1-8. 실행 스크립트

코더 지시:
```
../output/scripts/run_simulation.py를 구현하라.
- strategy_prompt.md 로드
- run_ralph_loop 실행
- stdout에 결과 출력:
  avg_score: <N>
  cluster_coverage: <N>
  best_strategy: <id>
- runs/<run_id>/에 상세 결과 저장
```

### Phase 1 완료 조건

`criteria/quality-gates.md`의 Phase 1 기준 전부 충족:
```bash
pip install -r requirements.txt                         # 성공
python -c "from src.ralph.loop import run_ralph_loop"   # 에러 없음
python scripts/run_simulation.py --dry-run              # 구조 확인
```

→ CHECKPOINT: `{"phase": "phase2", "phase1": {"status": "completed", ...}}`

---

## Phase 2: 베이스라인 실행

오케스트레이터가 직접 실행한다 (코더 불필요).

### 제품 정보 전달

시뮬레이션에는 반드시 제품 정보가 필요하다. 3가지 방법 중 택 1:

```bash
# 방법 1: YAML 파일로 전달
python scripts/run_simulation.py --product config/product.yaml

# 방법 2: 텍스트 파일로 전달
python scripts/run_simulation.py --product my_product.txt

# 방법 3: config/product.yaml이 있으면 자동 로드 (fallback)
python scripts/run_simulation.py
```

**제품 정보가 없으면 시뮬레이션이 시작되지 않는다.**

```bash
cd ../output

# 환경변수 확인
echo $GEMINI_API_KEY

# DEV 모드 실행 (제품 정보는 product.yaml 또는 --product로 지정)
RALPHTHON_MODE=DEV python scripts/run_simulation.py > run.log 2>&1

# 결과 확인
grep "^avg_score:\|^cluster_coverage:\|^best_strategy:" run.log
```

### 결과가 있으면

```bash
COMMIT=$(git rev-parse --short HEAD)
AVG=$(grep "^avg_score:" run.log | awk '{print $2}')
COV=$(grep "^cluster_coverage:" run.log | awk '{print $2}')
BEST=$(grep "^best_strategy:" run.log | awk '{print $2}')

echo "${COMMIT}\t${AVG}\t${COV}\t${BEST}\tkeep\tbaseline" >> results.tsv
git add -A && git commit -m "phase2: baseline avg_score=${AVG}"
```

→ CHECKPOINT: `{"phase": "phase3", "phase2": {"status": "completed", "baseline_score": <AVG>, ...}}`

### 결과가 없으면

```bash
tail -n 50 run.log
```

에러 파악 → 코더에게 수정 지시 → 재실행.

---

## Phase 3: Autoresearch (NEVER STOP)

### 셋업 (첫 시작)

```bash
git checkout -b autoresearch/$(date +%b%d | tr '[:upper:]' '[:lower:]')
```

→ CHECKPOINT: `phase3.git_branch = "autoresearch/<tag>"`

### 이어가기 (재진입)

```bash
git checkout <CHECKPOINT.phase3.git_branch>
```

### 루프

```
LOOP FOREVER:

  ┌─ 1. 상태 파악 ──────────────────────────────────┐
  │  cat CHECKPOINT.json → experiment_count, scores   │
  │  tail -20 results.tsv → 최근 실험 패턴           │
  │  cat ../output/strategy_prompt.md → 현재 프롬프트  │
  └──────────────────────────────────────────────────┘

  ┌─ 2. 가설 수립 ──────────────────────────────────┐
  │  약한 클러스터/패턴 파악                          │
  │  "이렇게 바꾸면 X 점수가 오를 것" 가설 설정       │
  │                                                   │
  │  consecutive_discards >= 5이면:                   │
  │    → 급진적 변경 (구조 변경, 새 접근)             │
  └──────────────────────────────────────────────────┘

  ┌─ 3. strategy_prompt.md 수정 ────────────────────┐
  │  가설에 따라 ../output/strategy_prompt.md 변경     │
  │  git add ../output/strategy_prompt.md             │
  │  git commit -m "experiment N: <가설 한 줄>"      │
  └──────────────────────────────────────────────────┘

  ┌─ 4. 시뮬레이션 실행 ────────────────────────────┐
  │  cd ../output                                    │
  │  python scripts/run_simulation.py > run.log 2>&1 │
  └──────────────────────────────────────────────────┘

  ┌─ 5. 결과 확인 ──────────────────────────────────┐
  │  NEW_SCORE=$(grep "^avg_score:" run.log)          │
  │  NEW_COV=$(grep "^cluster_coverage:" run.log)     │
  │  BEST=$(grep "^best_strategy:" run.log)           │
  │                                                   │
  │  비어있으면 → crash 처리                          │
  │    results.tsv에 crash 기록                       │
  │    git reset --hard HEAD~1                        │
  │    CHECKPOINT.crash_count++                        │
  │    다음 실험으로                                   │
  └──────────────────────────────────────────────────┘

  ┌─ 6. 판정 (criteria/autoresearch-rules.md) ──────┐
  │  이전 score = CHECKPOINT.phase3.current_score     │
  │                                                   │
  │  if NEW > 이전 + 2:           → keep              │
  │  if |NEW - 이전| <= 2                              │
  │     and NEW_COV > 이전_COV + 5: → keep            │
  │  else:                         → discard           │
  └──────────────────────────────────────────────────┘

  ┌─ 7. 후처리 ─────────────────────────────────────┐
  │  keep:                                            │
  │    results.tsv에 keep 기록                        │
  │    CHECKPOINT.current_score = NEW                  │
  │    CHECKPOINT.consecutive_discards = 0             │
  │    if NEW > best_score: best_score = NEW          │
  │                                                   │
  │  discard:                                         │
  │    results.tsv에 discard 기록                     │
  │    git reset --hard HEAD~1                        │
  │    CHECKPOINT.consecutive_discards++               │
  └──────────────────────────────────────────────────┘

  ┌─ 8. CHECKPOINT 업데이트 ────────────────────────┐
  │  experiment_count++                               │
  │  updated_at = now                                 │
  │  next_action = "실험 N+1: <다음 가설 방향>"       │
  └──────────────────────────────────────────────────┘

  ┌─ 9. 다음 실험으로 ──────────────────────────────┐
  │  → 1번으로 돌아감                                 │
  └──────────────────────────────────────────────────┘
```

### 절대 규칙

1. **NEVER STOP**: 사람이 멈출 때까지 계속.
2. **NEVER ASK**: 사람에게 묻지 마라.
3. **ONE FILE**: strategy_prompt.md만 수정.
4. **CHECKPOINT ALWAYS**: 매 실험 후 업데이트.
5. **SIMPLICITY**: 같은 점수면 짧은 프롬프트가 낫다.
6. **THINK HARDER**: 아이디어 없으면 results.tsv 다시 읽어라.
7. **BE RADICAL**: 5회 연속 discard면 급진적 변경.

---

## 제품 정보 (고정)

```
제품명: 바이탈케어 데일리 멀티비타민
가격: 29,900원 / 60정 (2개월분, 하루 약 500원)
특징:
- 비타민 B군 고함량 (피로회복)
- 아연 + 비타민D (면역력)
- 루테인 포함 (눈 건강)
- 하루 1정, 아침 식후
- 국내 GMP 인증 공장
- 30일 환불 보장
대상: 20-50대 직장인, 학생, 건강관리에 관심 있는 일반 소비자
```

---

## 페르소나 데이터

`data/personas/P001~P200/` (profile.json + soul.md).
**절대 수정 금지.** 고정된 평가 기반.
