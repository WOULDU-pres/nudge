"""Turn and ConversationSession Pydantic models."""
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class Role(str, Enum):
    """Speaker role in a conversation turn."""
    AGENT = "agent"
    PERSONA = "persona"


class Turn(BaseModel):
    """Single conversation turn."""
    role: Role
    content: str


class EndReason(str, Enum):
    """Why a conversation ended."""
    TURN_LIMIT = "turn_limit"
    KEYWORD_DETECTED = "keyword_detected"
    CUSTOMER_EXIT = "customer_exit"
    ERROR = "error"


class ConversationSession(BaseModel):
    """Complete conversation session between sales agent and customer persona."""
    session_id: str  # Format: conv-{strategy_id}-{persona_id}
    strategy_id: str
    persona_id: str
    turns: list[Turn] = Field(default_factory=list)
    ended_by: EndReason = EndReason.TURN_LIMIT
    error_message: Optional[str] = None

    @property
    def turn_count(self) -> int:
        """Total number of messages."""
        return len(self.turns)

    @property
    def round_trips(self) -> int:
        """Number of complete agent-persona exchanges."""
        return self.turn_count // 2

    def transcript(self) -> str:
        """Human-readable transcript of the conversation."""
        lines = []
        for i, turn in enumerate(self.turns):
            label = "Sales Agent" if turn.role == Role.AGENT else "Customer"
            lines.append(f"[Turn {i}] {label}: {turn.content}")
        return "\n\n".join(lines)

    def to_history_text(self) -> str:
        """Conversation history formatted for LLM context."""
        lines = []
        for turn in self.turns:
            label = "Agent" if turn.role == Role.AGENT else "Customer"
            lines.append(f"{label}: {turn.content}")
        return "\n".join(lines)
