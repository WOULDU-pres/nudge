"""L (Learn) — 학습 추출."""
from __future__ import annotations

import json
import logging
from src.llm import call_llm, parse_json_response

logger = logging.getLogger("ralphthon.ralph.learn")

LEARN_SYSTEM = """당신은 세일즈 전략 학습 시스템입니다.

## 지시

Reason 분석에서 발견된 패턴을 바탕으로,
다음 전략 생성에 활용할 수 있는 학습 포인트를 추출하세요.

반드시 아래 JSON 형식으로 응답하세요:

```json
{
  "learnings": [
    "재사용 가능한 학습 포인트 (구체적, 실행 가능한 형태)"
  ],
  "recommended_prompt_changes": [
    "strategy_prompt.md에 대한 구체적 수정 제안"
  ]
}
```

## 추출 원칙

- 일반화 가능한 학습만. 특정 페르소나 1명에만 해당되는 것은 제외.
- 실행 가능한 형태로. "더 좋게 하라"가 아니라 "첫 턴에 가격을 먼저 언급하라".
- strategy_prompt.md 수정 제안은 구체적으로.
- 이전 학습과 중복되는 것은 제외.
"""


async def learn(
    reason_output: dict,
    current_strategy_prompt: str,
) -> dict:
    """패턴 분석에서 재사용 학습 포인트 추출.

    Returns:
        {"learnings": [...], "recommended_prompt_changes": [...]}
    """
    user_msg = f"""## Reason 분석 결과
{json.dumps(reason_output, ensure_ascii=False, indent=2)}

## 현재 strategy_prompt.md
{current_strategy_prompt}"""

    raw = await call_llm(
        system_prompt=LEARN_SYSTEM,
        user_message=user_msg,
        temperature=0.3,
        model_tier="expensive",
    )

    if "[LLM ERROR]" in raw:
        logger.warning(f"Learn LLM error: {raw[:200]}")
        return {"learnings": [], "recommended_prompt_changes": []}

    parsed = parse_json_response(raw)
    if parsed is None:
        logger.warning("Learn JSON parse failed")
        return {"learnings": [], "recommended_prompt_changes": []}

    return {
        "learnings": parsed.get("learnings", []),
        "recommended_prompt_changes": parsed.get("recommended_prompt_changes", []),
    }
