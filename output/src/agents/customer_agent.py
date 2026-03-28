"""Customer Agent — soul.md 기반 고객 에이전트."""
from __future__ import annotations

from src.llm import call_llm

CUSTOMER_SYSTEM_TEMPLATE = """당신은 아래 인물입니다. 이 사람처럼 자연스럽게 반응하세요.

## 인물 정보
{soul_md}

## 반응 규칙
- 절대 역할에서 벗어나지 마세요.
- 세일즈 에이전트가 제품을 소개하면, 이 인물의 성격/관심사/반감 포인트에 따라 현실적으로 반응하세요.
- 관심이 있으면 질문하세요.
- 관심이 없으면 그렇다고 표현하세요.
- 과장되게 호의적이거나 과장되게 적대적이지 않게, 현실적으로 행동하세요.
- 1-2문단 이내로 자연스럽게 반응하세요.
- 이 인물이 실제로 하지 않을 말은 하지 마세요.
"""


class CustomerAgent:
    def __init__(self, persona: dict):
        self.persona = persona
        self.system_prompt = CUSTOMER_SYSTEM_TEMPLATE.format(
            soul_md=persona.get("soul", "일반적인 소비자입니다.")
        )

    async def respond(self, conversation_history: str) -> str:
        """대화 이력을 받아 고객 반응 생성."""
        return await call_llm(
            system_prompt=self.system_prompt,
            user_message=conversation_history,
            temperature=0.7,
            model_tier="cheap",
        )
