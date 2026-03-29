"""L (Learn) — Extract reusable learnings from Reason analysis."""
import json
import logging
from pathlib import Path

from src.llm import call_llm_expensive

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent.parent.parent / "harness" / "prompts"


def _load_learn_prompt() -> str:
    path = PROMPTS_DIR / "learn-system.md"
    if not path.exists():
        raise FileNotFoundError(f"Learn prompt not found: {path}")
    return path.read_text(encoding="utf-8")


def _load_current_strategy_prompt() -> str:
    local = Path(__file__).parent.parent.parent / "strategy_prompt.md"
    if local.exists():
        return local.read_text(encoding="utf-8")
    harness = PROMPTS_DIR / "strategy_prompt.md"
    if harness.exists():
        return harness.read_text(encoding="utf-8")
    return "(strategy_prompt.md not found)"


async def learn(reason_output: dict) -> dict:
    """Extract reusable learning points from Reason analysis.

    Args:
        reason_output: Dict from R stage with patterns.

    Returns:
        Dict with learnings, recommended_prompt_changes, etc.
    """
    template = _load_learn_prompt()
    current_strategy = _load_current_strategy_prompt()

    system_prompt = (
        template
        .replace("{reason_output}", json.dumps(reason_output, ensure_ascii=False, indent=2))
        .replace("{current_strategy_prompt}", current_strategy)
    )

    user_message = (
        "Reason 분석 결과에서 재사용 가능한 학습 포인트를 추출하세요.\n"
        "JSON 형식으로만 응답하세요."
    )

    response = await call_llm_expensive(
        system_prompt=system_prompt,
        user_message=user_message,
        temperature=0.3,
        expect_json=True,
    )

    result = json.loads(response) if isinstance(response, str) else response

    # Ensure required keys
    result.setdefault("learnings", [])
    result.setdefault("recommended_prompt_changes", [])

    logger.info(f"L stage: Extracted {len(result['learnings'])} learnings")
    return result
