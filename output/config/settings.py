"""Ralphthon 설정 — Pydantic Settings + python-dotenv."""
from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# .env 위치: 하네스 디렉토리
_HARNESS_DIR = Path(__file__).resolve().parent.parent.parent / "ralphthon-harness"
_ENV_FILE = _HARNESS_DIR / ".env"

# python-dotenv override=True 로 쉘 환경변수보다 .env를 우선
if _ENV_FILE.exists():
    load_dotenv(_ENV_FILE, override=True)


class Settings(BaseSettings):
    # Provider
    RALPHTHON_PROVIDER: str = "gemini"

    # API keys
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Models
    RALPHTHON_MODEL_CHEAP: str = "gemini-3.1-flash-lite-preview"
    RALPHTHON_MODEL_EXPENSIVE: str = "gemini-3.1-flash-lite-preview"

    # Execution
    RALPHTHON_MODE: str = "DEV"  # DEV=10, TEST=50, DEMO=200
    RALPHTHON_MAX_CONCURRENT: int = 1
    RALPHTHON_CONVERSATION_TURNS: int = 3
    RALPHTHON_STRATEGIES_PER_RUN: int = 3

    # Paths (resolved at runtime)
    @property
    def harness_dir(self) -> Path:
        return _HARNESS_DIR

    @property
    def personas_dir(self) -> Path:
        return _HARNESS_DIR / "data" / "personas"

    @property
    def output_dir(self) -> Path:
        return Path(__file__).resolve().parent.parent

    @property
    def persona_count(self) -> int:
        mode_map = {"DEV": 10, "TEST": 50, "DEMO": 200}
        return mode_map.get(self.RALPHTHON_MODE.upper(), 10)

    model_config = {"env_file": "", "extra": "ignore"}


# Singleton
_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
