"""Persona data models."""
from pydantic import BaseModel
from typing import Optional


class PersonaProfile(BaseModel):
    """Persona profile from profile.json."""
    persona_id: str
    archetype: str
    variation: str = ""
    cluster_tags: list[str] = []
    
    # Simplified — we store the full dict for flexibility
    raw: dict = {}
    
    @property
    def primary_cluster(self) -> str:
        """Primary cluster tag (first one)."""
        return self.cluster_tags[0] if self.cluster_tags else "unknown"


class Persona(BaseModel):
    """Full persona with profile + soul."""
    persona_id: str
    profile: PersonaProfile
    soul_md: str  # Full soul.md content
    
    @property
    def cluster_tags(self) -> list[str]:
        return self.profile.cluster_tags
    
    @property
    def primary_cluster(self) -> str:
        return self.profile.primary_cluster
