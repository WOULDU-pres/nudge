"""Codex/acpx-backed customer agent for v2 conversation simulation."""

from __future__ import annotations

from pathlib import Path

from config.settings import settings
from src.llm import call_llm
from src.personas.loader import Persona


class LLMCustomerAgent:
    def __init__(self, persona: Persona):
        self.persona = persona
        self._system_prompt: str | None = None

    def _build_system_prompt(self) -> str:
        if self._system_prompt is not None:
            return self._system_prompt
        template_path = Path(settings.prompts_dir) / 'customer-agent-system.md'
        template = template_path.read_text(encoding='utf-8')
        prompt = template.replace('{soul_md}', self.persona.soul_md)
        self._system_prompt = prompt
        return prompt

    async def respond(self, conversation_history: list[dict]) -> str:
        system_prompt = self._build_system_prompt()
        history = '\n'.join(
            f"{'세일즈' if t['role']=='agent' else '고객'}: {t['content']}" for t in conversation_history
        )
        user_prompt = (
            f"아래 대화에서 고객 역할로만 반응하세요.\n\n{history}\n\n"
            '고객의 성격과 예산/관심사에 맞게 1~3문장으로 현실적으로 응답하세요.'
        )
        return (await call_llm(prompt=user_prompt, system=system_prompt, model=settings.cheap_model)).strip()
