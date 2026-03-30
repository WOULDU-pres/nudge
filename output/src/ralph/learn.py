"""L(Learn) stage: Extract learnings from reason analysis."""

import json
import logging
from pathlib import Path

from config.settings import settings
from src.llm import call_llm, extract_json

logger = logging.getLogger(__name__)

_learn_system: str | None = None


def _get_learn_system() -> str:
    """Load learn-system.md template from PROMPTS_DIR."""
    global _learn_system
    if _learn_system is None:
        path = Path(settings.PROMPTS_DIR) / "learn-system.md"
        _learn_system = path.read_text(encoding="utf-8")
    return _learn_system


async def learn(reason_output: dict, current_strategy_prompt: str) -> dict:
    """Extract learnings from the reason analysis.

    Args:
        reason_output: The reason dict from R stage.
        current_strategy_prompt: Current strategy_prompt.md content.

    Returns:
        Learnings dict with learnings, recommended_prompt_changes, etc.
    """
    system_template = _get_learn_system()

    # Fill placeholders
    reason_text = json.dumps(reason_output, ensure_ascii=False, indent=2)
    system_prompt = system_template.replace(
        "{reason_output}", reason_text
    ).replace("{current_strategy_prompt}", current_strategy_prompt)

    user_prompt = (
        "위 분석 결과를 바탕으로 다음 전략 생성에 활용할 학습 포인트를 추출하세요.\n"
        "JSON 형식으로 응답하세요."
    )

    response = await call_llm(
        prompt=user_prompt,
        system=system_prompt,
        model=settings.expensive_model,
        temperature=0.3,
    )

    try:
        parsed = extract_json(response)
    except ValueError:
        logger.error("Failed to parse learn response, using empty result")
        parsed = {}

    # Ensure required fields exist
    result = {
        "learnings": parsed.get("learnings", []),
        "recommended_prompt_changes": parsed.get("recommended_prompt_changes", []),
    }

    # Include optional fields if present
    for key in ("pattern_updates", "cluster_specific_learnings", "funnel_stage_learnings"):
        if key in parsed:
            result[key] = parsed[key]

    return result
