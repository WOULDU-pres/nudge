"""Persona loader — reads persona directories and builds Persona objects."""

import json
import logging
from collections import defaultdict
from pathlib import Path

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Persona(BaseModel):
    """A single synthetic persona with full profile and soul description."""

    persona_id: str
    archetype_id: str
    archetype_name: str
    variation_slot: str
    summary: str
    cluster_tags: list[str]
    profile: dict
    purchase_context: dict
    decision_style: dict
    voice_preferences: dict
    persuasion_triggers: list[str]
    objection_profile: dict
    likely_reaction_style: dict
    soul_md: str


def load_personas(personas_dir: str, mode: str = "DEMO") -> list[Persona]:
    """Load personas from P* directories under personas_dir.

    Each persona directory (e.g. P001/) should contain:
      - profile.json  — full persona profile
      - soul.md       — narrative soul description

    Args:
        personas_dir: Path to the directory containing P* persona folders.
        mode: One of DEV (10), TEST (50), DEMO (200).

    Returns:
        Sorted list of Persona objects, trimmed to mode count.
    """
    mode_limits = {"DEV": 10, "TEST": 50, "DEMO": 200}
    limit = mode_limits.get(mode.upper(), 200)

    base_path = Path(personas_dir)
    if not base_path.exists():
        logger.warning("Personas directory does not exist: %s", base_path)
        return []

    # Find all P* directories, sorted by name
    persona_dirs = sorted(
        [d for d in base_path.iterdir() if d.is_dir() and d.name.startswith("P")],
        key=lambda d: d.name,
    )

    personas: list[Persona] = []

    for pdir in persona_dirs:
        profile_path = pdir / "profile.json"
        soul_path = pdir / "soul.md"

        if not profile_path.exists():
            logger.warning("Missing profile.json in %s, skipping", pdir.name)
            continue

        try:
            profile_data = json.loads(profile_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to read profile.json in %s: %s", pdir.name, exc)
            continue

        # Read soul.md (optional)
        soul_md = ""
        if soul_path.exists():
            try:
                soul_md = soul_path.read_text(encoding="utf-8")
            except OSError as exc:
                logger.warning("Failed to read soul.md in %s: %s", pdir.name, exc)

        try:
            persona = Persona(
                persona_id=profile_data.get("persona_id", pdir.name),
                archetype_id=profile_data.get("archetype_id", ""),
                archetype_name=profile_data.get("archetype_name", ""),
                variation_slot=profile_data.get("variation_slot", ""),
                summary=profile_data.get("summary", ""),
                cluster_tags=profile_data.get("cluster_tags", []),
                profile=profile_data.get("profile", {}),
                purchase_context=profile_data.get("purchase_context", {}),
                decision_style=profile_data.get("decision_style", {}),
                voice_preferences=profile_data.get("voice_preferences", {}),
                persuasion_triggers=profile_data.get("persuasion_triggers", []),
                objection_profile=profile_data.get("objection_profile", {}),
                likely_reaction_style=profile_data.get("likely_reaction_style", {}),
                soul_md=soul_md,
            )
            personas.append(persona)
        except Exception as exc:
            logger.warning("Failed to create Persona from %s: %s", pdir.name, exc)
            continue

    # Sort by persona_id and trim to mode limit
    personas.sort(key=lambda p: p.persona_id)
    personas = personas[:limit]

    logger.info("Loaded %d personas (mode=%s, limit=%d)", len(personas), mode, limit)
    return personas


def get_cluster_map(personas: list[Persona]) -> dict[str, list[Persona]]:
    """Group personas by archetype_id.

    Args:
        personas: List of Persona objects.

    Returns:
        Dictionary mapping archetype_id to list of Personas in that cluster.
    """
    cluster_map: dict[str, list[Persona]] = defaultdict(list)
    for persona in personas:
        cluster_map[persona.archetype_id].append(persona)
    return dict(cluster_map)
