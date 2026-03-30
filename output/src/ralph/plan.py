"""P(Plan) stage: Plan all conversation pairs."""

import logging

logger = logging.getLogger(__name__)


def plan_conversations(
    strategies: list[dict], personas: list
) -> list[tuple]:
    """Generate all (strategy, persona) pairs to simulate.

    Args:
        strategies: List of strategy dicts.
        personas: List of Persona objects.

    Returns:
        List of (strategy, persona) tuples.
        Total pairs = len(strategies) * len(personas).
    """
    pairs = []
    for strategy in strategies:
        for persona in personas:
            pairs.append((strategy, persona))

    logger.info(
        "Planned %d conversations (%d strategies x %d personas)",
        len(pairs),
        len(strategies),
        len(personas),
    )
    return pairs
