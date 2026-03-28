"""대화 턴 & 세션 모델."""
from __future__ import annotations
from pydantic import BaseModel


class Turn(BaseModel):
    role: str  # "agent" | "persona"
    content: str


class ConversationSession(BaseModel):
    session_id: str
    strategy_id: str
    persona_id: str
    turns: list[Turn]
    ended_by: str = "turn_limit"  # turn_limit | keyword_detected | customer_exit | error
