"""Compact Codex/acpx-backed customer agent for v2 conversation simulation."""

from __future__ import annotations

from src.llm import call_llm
from src.personas.loader import Persona


class LLMCustomerAgent:
    def __init__(self, persona: Persona):
        self.persona = persona
        self._system_prompt: str | None = None

    def _build_system_prompt(self) -> str:
        if self._system_prompt is not None:
            return self._system_prompt

        profile = getattr(self.persona, 'profile', {}) or {}
        purchase_context = getattr(self.persona, 'purchase_context', {}) or {}
        objection_profile = getattr(self.persona, 'objection_profile', {}) or {}
        decision_style = getattr(self.persona, 'decision_style', {}) or {}

        self._system_prompt = (
            '당신은 아래 페르소나 그 자체처럼 반응하는 고객이다. '\
            '항상 한국어로, 현실적이고 방어적으로 반응하라. 즉석 구매는 거의 하지 말고, '\
            '관심이 생겨도 질문/보류 수준에서 멈춰라. 1~3문장으로 짧게 답하라.\n\n'
            f"persona_id: {self.persona.persona_id}\n"
            f"summary: {getattr(self.persona, 'summary', '')}\n"
            f"cluster_tags: {', '.join(getattr(self.persona, 'cluster_tags', []))}\n"
            f"life_context: {profile.get('life_context', '')}\n"
            f"budget_sensitivity: {purchase_context.get('budget_sensitivity', '')}\n"
            f"decision_speed: {decision_style.get('decision_speed', '')}\n"
            f"trust_style: {', '.join(decision_style.get('trust_style', []))}\n"
            f"primary_objection: {objection_profile.get('primary_type', '')}\n"
            '규칙: 세일즈 문구를 경계하라. 숫자/비교를 선호하되, 설득이 부족하면 짧게 거절하거나 보류하라.'
        )
        return self._system_prompt

    async def respond(self, conversation_history: list[dict]) -> str:
        system_prompt = self._build_system_prompt()
        history = '\n'.join(
            f"{'세일즈' if t['role']=='agent' else '고객'}: {t['content']}" for t in conversation_history[-6:]
        )
        user_prompt = (
            f"아래 대화를 이어서 고객 입장에서만 반응하세요.\n\n{history}\n\n"
            '고객의 성격과 생활 맥락에 맞게 현실적으로 1~3문장으로 응답하세요.'
        )
        return (await call_llm(prompt=user_prompt, system=system_prompt, model='gpt-5.4-mini')).strip()
