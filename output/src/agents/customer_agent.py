"""Customer Agent — reads customer-agent-system.md template and simulates customer responses."""

from __future__ import annotations

from pathlib import Path

from config.settings import Settings
from src.llm import call_llm
from src.personas.loader import Persona

settings = Settings()


class CustomerAgent:
    """LLM-powered customer agent that role-plays as a specific persona."""

    def __init__(self, persona: Persona) -> None:
        self.persona = persona
        self._system_prompt: str | None = None

    def _build_system_prompt(self) -> str:
        """Load the template and fill {soul_md} with the persona's soul markdown."""
        if self._system_prompt is not None:
            return self._system_prompt

        template_path = Path(settings.PROMPTS_DIR) / "customer-agent-system.md"
        template = template_path.read_text(encoding="utf-8")

        # Use .replace() to safely substitute only the known placeholder
        prompt = template.replace("{soul_md}", self.persona.soul_md)

        self._system_prompt = prompt
        return self._system_prompt

    async def generate_response(
        self, conversation_history: list[dict], turn: int
    ) -> str:
        """Generate the customer's response given conversation history and turn number.

        Args:
            conversation_history: List of {role, content} dicts so far.
            turn: Current turn number (0-indexed).

        Returns:
            The customer persona's response string.
        """
        system_prompt = self._build_system_prompt()

        # Build user prompt from conversation history
        lines = []
        for entry in conversation_history:
            role = entry.get("role", "")
            label = "세일즈" if role == "agent" else "나"
            lines.append(f"[{label}]: {entry['content']}")
        lines.append(f"\n턴 {turn}/3. 세일즈 상담원의 마지막 메시지에 대해 고객으로서 응답하세요.")
        user_prompt = "\n".join(lines)

        response = await call_llm(
            prompt=user_prompt,
            system=system_prompt,
            model=settings.cheap_model,
        )
        return response.strip()
