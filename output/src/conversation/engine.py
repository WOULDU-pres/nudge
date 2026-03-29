"""Turn-based conversation orchestration engine."""
import logging
from typing import Protocol, runtime_checkable

from src.conversation.turn import (
    Turn,
    Role,
    ConversationSession,
    EndReason,
)
from src.conversation.rules import should_end_conversation

logger = logging.getLogger(__name__)


@runtime_checkable
class SalesAgentProtocol(Protocol):
    """Protocol for sales agent — must implement send_opening and respond."""

    async def send_opening(self) -> str: ...
    async def respond(self, conversation_history: str) -> str: ...


@runtime_checkable
class CustomerAgentProtocol(Protocol):
    """Protocol for customer agent — must implement respond."""

    async def respond(self, conversation_history: str) -> str: ...


async def run_conversation(
    sales_agent: SalesAgentProtocol,
    customer_agent: CustomerAgentProtocol,
    strategy_id: str,
    persona_id: str,
    max_round_trips: int = 3,
) -> ConversationSession:
    """Run a turn-based conversation between sales agent and customer persona.

    Conversation flow (default 3 round-trips = 6 messages):
      Turn 0: Sales Agent sends opening (gets product + strategy context)
      Turn 1: Customer Agent responds
      Turn 2: Sales Agent responds (gets conversation history)
      Turn 3: Customer Agent responds
      Turn 4: Sales Agent responds
      Turn 5: Customer Agent final response

    Args:
        sales_agent: Agent implementing SalesAgentProtocol.
        customer_agent: Agent implementing CustomerAgentProtocol.
        strategy_id: Strategy identifier for this conversation.
        persona_id: Persona identifier for this conversation.
        max_round_trips: Number of agent-persona exchanges (default: 3).

    Returns:
        Completed ConversationSession with all turns and end reason.
    """
    session_id = f"conv-{strategy_id}-{persona_id}"
    max_turns = max_round_trips * 2  # Each round-trip = 2 turns

    session = ConversationSession(
        session_id=session_id,
        strategy_id=strategy_id,
        persona_id=persona_id,
    )

    logger.info(f"Starting conversation {session_id} ({max_round_trips} round-trips)")

    try:
        for turn_idx in range(max_turns):
            is_agent_turn = turn_idx % 2 == 0  # Even turns = agent, odd = persona

            if is_agent_turn:
                # Sales agent turn
                if turn_idx == 0:
                    # Opening message — agent uses product/strategy context
                    message = await sales_agent.send_opening()
                else:
                    # Follow-up — agent gets conversation history
                    history = session.to_history_text()
                    message = await sales_agent.respond(history)

                session.turns.append(Turn(role=Role.AGENT, content=message))
                logger.debug(f"[{session_id}] Turn {turn_idx} (Agent): {message[:80]}...")

            else:
                # Customer persona turn
                history = session.to_history_text()
                message = await customer_agent.respond(history)

                session.turns.append(Turn(role=Role.PERSONA, content=message))
                logger.debug(f"[{session_id}] Turn {turn_idx} (Customer): {message[:80]}...")

                # Check end conditions after customer responds
                should_end, reason = should_end_conversation(
                    current_turn=turn_idx + 1,
                    max_turns=max_turns,
                    last_customer_message=message,
                )
                if should_end and reason == "keyword_detected":
                    session.ended_by = EndReason.KEYWORD_DETECTED
                    logger.info(
                        f"[{session_id}] Customer exit keyword detected at turn {turn_idx}"
                    )
                    break

        else:
            # Loop completed without break — ended by turn limit
            session.ended_by = EndReason.TURN_LIMIT

    except Exception as e:
        session.ended_by = EndReason.ERROR
        session.error_message = str(e)
        logger.error(f"[{session_id}] Conversation error: {e}")

    logger.info(
        f"Completed {session_id}: {session.turn_count} turns, ended_by={session.ended_by.value}"
    )
    return session
