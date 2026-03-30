"""Async v2 conversation engine using LLMSalesAgent and LLMCustomerAgent."""

from __future__ import annotations

import time

from src.conversation.rules import check_early_exit, truncate_message


async def run_conversation_v2(
    sales_agent,
    customer_agent,
    strategy_id: str,
    persona_id: str,
    max_turns: int = 4,
) -> dict:
    turns: list[dict] = []
    ended_by = 'turn_limit'
    started_at = time.time()

    for turn_idx in range(max_turns):
        sales_message = await (sales_agent.send_opening() if turn_idx == 0 else sales_agent.respond(turns))
        sales_message = truncate_message(sales_message)
        turns.append({'role': 'agent', 'content': sales_message})

        customer_message = await customer_agent.respond(turns)
        customer_message = truncate_message(customer_message)
        turns.append({'role': 'persona', 'content': customer_message})

        if check_early_exit(customer_message):
            ended_by = 'keyword_detected'
            break

    return {
        'session_id': f'conv-v2-{strategy_id}-{persona_id}',
        'strategy_id': strategy_id,
        'persona_id': persona_id,
        'turns': turns,
        'ended_by': ended_by,
        'latency_sec': round(time.time() - started_at, 2),
    }
