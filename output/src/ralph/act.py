"""A(Act) stage: Run simulated sales conversations."""

import asyncio
import logging

from src.agents.sales_agent import SalesAgent
from src.agents.customer_agent import CustomerAgent
from src.conversation.engine import run_conversation

logger = logging.getLogger(__name__)


async def act(
    strategy: dict,
    persona,
    product: dict,
    max_turns: int = 3,
) -> dict:
    """Run a single simulated conversation.

    Args:
        strategy: Strategy dict for the sales agent.
        persona: Persona object for the customer agent.
        product: Product information dict.
        max_turns: Maximum conversation round-trips.

    Returns:
        Conversation session dict matching conversation-session schema.
    """
    persona_id = persona.persona_id if hasattr(persona, "persona_id") else persona.get("persona_id", "unknown")
    strategy_id = strategy.get("strategy_id", "unknown")

    sales_agent = SalesAgent(strategy=strategy, product=product)
    customer_agent = CustomerAgent(persona=persona)

    session = await run_conversation(
        sales_agent=sales_agent,
        customer_agent=customer_agent,
        strategy_id=strategy_id,
        persona_id=persona_id,
        max_turns=max_turns,
    )

    return session


async def act_all(
    pairs: list[tuple],
    product: dict,
    max_turns: int,
    semaphore: asyncio.Semaphore,
) -> list[dict]:
    """Run all conversations concurrently with semaphore control.

    Retries failed conversations up to 2 times.

    Args:
        pairs: List of (strategy, persona) tuples.
        product: Product information dict.
        max_turns: Maximum conversation round-trips.
        semaphore: Asyncio semaphore for concurrency control.

    Returns:
        List of conversation session dicts.
    """
    max_retries = 2

    async def _run_with_retry(strategy: dict, persona, idx: int) -> dict:
        persona_id = persona.persona_id if hasattr(persona, "persona_id") else persona.get("persona_id", "unknown")
        strategy_id = strategy.get("strategy_id", "unknown")

        for attempt in range(max_retries + 1):
            try:
                async with semaphore:
                    result = await act(strategy, persona, product, max_turns)
                    return result
            except Exception as exc:
                if attempt < max_retries:
                    logger.warning(
                        "Conversation %s/%s failed (attempt %d/%d): %s",
                        strategy_id,
                        persona_id,
                        attempt + 1,
                        max_retries + 1,
                        exc,
                    )
                    await asyncio.sleep(0.5 * (attempt + 1))
                else:
                    logger.error(
                        "Conversation %s/%s failed after %d attempts: %s",
                        strategy_id,
                        persona_id,
                        max_retries + 1,
                        exc,
                    )
                    # Return error session
                    session_id = f"conv-{strategy_id}-{persona_id}"
                    return {
                        "session_id": session_id,
                        "strategy_id": strategy_id,
                        "persona_id": persona_id,
                        "turns": [
                            {
                                "role": "agent",
                                "content": "[ERROR] Conversation failed to complete.",
                            }
                        ],
                        "ended_by": "error",
                    }

    tasks = [
        _run_with_retry(strategy, persona, idx)
        for idx, (strategy, persona) in enumerate(pairs)
    ]

    results = await asyncio.gather(*tasks, return_exceptions=False)
    logger.info("Completed %d conversations", len(results))
    return list(results)
