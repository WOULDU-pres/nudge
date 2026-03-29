"""Base agent class for Ralphthon simulation."""
import re
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Harness prompts directory
PROMPTS_DIR = Path(__file__).parent.parent.parent.parent / "harness" / "prompts"


class BaseAgent:
    """Base class for LLM-backed conversation agents."""

    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.conversation_history: list[dict[str, str]] = []

    async def respond(self, message: str) -> str:
        """Generate a response to the given message. Override in subclasses."""
        raise NotImplementedError

    def add_to_history(self, role: str, content: str):
        """Append a turn to conversation history."""
        self.conversation_history.append({"role": role, "content": content})

    def get_history_text(self) -> str:
        """Format conversation history as a readable transcript."""
        lines = []
        for turn in self.conversation_history:
            prefix = "세일즈" if turn["role"] == "sales" else "고객"
            lines.append(f"{prefix}: {turn['content']}")
        return "\n".join(lines)

    def reset(self):
        """Clear conversation history."""
        self.conversation_history = []

    @staticmethod
    def load_prompt_template(filename: str) -> str:
        """Load a prompt template from the harness prompts directory."""
        path = PROMPTS_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Prompt template not found: {path}")
        return path.read_text(encoding="utf-8")

    @staticmethod
    def strip_soul_for_customer(soul_md: str) -> str:
        """Strip sensitive sections from soul.md for the customer agent.

        Removes:
        - 설득 포인트 section (self-reference prevention)
        - 관심 신호 section (self-reference prevention)
        - 이탈 신호 section (self-reference prevention)
        - Solution hints (→ ...) from 예상 반론 section
        """
        # Remove full sections: 설득 포인트, 관심 신호, 이탈 신호
        # These are ## level headings followed by content until next ## or EOF
        sections_to_remove = ["설득 포인트", "관심 신호", "이탈 신호"]
        for section in sections_to_remove:
            # Match ## <section> through to next ## heading or end of string
            pattern = rf"(^|\n)##\s*{re.escape(section)}.*?(?=\n##\s|\Z)"
            soul_md = re.sub(pattern, "", soul_md, flags=re.DOTALL)

        # In 예상 반론 section: strip solution hints after →
        # Keep the objection part (before →), remove the hint (after →)
        # Lines like: - "질문" → 해결법 설명  =>  - "질문"
        soul_md = re.sub(
            r"(- .+?)→[^\n]*",
            r"\1",
            soul_md,
        )

        # Clean up excessive blank lines
        soul_md = re.sub(r"\n{3,}", "\n\n", soul_md).strip()

        return soul_md
