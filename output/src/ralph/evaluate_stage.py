"""E(Evaluate) stage: Evaluate all conversation sessions."""

import asyncio
import logging

from src.evaluation.evaluator import evaluate_conversation

logger = logging.getLogger(__name__)


async def evaluate_all(
    sessions: list[dict],
    strategies: list[dict],
    semaphore: asyncio.Semaphore,
) -> list[dict]:
    """Evaluate all conversation sessions concurrently.

    Args:
        sessions: List of conversation session dicts.
        strategies: List of strategy dicts (for lookup by strategy_id).
        semaphore: Asyncio semaphore for concurrency control.

    Returns:
        List of evaluation result dicts.
    """
    # Build strategy lookup
    strategy_map = {s["strategy_id"]: s for s in strategies}

    async def _evaluate_one(session: dict) -> dict:
        strategy_id = session.get("strategy_id", "unknown")
        persona_id = session.get("persona_id", "unknown")
        strategy = strategy_map.get(strategy_id, {"strategy_id": strategy_id})

        async with semaphore:
            return await evaluate_conversation(session, strategy, persona_id)

    tasks = [_evaluate_one(session) for session in sessions]
    results = await asyncio.gather(*tasks, return_exceptions=False)

    logger.info("Evaluated %d sessions", len(results))
    return list(results)
