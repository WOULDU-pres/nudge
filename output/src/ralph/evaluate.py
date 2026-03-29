"""E (Evaluate) — Judge all conversation sessions."""
import asyncio
import logging

from src.conversation.turn import ConversationSession
from src.evaluation.evaluator import judge_conversation
from src.evaluation.schema import EvaluationResult
from src.personas.schema import Persona

logger = logging.getLogger(__name__)


async def evaluate(
    sessions: list[ConversationSession],
    personas: list[Persona],
    max_concurrent: int = 20,
) -> list[EvaluationResult]:
    """Evaluate all conversation sessions using the Judge LLM.

    Args:
        sessions: Completed conversation sessions from A stage.
        personas: All personas (for lookup by persona_id).
        max_concurrent: Max parallel judge calls.

    Returns:
        List of EvaluationResult objects.
    """
    # Build persona lookup
    persona_map = {p.persona_id: p for p in personas}
    semaphore = asyncio.Semaphore(max_concurrent)

    async def _judge_with_sem(session: ConversationSession) -> EvaluationResult:
        async with semaphore:
            persona = persona_map.get(session.persona_id)
            if persona is None:
                return EvaluationResult.error_fallback(
                    session.session_id, session.strategy_id, session.persona_id,
                    f"Persona {session.persona_id} not found"
                )
            return await judge_conversation(session, persona)

    logger.info(f"E stage: Evaluating {len(sessions)} conversations (concurrency={max_concurrent})")

    tasks = [_judge_with_sem(s) for s in sessions]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Handle exceptions
    eval_results = []
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            s = sessions[i]
            logger.error(f"Judge failed for {s.session_id}: {r}")
            eval_results.append(
                EvaluationResult.error_fallback(
                    s.session_id, s.strategy_id, s.persona_id, str(r)
                )
            )
        else:
            eval_results.append(r)

    error_count = sum(1 for r in eval_results if r.outcome.value == "error")
    logger.info(f"E stage: Completed {len(eval_results)} evaluations ({error_count} errors)")
    return eval_results
