"""P (Plan) — 페르소나 선택. LLM 불필요, 순수 코드."""
from __future__ import annotations

from src.personas.loader import load_personas


def plan(count: int | None = None) -> list[dict]:
    """이번 실행 대상 페르소나 선택.

    Args:
        count: 로드할 수. None이면 settings 기반 (DEV=10, TEST=50, DEMO=200).

    Returns:
        Persona dict 리스트 (ID 순).
    """
    return load_personas(count)
