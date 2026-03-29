# Tech Stack & Constraints

에이전트가 완성품(코드)을 생성할 때 따라야 하는 기술 스택과 제약사항.

---

## 언어 & 런타임

- **Python 3.11+**
- asyncio 기반 비동기 실행
- 타입 힌트 필수 (mypy 호환 권장)

---

## 핵심 라이브러리

| 라이브러리 | 용도 | 비고 |
|-----------|------|------|
| aiohttp | LLM API 비동기 호출 | httpx도 허용 |
| pydantic | 데이터 모델 (Strategy, Evaluation 등) | BaseModel + Settings |
| pydantic-settings | 환경변수 기반 설정 | .env 파일 지원 |

### 선택적 라이브러리 (에이전트 판단)

| 라이브러리 | 용도 |
|-----------|------|
| rich | 콘솔 출력 포맷팅 |
| fastapi + uvicorn | 웹 대시보드 (선택) |
| jinja2 | HTML 템플릿 (대시보드용) |

### 사용 금지

- LangChain, LlamaIndex 등 프레임워크: 직접 API 호출로 충분
- 외부 데이터베이스: 파일 기반으로 충분 (JSON + TSV)
- Docker: 로컬 실행 기준

---

## LLM 프로바이더

멀티 프로바이더를 지원해야 한다. 환경변수로 선택.

| 프로바이더 | 환경변수 (API Key) | 기본 모델 |
|-----------|-------------------|----------|
| gemini | GEMINI_API_KEY | gemini-2.0-flash |
| openai | OPENAI_API_KEY | gpt-4o-mini |
| anthropic | ANTHROPIC_API_KEY | claude-sonnet-4-20250514 |
| ollama | OLLAMA_BASE_URL | llama3.1:8b |

프로바이더 선택: `RALPHTHON_PROVIDER` 환경변수.
모델 오버라이드: `RALPHTHON_MODEL` 환경변수.

### 모델 사용 분리 (비용 최적화)

| 역할 | 모델 등급 | 이유 |
|------|----------|------|
| Act (대화) | 싼 모델 (flash/mini) | 대량 호출, 단순 대화 |
| Hypothesize (전략 생성) | 비싼 모델 | 창의적 추론 필요 |
| Evaluate (Judge) | 비싼 모델 | 정확한 평가 필요 |
| Reason (패턴 분석) | 비싼 모델 | 복잡한 비교 분석 |
| Learn (학습 추출) | 비싼 모델 | 일반화 능력 필요 |

싼/비싼 모델 분리는 환경변수로 제어:
- `RALPHTHON_MODEL_CHEAP`: Act 단계용 (기본: gemini-3.1-flash-lite-preview)
- `RALPHTHON_MODEL_EXPENSIVE`: H/E/R/L 단계용 (기본: gemini-3.1-flash-lite-preview)

**주의**: google-genai SDK (`from google import genai`)를 사용한다.
pip install google-genai 필수. 무료 티어 RPM/RPD 제한에 유의.

---

## 동시성 제어

- `asyncio.Semaphore`로 동시 API 호출 수 제한
- 기본값: `MAX_CONCURRENT=20` (기존 5에서 상향)
- Gemini 유료 Pro: 256 RPM → 동시 20 안전
- Gemini Flash Lite: 4,000 RPM → 동시 50까지 가능
- 환경변수 `RALPHTHON_MAX_CONCURRENT`로 오버라이드
- 향후: 429 빈도 기반 adaptive concurrency 고려

---

## 실험 모드

| 모드 | 페르소나 수 | 용도 |
|------|-----------|------|
| DEV | 10명 | 개발/디버깅 |
| TEST | 50명 | 중간 검증 |
| DEMO | 200명 | 전체 실행 |

환경변수: `RALPHTHON_MODE` (기본: DEV)

---

## 디렉토리 규약 (에이전트가 생성할 코드)

```
output/
├── config/
│   ├── settings.py          ← Pydantic Settings
│   ├── default.yaml         ← 기본 설정값
│   └── product.yaml         ← 판매 제품 정보
├── src/
│   ├── llm.py               ← 멀티프로바이더 LLM 클라이언트
│   ├── agents/              ← Sales Agent, Customer Agent
│   ├── conversation/        ← 대화 엔진, 턴 관리
│   ├── evaluation/          ← Judge, 집계
│   ├── ralph/               ← RALPH Loop (H→P→A→E→R→L)
│   └── personas/            ← 페르소나 로더
├── scripts/
│   ├── run_simulation.py    ← RALPH 1회 실행
│   └── run_autoresearch.py  ← autoresearch 외부 루프
├── strategy_prompt.md       ← autoresearch 수정 대상
├── results.tsv              ← 실험 로그
└── requirements.txt
```

---

## 파일 형식

| 데이터 | 형식 | 이유 |
|--------|------|------|
| 페르소나 프로필 | JSON | 구조화된 특성 데이터 |
| 페르소나 영혼 | Markdown (soul.md) | 자연어 캐릭터 묘사 |
| 대화 transcript | JSON | 턴 기반 구조 |
| 평가 결과 | JSON | 4차원 점수 + 근거 (engagement/relevance/persuasion/purchase_intent) |
| 실험 로그 | TSV | grep/awk 친화적, 간결 |
| 설정 | YAML | 가독성 |

---

## Retry 정책

- LLM 호출 레이어 (`llm.py`)에서 모든 API 호출에 자동 retry 적용
- `max_retries = 3`, `base_delay = 1.0`초
- Exponential backoff: `delay = base_delay * (2^attempt) + random jitter(0~0.5s)`
- **RateLimitError (429)**: retry with backoff
- **TransientError (5xx, timeout, connection reset)**: retry with backoff
- **FatalError (401 auth, 400 invalid model)**: 즉시 raise, retry 하지 않음
- Task-level retry: `act.py`/`evaluate.py`에서 개별 대화/평가 실패 시 2회 추가 재시도
- 실패 보고: 모든 실패를 stats 객체로 집계하여 `summary.json`에 포함

---

## 제약사항

1. **API 키는 환경변수로만**: 코드에 하드코딩 금지.
2. **외부 서비스 의존 최소화**: LLM API 외에 외부 호출 없음.
3. **파일 기반 상태 관리**: DB 사용 금지. JSON + TSV로 충분.
4. **단일 머신 실행**: 분산 시스템 아님. 로컬 asyncio.
5. **UTF-8 한국어**: 모든 텍스트는 UTF-8. 한국어 대화.
6. **JSON 출력 안정성**: LLM 응답에서 ```json 블록 추출 패턴 필수.
