"""R(Reason) stage: Analyze patterns from evaluation results."""

import json
import logging
from pathlib import Path

from config.settings import settings
from src.llm import call_llm, extract_json

logger = logging.getLogger(__name__)

_reason_system: str | None = None


def _get_reason_system() -> str:
    """Load reason-system.md template from PROMPTS_DIR."""
    global _reason_system
    if _reason_system is None:
        path = Path(settings.PROMPTS_DIR) / "reason-system.md"
        _reason_system = path.read_text(encoding="utf-8")
    return _reason_system


def _format_conversation_summary(session: dict, evaluation: dict) -> str:
    """Format a conversation + evaluation for analysis."""
    lines = [
        f"### Session: {session.get('session_id', 'unknown')}",
        f"- Strategy: {session.get('strategy_id', 'unknown')}",
        f"- Persona: {session.get('persona_id', 'unknown')}",
        f"- Score: {evaluation['scores']['total']}",
        f"- Outcome: {evaluation.get('outcome', 'unknown')}",
        f"- Reason: {evaluation.get('reason', 'N/A')}",
        "",
        "**대화:**",
    ]
    for turn in session.get("turns", []):
        role = turn.get("role", "unknown")
        content = turn.get("content", "")
        label = "세일즈" if role == "agent" else "고객"
        lines.append(f"[{label}] {content}")
    return "\n".join(lines)


async def reason(evaluations: list[dict], sessions: list[dict]) -> dict:
    """Analyze evaluation results to find winning and losing patterns.

    Selects top 5 and bottom 5 evaluations by score and builds
    a comparative analysis.

    Args:
        evaluations: List of evaluation result dicts.
        sessions: List of conversation session dicts.

    Returns:
        Reason dict with winning_patterns, losing_patterns, cluster_insights, etc.
    """
    # Filter out error evaluations
    valid_evals = [e for e in evaluations if e.get("outcome") != "error"]

    if not valid_evals:
        return {
            "winning_patterns": [],
            "losing_patterns": [],
            "cluster_insights": {},
        }

    # Sort by total score
    sorted_evals = sorted(
        valid_evals, key=lambda e: e["scores"]["total"], reverse=True
    )

    top_evals = sorted_evals[:5]
    bottom_evals = sorted_evals[-5:]

    # Build session lookup
    session_map = {s.get("session_id", ""): s for s in sessions}

    # Format top conversations
    top_texts = []
    for e in top_evals:
        session = session_map.get(e["session_id"], {})
        top_texts.append(_format_conversation_summary(session, e))

    # Format bottom conversations
    bottom_texts = []
    for e in bottom_evals:
        session = session_map.get(e["session_id"], {})
        bottom_texts.append(_format_conversation_summary(session, e))

    # Build prompt with placeholders filled
    system_template = _get_reason_system()
    system_prompt = system_template.replace(
        "{top_conversations}", "\n\n".join(top_texts)
    ).replace("{bottom_conversations}", "\n\n".join(bottom_texts))

    user_prompt = (
        f"총 {len(valid_evals)}개 대화를 분석합니다.\n"
        f"평균 점수: {sum(e['scores']['total'] for e in valid_evals) / len(valid_evals):.1f}\n"
        f"상위 5개와 하위 5개 대화의 패턴을 비교 분석하여 JSON으로 응답하세요."
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
        logger.error("Failed to parse reason response, using empty result")
        parsed = {}

    # Ensure required fields exist
    result = {
        "winning_patterns": parsed.get("winning_patterns", []),
        "losing_patterns": parsed.get("losing_patterns", []),
        "cluster_insights": parsed.get("cluster_insights", {}),
    }

    # Include optional analysis fields if present
    for key in (
        "objection_handling_analysis",
        "tone_matching_analysis",
        "funnel_analysis",
        "technique_effectiveness",
    ):
        if key in parsed:
            result[key] = parsed[key]

    return result
