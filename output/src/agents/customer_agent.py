"""Customer agent — simulates a persona's realistic responses."""
import logging

from src.agents.base import BaseAgent
from src.personas.schema import Persona
from src.llm import call_llm_cheap

logger = logging.getLogger(__name__)


class CustomerAgent(BaseAgent):
    """LLM-backed customer agent driven by persona soul.md."""

    def __init__(self, persona: Persona):
        """
        Args:
            persona: Persona with profile + soul.md.
        """
        template = self.load_prompt_template("customer-agent-system.md")

        # Strip sensitive sections from soul for the customer agent
        filtered_soul = self.strip_soul_for_customer(persona.soul_md)

        system_prompt = template.replace("{soul_md}", filtered_soul)
        super().__init__(system_prompt)

        self.persona = persona
        self.persona_id = persona.persona_id

    async def respond(self, conversation_history: str) -> str:
        """Generate customer response to the sales conversation."""
        user_msg = (
            f"대화 기록:\n{conversation_history}\n\n"
            "위 대화에서 세일즈맨의 마지막 발언에 자연스럽게 반응하세요.\n"
            "당신의 성격과 상황에 맞게 현실적으로 응답하세요.\n"
            "1-2문단 이내로."
        )
        response = await call_llm_cheap(
            system_prompt=self.system_prompt,
            user_message=user_msg,
            temperature=0.8,
        )
        self.add_to_history("customer", response)
        return response
