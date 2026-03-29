"""Conversation module — turn-based simulation engine."""
from src.conversation.turn import Turn, Role, ConversationSession, EndReason
from src.conversation.rules import check_exit_keyword, should_end_conversation
from src.conversation.engine import run_conversation

__all__ = [
    "Turn",
    "Role",
    "ConversationSession",
    "EndReason",
    "check_exit_keyword",
    "should_end_conversation",
    "run_conversation",
]
