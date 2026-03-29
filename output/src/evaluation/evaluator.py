"""Judge evaluator — scores a conversation transcript via LLM.

Uses prompts/judge-system.md as the system prompt.
Calls expensive model with low temperature for scoring consistency.
Returns EvaluationResult conforming to evaluation-result.schema.json.
"""
import json
import logging
from pathlib import Path

from src.llm import call_llm_expensive, extract_json
from src.conversation.turn import ConversationSession
from src.personas.schema import Persona
from src.evaluation.schema import (
    EvaluationResult,
    Scores,
    Outcome,
    ObjectionHandling,
)

logger = logging.getLogger(__name__)

# Load judge system prompt once
_JUDGE_PROMPT: str | None = None


def _load_judge_prompt() -> str:
    """Load and cache the judge system prompt from harness prompts."""
    global _JUDGE_PROMPT
    if _JUDGE_PROMPT is not None:
        return _JUDGE_PROMPT

    prompts_dir = Path(__file__).parent.parent.parent.parent / "harness" / "prompts"
    judge_path = prompts_dir / "judge-system.md"

    if not judge_path.exists():
        raise FileNotFoundError(f"Judge prompt not found: {judge_path}")

    _JUDGE_PROMPT = judge_path.read_text(encoding="utf-8")
    return _JUDGE_PROMPT


def _format_transcript_for_judge(session: ConversationSession, persona: Persona) -> str:
    """Format conversation + persona context as the user message for the judge."""
    lines = []

    # Persona context
    lines.append("## 고객 프로필")
    lines.append(f"- persona_id: {persona.persona_id}")
    lines.append(f"- archetype: {persona.profile.archetype}")
    lines.append(f"- cluster_tags: {', '.join(persona.profile.cluster_tags)}")
    if persona.profile.variation:
        lines.append(f"- variation: {persona.profile.variation}")
    lines.append("")

    # Session metadata
    lines.append("## 대화 정보")
    lines.append(f"- session_id: {session.session_id}")
    lines.append(f"- strategy_id: {session.strategy_id}")
    lines.append(f"- ended_by: {session.ended_by.value}")
    lines.append("")

    # Transcript
    lines.append("## 대화 Transcript")
    lines.append("")
    lines.append(session.transcript())

    return "\n".join(lines)


def _clamp(value: int, lo: int, hi: int) -> int:
    """Clamp value within [lo, hi]."""
    return max(lo, min(hi, value))


def _parse_judge_response(raw: dict, session: ConversationSession) -> EvaluationResult:
    """Parse the raw JSON response from the judge into an EvaluationResult."""
    # Extract and clamp scores
    engagement = _clamp(int(raw.get("engagement", 0)), 0, 25)
    relevance = _clamp(int(raw.get("relevance", 0)), 0, 25)
    persuasion = _clamp(int(raw.get("persuasion", 0)), 0, 25)
    purchase_intent = _clamp(int(raw.get("purchase_intent", 0)), 0, 25)

    # Total: use judge's total if provided and valid, otherwise compute
    raw_total = int(raw.get("total", 0))
    computed_total = engagement + relevance + persuasion + purchase_intent
    total = raw_total if 0 <= raw_total <= 100 else computed_total
    # If judge total deviates from sum by more than 2, use computed
    if abs(total - computed_total) > 2:
        total = computed_total

    scores = Scores(
        engagement=engagement,
        relevance=relevance,
        persuasion=persuasion,
        purchase_intent=purchase_intent,
        total=_clamp(total, 0, 100),
    )

    # Outcome
    outcome_str = raw.get("outcome", "neutral")
    try:
        outcome = Outcome(outcome_str)
    except ValueError:
        # Map total to outcome if judge returned invalid value
        if total >= 80:
            outcome = Outcome.CONVERTED
        elif total >= 60:
            outcome = Outcome.INTERESTED
        elif total >= 40:
            outcome = Outcome.NEUTRAL
        elif total >= 20:
            outcome = Outcome.RESISTANT
        else:
            outcome = Outcome.LOST

    # Funnel progress
    funnel_progress = _clamp(int(raw.get("funnel_progress", 0)), 0, 3)

    # Objection handling
    obj_str = raw.get("objection_handling", "none")
    try:
        objection_handling = ObjectionHandling(obj_str)
    except ValueError:
        objection_handling = ObjectionHandling.NONE

    # Tone match
    tone_match = bool(raw.get("tone_match", False))

    # Reason
    reason = str(raw.get("reason", "채점 완료"))

    return EvaluationResult(
        session_id=session.session_id,
        strategy_id=session.strategy_id,
        persona_id=session.persona_id,
        scores=scores,
        outcome=outcome,
        reason=reason,
        funnel_progress=funnel_progress,
        objection_handling=objection_handling,
        tone_match=tone_match,
    )


async def judge_conversation(
    session: ConversationSession,
    persona: Persona,
) -> EvaluationResult:
    """Evaluate a conversation session using the Judge LLM.

    Args:
        session: Completed conversation session with turns.
        persona: The customer persona involved in the conversation.

    Returns:
        EvaluationResult with 4-dimension scores and outcome.
        On failure, returns a 0-score error fallback.
    """
    try:
        system_prompt = _load_judge_prompt()
        user_message = _format_transcript_for_judge(session, persona)

        # Call expensive model with low temperature for consistency
        response_text = await call_llm_expensive(
            system_prompt=system_prompt,
            user_message=user_message,
            temperature=0.1,
            expect_json=True,
        )

        raw = json.loads(response_text) if isinstance(response_text, str) else response_text
        result = _parse_judge_response(raw, session)

        logger.info(
            f"Evaluated {session.session_id}: "
            f"total={result.scores.total}, outcome={result.outcome.value}, "
            f"funnel={result.funnel_progress}"
        )
        return result

    except Exception as e:
        logger.error(f"Judge evaluation failed for {session.session_id}: {e}")
        return EvaluationResult.error_fallback(
            session_id=session.session_id,
            strategy_id=session.strategy_id,
            persona_id=session.persona_id,
            error_msg=str(e),
        )
