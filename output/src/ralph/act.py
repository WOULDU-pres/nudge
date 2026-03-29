"""A (Act) — Run conversations: strategy x persona, with concurrency."""
import asyncio
import logging

from src.agents.sales_agent import SalesAgent
from src.agents.customer_agent import CustomerAgent
from src.conversation.engine import run_conversation
from src.conversation.turn import ConversationSession
from src.personas.schema import Persona

logger = logging.getLogger(__name__)


async def _run_single_conversation(
    strategy: dict,
    persona: Persona,
    product_brief: str,
    max_round_trips: int,
    semaphore: asyncio.Semaphore,
) -> ConversationSession:
    """Run a single strategy x persona conversation under semaphore."""
    async with semaphore:
        sales = SalesAgent(strategy=strategy, product_brief=product_brief)
        customer = CustomerAgent(persona=persona)

        session = await run_conversation(
            sales_agent=sales,
            customer_agent=customer,
            strategy_id=strategy.get("strategy_id", "unknown"),
            persona_id=persona.persona_id,
            max_round_trips=max_round_trips,
        )
        return session


async def act(
    strategies: list[dict],
    personas: list[Persona],
    product_brief: str,
    max_round_trips: int = 3,
    max_concurrent: int = 20,
) -> list[ConversationSession]:
    """Run all strategy x persona conversation pairs.

    Args:
        strategies: List of strategy dicts from H stage.
        personas: List of personas from P stage.
        product_brief: Product information text.
        max_round_trips: Turns per conversation (default 3).
        max_concurrent: Max parallel LLM calls.

    Returns:
        List of completed ConversationSession objects.
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    tasks = []
    for strategy in strategies:
        for persona in personas:
            tasks.append(
                _run_single_conversation(
                    strategy=strategy,
                    persona=persona,
                    product_brief=product_brief,
                    max_round_trips=max_round_trips,
                    semaphore=semaphore,
                )
            )

    total = len(tasks)
    logger.info(
        f"A stage: Running {total} conversations "
        f"({len(strategies)} strategies x {len(personas)} personas, "
        f"concurrency={max_concurrent})"
    )

    sessions = await asyncio.gather(*tasks, return_exceptions=True)

    # Handle exceptions
    results = []
    errors = 0
    for s in sessions:
        if isinstance(s, Exception):
            errors += 1
            logger.error(f"Conversation failed: {s}")
        else:
            results.append(s)

    logger.info(f"A stage: Completed {len(results)}/{total} conversations ({errors} errors)")
    return results
