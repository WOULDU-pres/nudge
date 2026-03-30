"""Ralphthon project settings using Pydantic BaseSettings.

The merged repository keeps the ralphton output codebase while using the
root-level plz harness layout (`../harness/...`). This settings module exposes
both the newer uppercase names used by the ralphton output code and the older
lowercase aliases used by some retained compatibility modules.
"""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration for the Ralphthon output pipeline."""

    # Provider & model selection
    RALPHTHON_PROVIDER: str = "gemini"  # gemini / openai / anthropic / ollama
    RALPHTHON_MODEL: str = "gemini-2.0-flash-lite"
    RALPHTHON_MODEL_CHEAP: str = ""  # if empty, falls back to RALPHTHON_MODEL
    RALPHTHON_MODEL_EXPENSIVE: str = ""  # if empty, falls back to RALPHTHON_MODEL

    # Run mode
    RALPHTHON_MODE: str = "DEMO"  # DEV=10, TEST=50, DEMO=200 personas

    # Concurrency & rate limiting
    MAX_CONCURRENT: int = 20
    MAX_RETRIES: int = 10
    RATE_LIMIT_DELAY: float = 0.05

    # Pipeline parameters
    STRATEGIES_PER_RUN: int = 3
    MAX_TURNS: int = 3  # conversation round-trips
    RALPH_ITERATIONS: int = 1

    # API keys
    GEMINI_API_KEY: str = ""
    GEMINI_API_KEY_2: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Paths relative to output/
    PERSONAS_DIR: str = "../harness/data/personas"
    PROMPTS_DIR: str = "../harness/prompts"

    # Judge
    JUDGE_TEMPERATURE: float = 0.1

    model_config = {
        "env_prefix": "",
        "env_file": ".env",
        "extra": "ignore",
    }

    @property
    def concurrent(self) -> int:
        """Return MAX_CONCURRENT clamped to [10, 20]."""
        return max(10, min(20, self.MAX_CONCURRENT))

    @property
    def cheap_model(self) -> str:
        """Return the cheap model, falling back to the default model."""
        return self.RALPHTHON_MODEL_CHEAP or self.RALPHTHON_MODEL

    @property
    def expensive_model(self) -> str:
        """Return the expensive model, falling back to the default model."""
        return self.RALPHTHON_MODEL_EXPENSIVE or self.RALPHTHON_MODEL

    @property
    def persona_count(self) -> int:
        """Return persona count based on mode: DEV=10, TEST=50, DEMO=200."""
        mode_map = {"DEV": 10, "TEST": 50, "DEMO": 200}
        return mode_map.get(self.RALPHTHON_MODE.upper(), 200)

    @property
    def output_dir(self) -> Path:
        return Path(__file__).resolve().parent.parent

    @property
    def harness_dir(self) -> Path:
        return (self.output_dir.parent / "harness").resolve()

    @property
    def personas_dir(self) -> Path:
        return (self.output_dir / self.PERSONAS_DIR).resolve()

    @property
    def prompts_dir(self) -> Path:
        return (self.output_dir / self.PROMPTS_DIR).resolve()

    @property
    def api_keys(self) -> list[str]:
        """Return available Gemini API keys for round-robin usage."""
        keys = [self.GEMINI_API_KEY]
        if self.GEMINI_API_KEY_2:
            keys.append(self.GEMINI_API_KEY_2)
        return [k for k in keys if k]

    # Compatibility aliases for retained v2 modules / dry-run helpers
    @property
    def provider(self) -> str:
        return self.RALPHTHON_PROVIDER

    @property
    def model_cheap(self) -> str:
        return self.cheap_model

    @property
    def model_expensive(self) -> str:
        return self.expensive_model

    @property
    def mode(self) -> str:
        return self.RALPHTHON_MODE

    @property
    def max_concurrent(self) -> int:
        return self.MAX_CONCURRENT

    @property
    def rate_limit_delay(self) -> float:
        return self.RATE_LIMIT_DELAY

    @property
    def strategies_per_run(self) -> int:
        return self.STRATEGIES_PER_RUN

    @property
    def conversation_turns(self) -> int:
        return self.MAX_TURNS

    @property
    def ralph_iterations(self) -> int:
        return self.RALPH_ITERATIONS


# Singleton instance
settings = Settings()
