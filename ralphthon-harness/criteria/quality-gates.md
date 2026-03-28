# Quality Gates — 단계별 통과 기준

에이전트가 각 Phase를 완료했다고 판단하는 기준.

---

## Phase 1: 코드 생성 — 통과 기준

### 필수 (전부 충족해야 Phase 2로 진행)

| # | 기준 | 확인 방법 |
|---|------|----------|
| 1 | requirements.txt 존재 | `test -f requirements.txt` |
| 2 | pip install 성공 | `pip install -r requirements.txt` 에러 없음 |
| 3 | import 성공 | `python -c "from src.ralph.loop import run_ralph_loop"` |
| 4 | 핵심 파일 존재 | src/llm.py, src/ralph/loop.py, scripts/run_simulation.py |
| 5 | settings 로딩 | `python -c "from config.settings import Settings; s = Settings()"` |
| 6 | 페르소나 로딩 | `python -c "from src.personas.loader import load_personas; print(len(load_personas(10)))"` → 10 |
| 7 | strategy_prompt.md 존재 | prompts/에서 복사됨 |

### 선택 (있으면 좋지만 없어도 Phase 2 진행)

| # | 기준 |
|---|------|
| 8 | 대시보드 파일 존재 (frontend/) |
| 9 | 테스트 코드 존재 |
| 10 | type hint 완전성 |

---

## Phase 2: 베이스라인 실행 — 통과 기준

### 필수

| # | 기준 | 확인 방법 |
|---|------|----------|
| 1 | 시뮬레이션 완료 | `python scripts/run_simulation.py` exit code 0 |
| 2 | avg_score 유효 | `grep "^avg_score:" run.log` → 0이 아닌 숫자 |
| 3 | cluster_coverage 유효 | `grep "^cluster_coverage:" run.log` → 0이 아닌 숫자 |
| 4 | best_strategy 존재 | `grep "^best_strategy:" run.log` → 빈 문자열 아님 |
| 5 | results.tsv 기록 | baseline 행이 추가됨 |
| 6 | git commit | `git log --oneline -1` → baseline 관련 커밋 |

### 실패 시

- avg_score가 0: Judge 채점 실패 → prompts/judge-system.md 또는 JSON 파싱 확인
- grep 결과 비어있음: crash → `tail -n 50 run.log`
- 특정 전략만 실패: 해당 전략의 transcript 확인

---

## Phase 3: Autoresearch — 진행 기준

Phase 3는 "완료"가 아니라 "계속 진행 중"이 정상.

### 정상 진행 확인

| # | 기준 | 확인 방법 |
|---|------|----------|
| 1 | results.tsv 행 증가 | `wc -l results.tsv` → 계속 늘어남 |
| 2 | keep/discard 작동 | results.tsv에 keep과 discard가 섞여 있음 |
| 3 | avg_score 변동 | 고정되지 않고 실험마다 변함 |
| 4 | strategy_prompt.md 변경됨 | `git log --oneline strategy_prompt.md` → 커밋 증가 |

### 문제 상태

| 증상 | 가능한 원인 | 조치 |
|------|-----------|------|
| 모든 실험이 crash | JSON 파싱 깨짐 | strategy_prompt.md의 출력 형식 부분 확인 |
| 모든 실험이 discard | avg_score 천장 도달 또는 잘못된 방향 | 급진적 변경 시도 |
| avg_score가 계속 0 | Judge 프롬프트 문제 | prompts/judge-system.md 확인 |
| 루프가 멈춤 | 에이전트가 묻고 있음 | 묻지 말라. NEVER STOP. |
