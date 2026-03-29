"""Pydantic Settings for Ralphthon harness."""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Environment-variable based settings."""

    # Provider
    provider: str = Field(default="gemini", alias="RALPHTHON_PROVIDER")

    # API Keys (dual key support for higher RPM)
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_api_key_2: str = Field(default="", alias="GEMINI_API_KEY_2")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")

    # Models — google-genai SDK model names
    model_cheap: str = Field(default="gemini-2.5-flash-preview-05-20", alias="RALPHTHON_MODEL_CHEAP")
    model_expensive: str = Field(default="gemini-2.5-flash-preview-05-20", alias="RALPHTHON_MODEL_EXPENSIVE")

    # Execution mode: DEV=10, TEST=50, DEMO=200
    mode: str = Field(default="TEST", alias="RALPHTHON_MODE")

    # Concurrency
    max_concurrent: int = Field(default=20, alias="RALPHTHON_MAX_CONCURRENT")
    rate_limit_delay: float = Field(default=0.05, alias="RATE_LIMIT_DELAY")

    # RALPH parameters
    strategies_per_run: int = Field(default=3, alias="STRATEGIES_PER_RUN")
    conversation_turns: int = Field(default=3, alias="CONVERSATION_TURNS")
    ralph_iterations: int = Field(default=1, alias="RALPH_ITERATIONS")

    # Paths (computed at init)
    harness_dir: Optional[Path] = Field(default=None)
    output_dir: Optional[Path] = Field(default=None)
    personas_dir: Optional[Path] = Field(default=None)

    # Retry
    max_retries: int = 5
    retry_base_delay: float = 2.0

    class Config:
        env_file = ".env"
        extra = "ignore"
        populate_by_name = True

    def model_post_init(self, __context):
        config_dir = Path(__file__).parent
        if self.output_dir is None:
            object.__setattr__(self, "output_dir", config_dir.parent)
        if self.harness_dir is None:
            object.__setattr__(self, "harness_dir", config_dir.parent.parent / "harness")
        if self.personas_dir is None:
            object.__setattr__(self, "personas_dir", self.harness_dir / "data" / "personas")

    @property
    def persona_count(self) -> int:
        mode_map = {"DEV": 10, "TEST": 50, "DEMO": 200}
        return mode_map.get(self.mode.upper(), 50)

    @property
    def api_keys(self) -> list[str]:
        """Return list of available API keys for round-robin."""
        keys = [self.gemini_api_key]
        if self.gemini_api_key_2:
            keys.append(self.gemini_api_key_2)
        return [k for k in keys if k]


settings = Settings()
