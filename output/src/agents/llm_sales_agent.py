"""Codex/acpx-backed sales agent for v2 conversation simulation."""

from __future__ import annotations

from pathlib import Path

from config.settings import settings
from src.llm import call_llm


class LLMSalesAgent:
    def __init__(self, strategy: dict, product: dict):
        self.strategy = strategy
        self.product = product
        self._system_prompt: str | None = None

    def _build_product_brief(self) -> str:
        lines = [
            f"제품명: {self.product.get('name', '')}",
            f"가격: {self.product.get('price', '')}",
            f"타겟: {self.product.get('target', '')}",
            f"사용맥락: {self.product.get('use_case', '')}",
        ]
        benefits = self.product.get('key_benefits', [])
        if benefits:
            lines.append('핵심 효능:')
            lines.extend(f'- {b}' for b in benefits)
        return '\n'.join(lines)

    def _build_system_prompt(self) -> str:
        if self._system_prompt is not None:
            return self._system_prompt
        template_path = Path(settings.prompts_dir) / 'sales-agent-system.md'
        template = template_path.read_text(encoding='utf-8')
        funnel = self.strategy.get('funnel', {})
        attention = funnel.get('attention', {})
        interest = funnel.get('interest', {})
        desire = funnel.get('desire', {})
        action = funnel.get('action', {})
        replacements = {
            '{hook_type}': str(attention.get('hook_type', '공감형')),
            '{opening_line_guide}': str(attention.get('opening_line_guide', '짧고 직설적으로 시작')),
            '{target_emotion}': str(attention.get('target_emotion', '호기심')),
            '{value_framing}': str(interest.get('value_framing', '실생활 가치 중심')),
            '{information_depth}': str(interest.get('information_depth', '핵심 위주')),
            '{engagement_trigger}': str(interest.get('engagement_trigger', '짧은 질문 유도')),
            '{emotional_driver}': str(desire.get('emotional_driver', '일상 효율')),
            '{proof_type}': str(desire.get('proof_type', '구체적 수치')),
            '{objection_preempt}': str(desire.get('objection_preempt', '예산/효과성 반론 선제 대응')),
            '{cta_style}': str(action.get('cta_style', '부담 없는 다음 행동 제안')),
            '{urgency_type}': str(action.get('urgency_type', '없음')),
            '{fallback}': str(action.get('fallback', '추가 정보 제공')),
            '{product_brief}': self._build_product_brief(),
            '{tone}': str(self.strategy.get('tone', '친절하고 간결함')),
        }
        prompt = template
        for key, value in replacements.items():
            prompt = prompt.replace(key, value)
        self._system_prompt = prompt
        return prompt

    async def send_opening(self) -> str:
        return await self.respond([])

    async def respond(self, conversation_history: list[dict]) -> str:
        system_prompt = self._build_system_prompt()
        if not conversation_history:
            user_prompt = '첫 메시지를 2~4문장 이내로 시작하세요. 과장하지 말고 자연스럽게 시작하세요.'
        else:
            history = '\n'.join(
                f"{'세일즈' if t['role']=='agent' else '고객'}: {t['content']}" for t in conversation_history
            )
            user_prompt = (
                f"다음 대화 기록을 보고 세일즈 상담원의 다음 메시지를 작성하세요.\n\n{history}\n\n"
                '반드시 2~4문장 이내, 너무 길지 않게, 고객의 마지막 반응에 직접 대응하세요.'
            )
        return (await call_llm(prompt=user_prompt, system=system_prompt, model=settings.cheap_model)).strip()
