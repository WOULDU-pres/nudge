"""A (Act) — 대화 배치 실행."""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from src.agents.sales_agent import SalesAgent
from src.agents.customer_agent import CustomerAgent
from src.conversation.engine import run_conversation
from src.conversation.turn import ConversationSession
from config.settings import get_settings

logger = logging.getLogger("ralphthon.ralph.act")


async def act(
    strategies: list[dict],
    personas: list[dict],
    product_brief: str = "",
) -> list[ConversationSession]:
    """전략 × 페르소나 조합으로 대화 시뮬레이션 실행.

    Args:
        strategies: H에서 생성한 전략 목록
        personas: P에서 선택한 페르소나 목록
        product_brief: 제품 정보 텍스트

    Returns:
        ConversationSession 리스트
    """
    settings = get_settings()
    semaphore = asyncio.Semaphore(settings.RALPHTHON_MAX_CONCURRENT)

    async def _run_one(strategy: dict, persona: dict) -> ConversationSession:
        async with semaphore:
            sales = SalesAgent(strategy, product_brief)
            customer = CustomerAgent(persona)
            session = await run_conversation(
                sales_agent=sales,
                customer_agent=customer,
                strategy_id=strategy["strategy_id"],
                persona_id=persona["id"],
            )
            logger.info(
                f"  {strategy['strategy_id']} × {persona['id']} → "
                f"{len(session.turns)} turns, ended_by={session.ended_by}"
            )
            return session

    # Create all tasks
    tasks = []
    for strategy in strategies:
        for persona in personas:
            tasks.append(_run_one(strategy, persona))

    total = len(tasks)
    logger.info(f"Act: running {total} conversations ({len(strategies)} strategies × {len(personas)} personas)")

    results = await asyncio.gather(*tasks, return_exceptions=True)

    sessions = []
    for r in results:
        if isinstance(r, ConversationSession):
            sessions.append(r)
        elif isinstance(r, Exception):
            logger.warning(f"Conversation error: {r}")

    logger.info(f"Act: completed {len(sessions)}/{total} conversations")
    return sessions
