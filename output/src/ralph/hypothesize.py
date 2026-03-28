"""H (Hypothesize) — 전략 가설 생성."""
from __future__ import annotations

import logging
from src.llm import call_llm, parse_json_response
from config.settings import get_settings

logger = logging.getLogger("ralphthon.ralph.hypothesize")

HYPOTHESIZE_SUPPLEMENT = """
## 이전 학습 결과
{previous_learnings}

## 이전 최고 전략
{best_strategy_summary}

## 지시
이전 학습을 바탕으로, 기존 전략의 약점을 보완하거나
아직 시도하지 않은 새로운 접근을 시도하세요.

특히:
- 점수가 낮았던 클러스터에 대한 개선 방안을 포함하세요.
- 이전에 효과적이었던 패턴을 유지하되, 새로운 변형을 시도하세요.
- 가설을 명확하게 서술하세요.

## 출력
strategy_prompt.md의 출력 규칙에 따라 JSON 배열로 전략을 생성하세요.
"""


async def hypothesize(
    strategy_prompt: str,
    product_brief: str,
    previous_learnings: str = "",
    best_strategy_summary: str = "",
) -> list[dict]:
    """전략 가설 N개 생성.

    Args:
        strategy_prompt: strategy_prompt.md 내용 (system prompt)
        product_brief: 제품 정보 (user message)
        previous_learnings: 이전 L의 출력 (있으면)
        best_strategy_summary: 이전 최고 전략 요약

    Returns:
        Strategy[] (dict 배열). 실패 시 fallback 전략 1개.
    """
    settings = get_settings()
    n_strategies = settings.RALPHTHON_STRATEGIES_PER_RUN

    # Build system prompt
    system = strategy_prompt
    if previous_learnings or best_strategy_summary:
        system += "\n\n" + HYPOTHESIZE_SUPPLEMENT.format(
            previous_learnings=previous_learnings or "없음",
            best_strategy_summary=best_strategy_summary or "없음",
        )

    user_msg = f"""아래 제품에 대한 설득 전략 {n_strategies}개를 JSON 배열로 생성하세요.

제품 정보:
{product_brief}

반드시 JSON 배열만 반환하세요. 각 전략은 strategy_id, hypothesis, approach, opening_style, objection_handling, tone 필드를 포함해야 합니다."""

    raw = await call_llm(
        system_prompt=system,
        user_message=user_msg,
        temperature=0.8,
        model_tier="expensive",
    )

    if "[LLM ERROR]" in raw:
        logger.warning(f"Hypothesize LLM error: {raw[:200]}")
        return [_fallback_strategy()]

    parsed = parse_json_response(raw)
    if parsed is None or not isinstance(parsed, list):
        logger.warning("Hypothesize JSON parse failed, using fallback")
        return [_fallback_strategy()]

    # Validate and clean
    strategies = []
    for i, s in enumerate(parsed):
        if not isinstance(s, dict):
            continue
        strategy = {
            "strategy_id": s.get("strategy_id", f"strategy-{i+1}"),
            "hypothesis": s.get("hypothesis", ""),
            "approach": s.get("approach", ""),
            "opening_style": s.get("opening_style", ""),
            "objection_handling": s.get("objection_handling", ""),
            "tone": s.get("tone", ""),
        }
        # Ensure strategy_id prefix
        if not strategy["strategy_id"].startswith("strategy-"):
            strategy["strategy_id"] = f"strategy-{strategy['strategy_id']}"
        strategies.append(strategy)

    if not strategies:
        return [_fallback_strategy()]

    return strategies[:n_strategies]


def _fallback_strategy() -> dict:
    return {
        "strategy_id": "strategy-fallback",
        "hypothesis": "기본 가치 프레이밍으로 넓은 고객층 접근",
        "approach": "하루 500원으로 건강 관리를 시작할 수 있다는 가격 대비 가치 강조",
        "opening_style": "일상적 건강 고민으로 시작하는 친근한 접근",
        "objection_handling": "30일 환불 보장으로 리스크 완화",
        "tone": "친절하고 정보 중심적",
    }
