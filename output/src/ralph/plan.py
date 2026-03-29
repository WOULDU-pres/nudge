"""P (Plan) — Select personas for this run. Pure code, no LLM."""
import logging
from pathlib import Path

from src.personas.loader import load_personas
from src.personas.schema import Persona

logger = logging.getLogger(__name__)


def plan_personas(count: int = 50) -> list[Persona]:
    """Select personas for this simulation run.

    Args:
        count: Number of personas to load (DEV=10, TEST=50, DEMO=200).

    Returns:
        List of Persona objects sorted by ID.
    """
    from config.settings import settings

    personas = load_personas(settings.personas_dir, count=count)
    logger.info(f"P stage: Selected {len(personas)} personas from {settings.personas_dir}")

    if not personas:
        raise ValueError(f"No personas found in {settings.personas_dir}")

    return personas
