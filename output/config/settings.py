"""Central settings for the merged Ralphthon output pipeline.

This project now supports two backend styles:
1. acpx/Codex subprocess backend (default, restored from prior v2 work)
2. Direct API backend (gemini/openai/anthropic/ollama) as fallback
"""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Backend selection
    LLM_BACKEND: str = "acpx"  # acpx | api

    # Provider & model selection (API fallback mode)
    RALPHTHON_PROVIDER: str = "gemini"
    RALPHTHON_MODEL: str = "gemini-2.0-flash-lite"
    RALPHTHON_MODEL_CHEAP: str = ""
    RALPHTHON_MODEL_EXPENSIVE: str = ""

    # acpx / Codex subprocess mode
    ACPX_AGENT: str = "codex"
    ACPX_MODEL: str = ""
    ACPX_TIMEOUT: int = 300
    ACPX_APPROVE_ALL: bool = True
    ACPX_ALLOWED_TOOLS: str = ""

    # Run mode
    RALPHTHON_MODE: str = "DEV"

    # Concurrency & rate limiting
    MAX_CONCURRENT: int = 8
    MAX_RETRIES: int = 5
    RATE_LIMIT_DELAY: float = 0.05

    # Pipeline parameters
    STRATEGIES_PER_RUN: int = 3
    MAX_TURNS: int = 3
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
        return max(1, min(20, self.MAX_CONCURRENT))

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
    def persona_count(self) -> int:
        mode_map = {"DEV": 10, "TEST": 50, "DEMO": 200}
        return mode_map.get(self.RALPHTHON_MODE.upper(), 10)

    @property
    def api_keys(self) -> list[str]:
        keys = [self.GEMINI_API_KEY]
        if self.GEMINI_API_KEY_2:
            keys.append(self.GEMINI_API_KEY_2)
        return [k for k in keys if k]

    @property
    def provider(self) -> str:
        return "acpx" if self.LLM_BACKEND.lower() == "acpx" else self.RALPHTHON_PROVIDER

    @property
    def cheap_model(self) -> str:
        if self.LLM_BACKEND.lower() == "acpx":
            return self.ACPX_MODEL or "acpx"
        return self.RALPHTHON_MODEL_CHEAP or self.RALPHTHON_MODEL

    @property
    def expensive_model(self) -> str:
        if self.LLM_BACKEND.lower() == "acpx":
            return self.ACPX_MODEL or "acpx"
        return self.RALPHTHON_MODEL_EXPENSIVE or self.RALPHTHON_MODEL

    @property
    def acpx_model(self) -> str:
        return self.ACPX_MODEL or ""

    # compatibility aliases used by older modules
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


settings = Settings()
