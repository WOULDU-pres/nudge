"""Sales Agent — 전략 기반 세일즈 에이전트."""
from __future__ import annotations

from src.llm import call_llm

SALES_SYSTEM_TEMPLATE = """당신은 숙련된 세일즈 전문가입니다.
아래 전략에 따라 고객과 대화하세요.

## 전략
- 접근법: {approach}
- 오프닝: {opening_style}
- 반론 대응: {objection_handling}
- 톤: {tone}

## 제품 정보
{product_brief}

## 규칙
- 자연스러운 한국어로 대화하세요.
- 고객의 반응에 맞게 유연하게 대응하세요.
- 억지로 밀어붙이지 마세요. 관심이 없으면 가볍게 마무리하세요.
- 1-2문단 이내로 간결하게 말하세요.
- 고객이 질문하면 구체적으로 답하세요.
- 가격을 물어보면 솔직하게 답하세요.

## 첫 턴
제품 정보를 바탕으로 첫 인사와 함께 자연스럽게 대화를 시작하세요.
opening_style에 따른 방식으로 시작하세요.
"""


class SalesAgent:
    def __init__(self, strategy: dict, product_brief: str):
        self.strategy = strategy
        self.system_prompt = SALES_SYSTEM_TEMPLATE.format(
            approach=strategy.get("approach", ""),
            opening_style=strategy.get("opening_style", ""),
            objection_handling=strategy.get("objection_handling", ""),
            tone=strategy.get("tone", ""),
            product_brief=product_brief,
        )

    async def respond(self, conversation_history: str) -> str:
        """대화 이력을 받아 응답 생성."""
        user_msg = conversation_history if conversation_history else "대화를 시작하세요."
        return await call_llm(
            system_prompt=self.system_prompt,
            user_message=user_msg,
            temperature=0.7,
            model_tier="cheap",
        )
