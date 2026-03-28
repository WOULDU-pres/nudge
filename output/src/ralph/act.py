"""A (Act) — 대화 배치 실행."""
from __future__ import annotations

import asyncio
import logging
import yaml
from pathlib import Path

from src.agents.sales_agent import SalesAgent
from src.agents.customer_agent import CustomerAgent
from src.conversation.engine import run_conversation
from src.conversation.turn import ConversationSession
from config.settings import get_settings

logger = logging.getLogger("ralphthon.ralph.act")


def _load_product_brief() -> str:
    """product.yaml에서 product_brief 로드."""
    product_path = Path(__file__).resolve().parent.parent.parent / "config" / "product.yaml"
    if product_path.exists():
        with open(product_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("product_brief", "바이탈케어 데일리 멀티비타민")
    return "바이탈케어 데일리 멀티비타민 — 하루 500원, 60정 2개월분"


async def act(
    strategies: list[dict],
    personas: list[dict],
) -> list[ConversationSession]:
    """전략 × 페르소나 조합으로 대화 시뮬레이션 실행.

    Returns:
        ConversationSession 리스트
    """
    settings = get_settings()
    semaphore = asyncio.Semaphore(settings.RALPHTHON_MAX_CONCURRENT)
    product_brief = _load_product_brief()

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
