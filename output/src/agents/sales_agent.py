"""Sales Agent — reads sales-agent-system.md template and generates sales messages."""

from __future__ import annotations

from pathlib import Path

from config.settings import Settings
from src.llm import call_llm

settings = Settings()


class SalesAgent:
    """LLM-powered sales agent that follows an AIDA funnel strategy."""

    def __init__(self, strategy: dict, product: dict) -> None:
        self.strategy = strategy
        self.product = product
        self._system_prompt: str | None = None

    def _build_product_brief(self) -> str:
        """Build a product brief string from the product dict."""
        name = self.product.get("name", "")
        price = self.product.get("price", "")
        benefits = self.product.get("key_benefits", self.product.get("benefits", []))
        if isinstance(benefits, list):
            benefits_str = ", ".join(benefits)
        else:
            benefits_str = str(benefits)
        return f"제품명: {name}\n가격: {price}\n주요 효능: {benefits_str}"

    def _build_system_prompt(self) -> str:
        """Load the template and fill placeholders from strategy and product."""
        if self._system_prompt is not None:
            return self._system_prompt

        template_path = Path(settings.PROMPTS_DIR) / "sales-agent-system.md"
        template = template_path.read_text(encoding="utf-8")

        funnel = self.strategy.get("funnel", {})
        attention = funnel.get("attention", {})
        interest = funnel.get("interest", {})
        desire = funnel.get("desire", {})
        action = funnel.get("action", {})

        # Use .replace() one-by-one to avoid issues with other curly braces in template
        replacements = {
            # Attention
            "{hook_type}": str(attention.get("hook_type", "")),
            "{opening_line_guide}": str(attention.get("opening_line_guide", "")),
            "{target_emotion}": str(attention.get("target_emotion", "")),
            # Interest
            "{value_framing}": str(interest.get("value_framing", "")),
            "{information_depth}": str(interest.get("information_depth", "")),
            "{engagement_trigger}": str(interest.get("engagement_trigger", "")),
            # Desire
            "{emotional_driver}": str(desire.get("emotional_driver", "")),
            "{proof_type}": str(desire.get("proof_type", "")),
            "{objection_preempt}": str(desire.get("objection_preempt", "")),
            # Action
            "{cta_style}": str(action.get("cta_style", "")),
            "{urgency_type}": str(action.get("urgency_type", "")),
            "{fallback}": str(action.get("fallback", "")),
            # Product & Tone
            "{product_brief}": self._build_product_brief(),
            "{tone}": str(self.strategy.get("tone", "")),
        }

        prompt = template
        for placeholder, value in replacements.items():
            prompt = prompt.replace(placeholder, value)

        self._system_prompt = prompt
        return self._system_prompt

    async def generate_message(
        self, conversation_history: list[dict], turn: int
    ) -> str:
        """Generate the next sales message given conversation history and turn number.

        Args:
            conversation_history: List of {role, content} dicts so far.
            turn: Current turn number (0-indexed).

        Returns:
            The sales agent's message string.
        """
        system_prompt = self._build_system_prompt()

        # Build user prompt from conversation history
        if not conversation_history:
            user_prompt = f"턴 {turn}/3. 고객에게 첫 메시지를 보내세요."
        else:
            lines = []
            for entry in conversation_history:
                role = entry.get("role", "")
                label = "세일즈" if role == "agent" else "고객"
                lines.append(f"[{label}]: {entry['content']}")
            lines.append(f"\n턴 {turn}/3. 위 대화 이어서 고객에게 다음 메시지를 보내세요.")
            user_prompt = "\n".join(lines)

        response = await call_llm(
            prompt=user_prompt,
            system=system_prompt,
            model=settings.cheap_model,
        )
        return response.strip()
