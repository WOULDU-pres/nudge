"""페르소나 Pydantic 모델 (참고용)."""
from __future__ import annotations
from pydantic import BaseModel


class PersonaProfile(BaseModel):
    persona_id: str
    archetype_id: str = ""
    archetype_name: str = ""
    cluster_tags: list[str] = []


class Persona(BaseModel):
    id: str
    profile: dict
    soul: str = ""
    cluster_tags: list[str] = []
