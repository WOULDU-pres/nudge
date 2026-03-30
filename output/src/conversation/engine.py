"""Conversation engine — runs turn-based sales/customer dialogues."""

from __future__ import annotations

from src.agents.sales_agent import SalesAgent
from src.agents.customer_agent import CustomerAgent
from src.conversation.rules import check_early_exit, truncate_message


async def run_conversation(
    sales_agent: SalesAgent,
    customer_agent: CustomerAgent,
    strategy_id: str,
    persona_id: str,
    max_turns: int = 3,
) -> dict:
    """Run a turn-based conversation between a sales agent and customer agent.

    Each "turn" consists of one sales message and one customer response.
    The sales agent always speaks first.

    Args:
        sales_agent: The sales agent instance.
        customer_agent: The customer agent instance.
        strategy_id: The strategy identifier.
        persona_id: The persona identifier.
        max_turns: Maximum number of turn pairs (default: 3).

    Returns:
        A conversation session dict matching conversation-session.schema.json:
        {session_id, strategy_id, persona_id, turns: [{role, content}], ended_by}
    """
    session_id = f"{strategy_id}_{persona_id}"
    turns: list[dict] = []
    ended_by = "turn_limit"

    for turn_idx in range(max_turns):
        # Sales agent speaks
        sales_message = await sales_agent.generate_message(turns, turn_idx)
        sales_message = truncate_message(sales_message)
        turns.append({"role": "agent", "content": sales_message})

        # Customer agent responds
        customer_message = await customer_agent.generate_response(turns, turn_idx)
        customer_message = truncate_message(customer_message)
        turns.append({"role": "persona", "content": customer_message})

        # Check for early exit (customer expressed purchase intent)
        if check_early_exit(customer_message):
            ended_by = "keyword_detected"
            break

    return {
        "session_id": session_id,
        "strategy_id": strategy_id,
        "persona_id": persona_id,
        "turns": turns,
        "ended_by": ended_by,
    }
