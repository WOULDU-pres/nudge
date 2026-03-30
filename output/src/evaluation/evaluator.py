"""Evaluate a conversation session using the Judge LLM."""

import json
import logging
from pathlib import Path

from config.settings import settings
from src.llm import call_llm, extract_json

logger = logging.getLogger(__name__)

# Load judge system prompt once at module level
_judge_system: str | None = None


def _get_judge_system() -> str:
    """Load judge-system.md template from PROMPTS_DIR."""
    global _judge_system
    if _judge_system is None:
        path = Path(settings.PROMPTS_DIR) / "judge-system.md"
        _judge_system = path.read_text(encoding="utf-8")
    return _judge_system


def _format_transcript(turns: list[dict]) -> str:
    """Format conversation turns into a readable transcript."""
    lines = []
    for turn in turns:
        role = turn.get("role", "unknown")
        content = turn.get("content", "")
        label = "세일즈" if role == "agent" else "고객"
        lines.append(f"[{label}] {content}")
    return "\n\n".join(lines)


async def evaluate_conversation(
    session: dict, strategy: dict, persona_id: str
) -> dict:
    """Evaluate a single conversation session.

    Args:
        session: Conversation session dict (matching conversation-session schema).
        strategy: The strategy dict used for this conversation.
        persona_id: The persona ID for this conversation.

    Returns:
        Evaluation result dict matching evaluation-result schema.
    """
    session_id = session.get("session_id", "unknown")
    strategy_id = session.get("strategy_id", strategy.get("strategy_id", "unknown"))

    try:
        system_prompt = _get_judge_system()
        transcript = _format_transcript(session.get("turns", []))

        user_prompt = (
            f"## 대화 정보\n"
            f"- Strategy: {strategy_id}\n"
            f"- Persona: {persona_id}\n"
            f"- Strategy hypothesis: {strategy.get('hypothesis', 'N/A')}\n"
            f"- Strategy tone: {strategy.get('tone', 'N/A')}\n"
            f"- Ended by: {session.get('ended_by', 'unknown')}\n\n"
            f"## 대화 transcript\n\n{transcript}"
        )

        response = await call_llm(
            prompt=user_prompt,
            system=system_prompt,
            model=settings.expensive_model,
            temperature=settings.JUDGE_TEMPERATURE,
        )

        parsed = extract_json(response)

        # Extract scores
        scores = {
            "engagement": int(parsed.get("engagement", 0)),
            "relevance": int(parsed.get("relevance", 0)),
            "persuasion": int(parsed.get("persuasion", 0)),
            "purchase_intent": int(parsed.get("purchase_intent", 0)),
            "total": int(parsed.get("total", 0)),
        }

        # Clamp scores to valid ranges
        for key in ("engagement", "relevance", "persuasion", "purchase_intent"):
            scores[key] = max(0, min(25, scores[key]))
        scores["total"] = max(0, min(100, scores["total"]))

        # Validate total equals sum
        computed_total = sum(
            scores[k] for k in ("engagement", "relevance", "persuasion", "purchase_intent")
        )
        if scores["total"] != computed_total:
            scores["total"] = computed_total

        outcome = parsed.get("outcome", "neutral")
        valid_outcomes = {"converted", "interested", "neutral", "resistant", "lost", "error"}
        if outcome not in valid_outcomes:
            outcome = "neutral"

        reason = parsed.get("reason", "No reason provided")

        return {
            "session_id": session_id,
            "strategy_id": strategy_id,
            "persona_id": persona_id,
            "scores": scores,
            "outcome": outcome,
            "reason": str(reason),
        }

    except Exception as exc:
        logger.error(
            "Evaluation failed for session %s: %s", session_id, exc, exc_info=True
        )
        return {
            "session_id": session_id,
            "strategy_id": strategy_id,
            "persona_id": persona_id,
            "scores": {
                "engagement": 0,
                "relevance": 0,
                "persuasion": 0,
                "purchase_intent": 0,
                "total": 0,
            },
            "outcome": "error",
            "reason": f"Evaluation error: {exc}",
        }
