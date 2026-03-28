"""턴 기반 대화 엔진."""
from __future__ import annotations

import logging
from src.agents.sales_agent import SalesAgent
from src.agents.customer_agent import CustomerAgent
from src.conversation.turn import Turn, ConversationSession
from src.conversation.rules import check_exit
from config.settings import get_settings

logger = logging.getLogger("ralphthon.conversation")


async def run_conversation(
    sales_agent: SalesAgent,
    customer_agent: CustomerAgent,
    strategy_id: str,
    persona_id: str,
    turns: int | None = None,
) -> ConversationSession:
    """Sales Agent ↔ Customer Agent 대화 실행.

    Args:
        sales_agent: 판매 에이전트
        customer_agent: 고객 에이전트
        strategy_id: 전략 ID
        persona_id: 페르소나 ID
        turns: 왕복 턴 수 (기본: settings.CONVERSATION_TURNS)

    Returns:
        ConversationSession
    """
    settings = get_settings()
    if turns is None:
        turns = settings.RALPHTHON_CONVERSATION_TURNS

    session_id = f"conv-{strategy_id}-{persona_id}"
    conversation: list[Turn] = []
    ended_by = "turn_limit"

    history = ""

    for t in range(turns):
        # ── Sales Agent turn ──
        agent_resp = await sales_agent.respond(history)
        if "[LLM ERROR]" in agent_resp:
            logger.warning(f"Sales agent error: {agent_resp[:200]}")
            ended_by = "error"
            break
        conversation.append(Turn(role="agent", content=agent_resp))
        history += f"\n세일즈: {agent_resp}"

        # ── Customer Agent turn ──
        customer_resp = await customer_agent.respond(history)
        if "[LLM ERROR]" in customer_resp:
            logger.warning(f"Customer agent error: {customer_resp[:200]}")
            ended_by = "error"
            break
        conversation.append(Turn(role="persona", content=customer_resp))
        history += f"\n고객: {customer_resp}"

        # ── Exit check ──
        exit_reason = check_exit(customer_resp)
        if exit_reason:
            ended_by = exit_reason
            break

    return ConversationSession(
        session_id=session_id,
        strategy_id=strategy_id,
        persona_id=persona_id,
        turns=conversation,
        ended_by=ended_by,
    )
