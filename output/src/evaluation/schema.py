"""Evaluation data models — matches evaluation-result.schema.json."""
from enum import Enum
from pydantic import BaseModel, Field


class Outcome(str, Enum):
    """Conversation outcome classification."""
    CONVERTED = "converted"
    INTERESTED = "interested"
    NEUTRAL = "neutral"
    RESISTANT = "resistant"
    LOST = "lost"
    ERROR = "error"


class ObjectionHandling(str, Enum):
    """How the agent handled customer objections."""
    NONE = "none"
    IGNORED = "ignored"
    ACKNOWLEDGED = "acknowledged"
    ACKNOWLEDGED_AND_PIVOTED = "acknowledged_and_pivoted"


class Scores(BaseModel):
    """4-dimension evaluation scores (0-25 each, 0-100 total)."""
    engagement: int = Field(ge=0, le=25, description="참여도")
    relevance: int = Field(ge=0, le=25, description="적합성")
    persuasion: int = Field(ge=0, le=25, description="설득력")
    purchase_intent: int = Field(ge=0, le=25, description="구매의향")
    total: int = Field(ge=0, le=100, description="합계")


class EvaluationResult(BaseModel):
    """Result of Judge evaluating a single conversation session.

    Conforms to contracts/schemas/evaluation-result.schema.json.
    """
    session_id: str
    strategy_id: str
    persona_id: str
    scores: Scores
    outcome: Outcome
    reason: str = Field(description="판정 근거 (한 줄)")

    # Extended fields from judge-system.md (not in base schema but useful)
    funnel_progress: int = Field(default=0, ge=0, le=3, description="AIDA 퍼널 진행도 0-3")
    objection_handling: ObjectionHandling = Field(
        default=ObjectionHandling.NONE,
        description="반론 대응 수준",
    )
    tone_match: bool = Field(default=False, description="고객 톤 매칭 여부")

    @classmethod
    def error_fallback(
        cls,
        session_id: str,
        strategy_id: str,
        persona_id: str,
        error_msg: str,
    ) -> "EvaluationResult":
        """Create a 0-score fallback result for evaluation failures."""
        return cls(
            session_id=session_id,
            strategy_id=strategy_id,
            persona_id=persona_id,
            scores=Scores(
                engagement=0,
                relevance=0,
                persuasion=0,
                purchase_intent=0,
                total=0,
            ),
            outcome=Outcome.ERROR,
            reason=f"Evaluation failed: {error_msg}",
            funnel_progress=0,
            objection_handling=ObjectionHandling.NONE,
            tone_match=False,
        )

    def to_schema_dict(self) -> dict:
        """Export as dict conforming to evaluation-result.schema.json (strict)."""
        return {
            "session_id": self.session_id,
            "strategy_id": self.strategy_id,
            "persona_id": self.persona_id,
            "scores": {
                "engagement": self.scores.engagement,
                "relevance": self.scores.relevance,
                "persuasion": self.scores.persuasion,
                "purchase_intent": self.scores.purchase_intent,
                "total": self.scores.total,
            },
            "outcome": self.outcome.value,
            "reason": self.reason,
        }
