"""H(Hypothesize) stage: Generate new sales strategies via LLM."""

import json
import logging
from pathlib import Path

from config.settings import settings
from src.llm import call_llm, extract_json

logger = logging.getLogger(__name__)

# Cache loaded templates
_strategy_prompt: str | None = None
_hypothesize_system: str | None = None


def _get_strategy_prompt() -> str:
    """Load strategy_prompt.md from output/ directory (runtime copy)."""
    global _strategy_prompt
    if _strategy_prompt is None:
        # First try output/strategy_prompt.md (runtime copy)
        local_path = Path("strategy_prompt.md")
        if local_path.exists():
            _strategy_prompt = local_path.read_text(encoding="utf-8")
        else:
            # Fallback to prompts dir
            path = Path(settings.PROMPTS_DIR) / "strategy_prompt.md"
            _strategy_prompt = path.read_text(encoding="utf-8")
    return _strategy_prompt


def _get_hypothesize_system() -> str:
    """Load hypothesize-system.md template from PROMPTS_DIR."""
    global _hypothesize_system
    if _hypothesize_system is None:
        path = Path(settings.PROMPTS_DIR) / "hypothesize-system.md"
        _hypothesize_system = path.read_text(encoding="utf-8")
    return _hypothesize_system


def _fill_ledger_placeholders(template: str, ledger: dict | None) -> str:
    """Replace {ledger.*} and {previous_learnings} placeholders in the template."""
    if ledger is None:
        ledger = {}

    replacements = {
        "{ledger.never_repeat}": json.dumps(
            ledger.get("never_repeat", []), ensure_ascii=False, indent=2
        ),
        "{ledger.proven_effective}": json.dumps(
            ledger.get("proven_effective", []), ensure_ascii=False, indent=2
        ),
        "{ledger.best_score_ever}": str(ledger.get("best_score_ever", "N/A")),
        "{ledger.best_strategy_ever.generation}": str(
            ledger.get("best_strategy_ever", {}).get("generation", "N/A")
        ),
        "{ledger.recent_3_generations}": json.dumps(
            ledger.get("recent_3_generations", []), ensure_ascii=False, indent=2
        ),
        "{ledger.past_summary}": str(ledger.get("past_summary", "No past data available.")),
    }

    for placeholder, value in replacements.items():
        template = template.replace(placeholder, value)

    return template


async def hypothesize(
    product: dict,
    strategy_ledger: dict | None = None,
    learnings: dict | None = None,
    num_strategies: int = 3,
) -> list[dict]:
    """Generate new strategy hypotheses using LLM.

    Args:
        product: Product information dict (from product.yaml).
        strategy_ledger: Optional strategy ledger with history.
        learnings: Optional previous learnings dict.
        num_strategies: Number of strategies to generate.

    Returns:
        List of strategy dicts matching strategy schema.
    """
    strategy_prompt = _get_strategy_prompt()
    hypothesize_system = _get_hypothesize_system()

    # Fill ledger placeholders in hypothesize system prompt
    hypothesize_filled = _fill_ledger_placeholders(hypothesize_system, strategy_ledger)

    # Fill {previous_learnings} placeholder
    learnings_text = "No previous learnings available."
    if learnings:
        learnings_text = json.dumps(learnings, ensure_ascii=False, indent=2)
    hypothesize_filled = hypothesize_filled.replace("{previous_learnings}", learnings_text)

    # Combine system prompts
    system_prompt = strategy_prompt + "\n\n---\n\n" + hypothesize_filled

    # Build user prompt with product info and request
    product_brief = json.dumps(product, ensure_ascii=False, indent=2)
    user_prompt = (
        f"## 제품 정보\n{product_brief}\n\n"
        f"## 요청\n"
        f"{num_strategies}개의 서로 다른 설득 전략을 JSON 배열로 생성하세요.\n"
        f"각 전략은 strategy_id, hypothesis, funnel (attention/interest/desire/action), tone 필드를 반드시 포함해야 합니다.\n"
        f"JSON 배열만 반환하세요."
    )

    response = await call_llm(
        prompt=user_prompt,
        system=system_prompt,
        model=settings.expensive_model,
        temperature=0.8,
    )

    parsed = extract_json(response)

    # Ensure it's a list
    if isinstance(parsed, dict):
        parsed = [parsed]

    # Validate required fields
    required_fields = {"strategy_id", "hypothesis", "funnel", "tone"}
    validated = []
    for i, strategy in enumerate(parsed):
        if not isinstance(strategy, dict):
            logger.warning("Skipping non-dict strategy at index %d", i)
            continue

        missing = required_fields - set(strategy.keys())
        if missing:
            logger.warning(
                "Strategy at index %d missing fields %s, adding defaults", i, missing
            )
            # Add defaults for missing fields
            if "strategy_id" not in strategy:
                strategy["strategy_id"] = f"strategy-auto-{i}"
            if "hypothesis" not in strategy:
                strategy["hypothesis"] = "Auto-generated hypothesis"
            if "funnel" not in strategy:
                strategy["funnel"] = {
                    "attention": {
                        "hook_type": "공감형",
                        "opening_line_guide": "Auto-generated",
                        "target_emotion": "공감",
                    },
                    "interest": {
                        "value_framing": "Auto-generated",
                        "information_depth": "핵심1개",
                        "engagement_trigger": "Auto-generated",
                    },
                    "desire": {
                        "emotional_driver": "Auto-generated",
                        "proof_type": "사회적증거",
                        "objection_preempt": "Auto-generated",
                    },
                    "action": {
                        "cta_style": "소프트CTA",
                        "urgency_type": "없음",
                        "fallback": "무료 샘플 제안",
                    },
                }
            if "tone" not in strategy:
                strategy["tone"] = "친절하고 자연스러운"

        validated.append(strategy)

    if not validated:
        logger.error("No valid strategies generated, creating fallback")
        validated = [
            {
                "strategy_id": "strategy-fallback",
                "hypothesis": "Fallback strategy when generation fails",
                "funnel": {
                    "attention": {
                        "hook_type": "공감형",
                        "opening_line_guide": "요즘 건강 관리 어떻게 하고 계세요?",
                        "target_emotion": "공감",
                    },
                    "interest": {
                        "value_framing": "하루 한 알로 간편한 건강 관리",
                        "information_depth": "핵심1개",
                        "engagement_trigger": "평소 영양제 드시나요?",
                    },
                    "desire": {
                        "emotional_driver": "간편함",
                        "proof_type": "사회적증거",
                        "objection_preempt": "좋은 지적이세요. 하루 1정이라 부담 없이 시작하실 수 있어요.",
                    },
                    "action": {
                        "cta_style": "소프트CTA",
                        "urgency_type": "없음",
                        "fallback": "성분표 링크 보내드릴까요?",
                    },
                },
                "tone": "친절하고 자연스러운",
            }
        ]

    logger.info("Generated %d strategies", len(validated))
    return validated[:num_strategies]
