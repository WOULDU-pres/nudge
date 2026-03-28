"""대화 종료 조건 판정."""
from __future__ import annotations

EXIT_KEYWORDS = ["대화를 끝내", "다시 연락하지", "관심 없", "끊을게"]


def check_exit(content: str) -> str | None:
    """고객 발화에 종료 키워드가 있으면 'keyword_detected' 반환."""
    lower = content.lower()
    for kw in EXIT_KEYWORDS:
        if kw in lower:
            return "keyword_detected"
    return None
