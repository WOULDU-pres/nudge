"""Load personas from data/personas/ directory."""
import json
import re
from pathlib import Path
from typing import Optional
from .schema import Persona, PersonaProfile


def load_single_persona(persona_dir: Path) -> Optional[Persona]:
    """Load a single persona from its directory."""
    profile_path = persona_dir / "profile.json"
    soul_path = persona_dir / "soul.md"
    
    if not profile_path.exists() or not soul_path.exists():
        return None
    
    with open(profile_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    
    with open(soul_path, "r", encoding="utf-8") as f:
        soul_md = f.read()
    
    # Strip persuasion points from soul_md for customer agent
    # (the soul has persuasion_triggers that shouldn't leak to customer agent)
    
    # Extract cluster tags from profile
    cluster_tags = raw.get("cluster_tags", [])
    if not cluster_tags:
        # Try to extract from archetype
        archetype = raw.get("archetype", "unknown")
        cluster_tags = [archetype.lower().replace(" ", "_")]
    
    profile = PersonaProfile(
        persona_id=raw.get("persona_id", persona_dir.name),
        archetype=raw.get("archetype", "unknown"),
        variation=raw.get("variation", ""),
        cluster_tags=cluster_tags,
        raw=raw,
    )
    
    return Persona(
        persona_id=profile.persona_id,
        profile=profile,
        soul_md=soul_md,
    )


def load_personas(personas_dir: Path, count: int = 50) -> list[Persona]:
    """Load up to `count` personas sorted by ID."""
    personas = []
    
    # Get sorted persona directories
    dirs = sorted(
        [d for d in personas_dir.iterdir() if d.is_dir() and d.name.startswith("P")],
        key=lambda d: int(d.name[1:]) if d.name[1:].isdigit() else 0
    )
    
    for d in dirs[:count]:
        p = load_single_persona(d)
        if p:
            personas.append(p)
    
    return personas


def get_clusters(personas: list[Persona]) -> dict[str, list[Persona]]:
    """Group personas by primary cluster tag."""
    clusters: dict[str, list[Persona]] = {}
    for p in personas:
        tag = p.primary_cluster
        if tag not in clusters:
            clusters[tag] = []
        clusters[tag].append(p)
    return clusters
