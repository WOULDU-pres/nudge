"""Sales agent — uses strategy + product brief to persuade customers."""
import logging
from pathlib import Path

from src.agents.base import BaseAgent
from src.llm import call_llm_cheap

logger = logging.getLogger(__name__)


class SalesAgent(BaseAgent):
    """LLM-backed sales agent using AIDA funnel strategy."""

    def __init__(self, strategy: dict, product_brief: str):
        """
        Args:
            strategy: Strategy dict from H stage (matches strategy.schema.json).
            product_brief: Product information text.
        """
        template = self.load_prompt_template("sales-agent-system.md")

        # Build system prompt by substituting strategy fields into template
        system_prompt = self._build_system_prompt(template, strategy, product_brief)
        super().__init__(system_prompt)

        self.strategy = strategy
        self.product_brief = product_brief
        self.strategy_id = strategy.get("strategy_id", "unknown")

    def _build_system_prompt(self, template: str, strategy: dict, product_brief: str) -> str:
        """Substitute strategy fields into the sales agent template."""
        funnel = strategy.get("funnel", {})
        attention = funnel.get("attention", {})
        interest = funnel.get("interest", {})
        desire = funnel.get("desire", {})
        action = funnel.get("action", {})

        replacements = {
            "{hook_type}": attention.get("hook_type", "공감형"),
            "{opening_line_guide}": attention.get("opening_line_guide", "자연스러운 인사로 시작"),
            "{target_emotion}": attention.get("target_emotion", "호기심"),
            "{value_framing}": interest.get("value_framing", "건강 투자 가치"),
            "{information_depth}": interest.get("information_depth", "핵심1개"),
            "{engagement_trigger}": interest.get("engagement_trigger", "질문 유도"),
            "{emotional_driver}": desire.get("emotional_driver", "건강한 생활"),
            "{proof_type}": desire.get("proof_type", "사회적증거"),
            "{objection_preempt}": desire.get("objection_preempt", "반론 인정 후 전환"),
            "{cta_style}": action.get("cta_style", "소프트CTA"),
            "{urgency_type}": action.get("urgency_type", "없음"),
            "{fallback}": action.get("fallback", "무료 샘플 제안"),
            "{product_brief}": product_brief,
            "{tone}": strategy.get("tone", "친절하고 전문적"),
        }

        prompt = template
        for key, value in replacements.items():
            prompt = prompt.replace(key, str(value))

        return prompt

    async def send_opening(self) -> str:
        """Generate opening message (Turn 0: Attention -> Interest)."""
        user_msg = (
            "첫 인사를 시작하세요. 고객에게 처음 말을 거는 상황입니다.\n"
            "퍼널의 Attention 단계에 맞게, 자연스럽고 간결한 오프닝 메시지를 보내세요.\n"
            "1-2문단 이내로."
        )
        response = await call_llm_cheap(
            system_prompt=self.system_prompt,
            user_message=user_msg,
            temperature=0.8,
        )
        self.add_to_history("sales", response)
        return response

    async def respond(self, conversation_history: str) -> str:
        """Generate follow-up response based on conversation history."""
        user_msg = (
            f"대화 기록:\n{conversation_history}\n\n"
            "위 대화에 이어서 응답하세요.\n"
            "퍼널 단계에 맞게 자연스럽게 대화를 이어가세요.\n"
            "1-2문단 이내로 간결하게."
        )
        response = await call_llm_cheap(
            system_prompt=self.system_prompt,
            user_message=user_msg,
            temperature=0.7,
        )
        self.add_to_history("sales", response)
        return response
