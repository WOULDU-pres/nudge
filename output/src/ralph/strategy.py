"""Strategy 모델 (참고용)."""
from __future__ import annotations
from pydantic import BaseModel


class Strategy(BaseModel):
    strategy_id: str
    hypothesis: str = ""
    approach: str = ""
    opening_style: str = ""
    objection_handling: str = ""
    tone: str = ""
