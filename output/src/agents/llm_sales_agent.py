"""Compact Codex/acpx-backed sales agent for v2 conversation simulation."""

from __future__ import annotations

from src.llm import call_llm


class LLMSalesAgent:
    def __init__(self, strategy: dict, product: dict):
        self.strategy = strategy
        self.product = product
        self._system_prompt: str | None = None

    def _build_product_brief(self) -> str:
        benefits = ', '.join(self.product.get('key_benefits', [])[:4])
        return (
            f"제품명={self.product.get('name', '')}, 가격={self.product.get('price', '')}, "
            f"타겟={self.product.get('target', '')}, 혜택={benefits}"
        )

    def _build_system_prompt(self) -> str:
        if self._system_prompt is not None:
            return self._system_prompt

        funnel = self.strategy.get('funnel', {})
        attention = funnel.get('attention', {})
        interest = funnel.get('interest', {})
        desire = funnel.get('desire', {})
        action = funnel.get('action', {})

        self._system_prompt = (
            '당신은 한국어 세일즈 상담원이다. 짧고 자연스럽고 부담 없게 말하라. '
            '과장, 장문 설명, 반복, 과도한 광고 톤은 금지. 각 응답은 2~4문장 이내.\n\n'
            f"strategy_id: {self.strategy.get('strategy_id', '')}\n"
            f"hypothesis: {self.strategy.get('hypothesis', '')}\n"
            f"tone: {self.strategy.get('tone', '')}\n"
            f"hook_type: {attention.get('hook_type', '')}\n"
            f"value_framing: {interest.get('value_framing', '')}\n"
            f"proof_type: {desire.get('proof_type', '')}\n"
            f"cta_style: {action.get('cta_style', '')}\n"
            f"product: {self._build_product_brief()}\n"
            '규칙: 고객의 마지막 말에 직접 대응하고, 숫자/비교 요청에는 짧고 구체적으로 답하라. '
            '고객 반론은 인정하고 전환하라. 즉시 구매 강요 금지.'
        )
        return self._system_prompt

    async def send_opening(self) -> str:
        return await self.respond([])

    async def respond(self, conversation_history: list[dict]) -> str:
        system_prompt = self._build_system_prompt()
        if not conversation_history:
            user_prompt = '첫 오프닝 메시지를 작성하세요. 고객의 일상과 연결된 한 가지 장면으로 시작하세요.'
        else:
            history = '\n'.join(
                f"{'세일즈' if t['role']=='agent' else '고객'}: {t['content']}" for t in conversation_history[-6:]
            )
            user_prompt = (
                f"다음 대화를 이어서 세일즈 메시지를 작성하세요.\n\n{history}\n\n"
                '고객의 마지막 말에 바로 대응하고, 2~4문장으로 짧게 답하세요.'
            )
        return (await call_llm(prompt=user_prompt, system=system_prompt, model='gpt-5.4-mini')).strip()
