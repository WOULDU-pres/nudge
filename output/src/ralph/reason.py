"""R (Reason) — Pattern analysis comparing top vs bottom conversations."""
import json
import logging
from pathlib import Path

from src.llm import call_llm_expensive
from src.evaluation.schema import EvaluationResult
from src.evaluation.aggregator import get_top_bottom_results
from src.conversation.turn import ConversationSession

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent.parent.parent / "harness" / "prompts"


def _load_reason_prompt() -> str:
    path = PROMPTS_DIR / "reason-system.md"
    if not path.exists():
        raise FileNotFoundError(f"Reason prompt not found: {path}")
    return path.read_text(encoding="utf-8")


def _format_conversations(
    results: list[EvaluationResult],
    sessions: list[ConversationSession],
    label: str,
) -> str:
    """Format evaluation results + transcripts for the Reason prompt."""
    session_map = {s.session_id: s for s in sessions}
    lines = []

    for r in results:
        session = session_map.get(r.session_id)
        lines.append(f"### {r.session_id} (total={r.scores.total}, outcome={r.outcome.value}, funnel={r.funnel_progress})")
        lines.append(f"- strategy: {r.strategy_id}")
        lines.append(f"- persona: {r.persona_id}")
        lines.append(f"- scores: engagement={r.scores.engagement}, relevance={r.scores.relevance}, persuasion={r.scores.persuasion}, purchase_intent={r.scores.purchase_intent}")
        lines.append(f"- objection_handling: {r.objection_handling.value}")
        lines.append(f"- tone_match: {r.tone_match}")
        if session:
            lines.append(f"- transcript:\n{session.transcript()}")
        lines.append("")

    return "\n".join(lines)


async def reason(
    eval_results: list[EvaluationResult],
    sessions: list[ConversationSession],
    top_n: int = 5,
) -> dict:
    """Analyze patterns by comparing top and bottom conversations.

    Args:
        eval_results: All evaluation results from E stage.
        sessions: All conversation sessions from A stage.
        top_n: Number of top/bottom conversations to compare.

    Returns:
        Dict with winning_patterns, losing_patterns, cluster_insights, etc.
    """
    top, bottom = get_top_bottom_results(eval_results, n=top_n)

    template = _load_reason_prompt()
    top_text = _format_conversations(top, sessions, "TOP")
    bottom_text = _format_conversations(bottom, sessions, "BOTTOM")

    system_prompt = template.replace("{top_conversations}", top_text).replace("{bottom_conversations}", bottom_text)

    user_message = (
        "위 상위/하위 대화를 비교 분석하세요.\n"
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
    result.setdefault("winning_patterns", [])
    result.setdefault("losing_patterns", [])
    result.setdefault("cluster_insights", {})

    logger.info(
        f"R stage: Found {len(result['winning_patterns'])} winning, "
        f"{len(result['losing_patterns'])} losing patterns"
    )
    return result
