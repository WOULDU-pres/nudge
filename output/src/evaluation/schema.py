"""평가 결과 모델."""
from __future__ import annotations
from pydantic import BaseModel


class Scores(BaseModel):
    engagement: int = 0
    relevance: int = 0
    persuasion: int = 0
    purchase_intent: int = 0
    total: int = 0


class EvaluationResult(BaseModel):
    session_id: str
    strategy_id: str
    persona_id: str
    scores: Scores
    outcome: str = "neutral"  # converted|interested|neutral|resistant|lost|error
    reason: str = ""
