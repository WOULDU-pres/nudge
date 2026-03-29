"""H (Hypothesize) — Generate persuasion strategies via LLM."""
import json
import logging
from pathlib import Path

from src.llm import call_llm_expensive, extract_json

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent.parent.parent / "harness" / "prompts"


def _load_strategy_prompt() -> str:
    """Load strategy_prompt.md from output directory."""
    # First try output/strategy_prompt.md (autoresearch may modify this)
    local_path = Path(__file__).parent.parent.parent / "strategy_prompt.md"
    if local_path.exists():
        return local_path.read_text(encoding="utf-8")
    # Fallback to harness version
    harness_path = PROMPTS_DIR / "strategy_prompt.md"
    if harness_path.exists():
        return harness_path.read_text(encoding="utf-8")
    raise FileNotFoundError("strategy_prompt.md not found")


def _load_hypothesize_prompt() -> str:
    """Load hypothesize-system.md template."""
    path = PROMPTS_DIR / "hypothesize-system.md"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _build_hypothesize_context(
    product_brief: str,
    previous_learnings: dict | None = None,
    strategy_ledger: dict | None = None,
) -> str:
    """Build the user message for H stage."""
    lines = []

    lines.append("## 제품 정보")
    lines.append(product_brief)
    lines.append("")

    if strategy_ledger:
        ci = strategy_ledger.get("cumulative_insights", {})
        lines.append("## 이전 세대 결과")
        if ci.get("never_repeat"):
            lines.append("### 절대 반복 금지")
            for p in ci["never_repeat"]:
                lines.append(f"- {p}")
        if ci.get("proven_effective"):
            lines.append("### 검증된 성공 패턴")
            for p in ci["proven_effective"]:
                lines.append(f"- {p}")
        lines.append(f"### 역대 최고: {ci.get('best_score_ever', 0)}점")
        lines.append("")

    if previous_learnings:
        lines.append("## 직전 학습 결과")
        for l in previous_learnings.get("learnings", []):
            lines.append(f"- {l}")
        lines.append("")

    return "\n".join(lines)


async def hypothesize(
    product_brief: str,
    num_strategies: int = 3,
    previous_learnings: dict | None = None,
    strategy_ledger: dict | None = None,
) -> list[dict]:
    """Generate N persuasion strategies using the expensive LLM.

    Returns:
        List of strategy dicts conforming to strategy.schema.json.
    """
    strategy_prompt = _load_strategy_prompt()
    hypothesize_template = _load_hypothesize_prompt()

    # Build system prompt: strategy_prompt is the main, hypothesize adds context
    if hypothesize_template and (strategy_ledger or previous_learnings):
        # Fill in ledger placeholders
        hyp = hypothesize_template
        if strategy_ledger:
            ci = strategy_ledger.get("cumulative_insights", {})
            hyp = hyp.replace("{ledger.never_repeat}", "\n".join(ci.get("never_repeat", ["없음"])))
            hyp = hyp.replace("{ledger.proven_effective}", "\n".join(ci.get("proven_effective", ["없음"])))
            hyp = hyp.replace("{ledger.best_score_ever}", str(ci.get("best_score_ever", 0)))
            hyp = hyp.replace("{ledger.best_strategy_ever.generation}", str(ci.get("best_strategy_ever", {}).get("generation", 0)))
            hyp = hyp.replace("{ledger.recent_3_generations}", "없음")
            hyp = hyp.replace("{ledger.past_summary}", "없음")
        else:
            hyp = hyp.replace("{ledger.never_repeat}", "없음")
            hyp = hyp.replace("{ledger.proven_effective}", "없음")
            hyp = hyp.replace("{ledger.best_score_ever}", "0")
            hyp = hyp.replace("{ledger.best_strategy_ever.generation}", "0")
            hyp = hyp.replace("{ledger.recent_3_generations}", "없음")
            hyp = hyp.replace("{ledger.past_summary}", "없음")

        if previous_learnings:
            hyp = hyp.replace("{previous_learnings}", json.dumps(previous_learnings, ensure_ascii=False, indent=2))
        else:
            hyp = hyp.replace("{previous_learnings}", "없음")

        system_prompt = strategy_prompt + "\n\n---\n\n" + hyp
    else:
        system_prompt = strategy_prompt

    user_message = _build_hypothesize_context(product_brief, previous_learnings, strategy_ledger)
    user_message += f"\n\n{num_strategies}개의 서로 다른 전략을 생성하세요. JSON 배열로만 반환하세요."

    response = await call_llm_expensive(
        system_prompt=system_prompt,
        user_message=user_message,
        temperature=0.9,
        max_tokens=8192,
        expect_json=True,
    )

    strategies = json.loads(response) if isinstance(response, str) else response

    # Ensure it's a list
    if isinstance(strategies, dict):
        strategies = [strategies]

    # Validate and ensure strategy_id
    for i, s in enumerate(strategies):
        if "strategy_id" not in s or not s["strategy_id"]:
            s["strategy_id"] = f"strategy-gen-{i}"

    logger.info(f"H stage: Generated {len(strategies)} strategies: {[s['strategy_id'] for s in strategies]}")
    return strategies[:num_strategies]
