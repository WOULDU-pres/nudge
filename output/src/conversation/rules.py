"""End condition detection for conversations."""
import re

# Keywords that signal customer wants to end the conversation
EXIT_KEYWORDS = [
    "no thanks",
    "not interested",
    "stop contacting",
    "leave me alone",
    "goodbye",
    "bye",
    "i'm done",
    "im done",
    "don't contact me",
    "dont contact me",
    "end conversation",
    "no thank you",
    "i'll pass",
    "ill pass",
    "please stop",
    "unsubscribe",
    "remove me",
]

# Compiled pattern for efficient matching
_EXIT_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(kw) for kw in EXIT_KEYWORDS) + r")\b",
    re.IGNORECASE,
)


def check_exit_keyword(text: str) -> bool:
    """Check if customer response contains an exit keyword.

    Args:
        text: Customer's response text.

    Returns:
        True if an exit keyword was detected.
    """
    return bool(_EXIT_PATTERN.search(text))


def should_end_conversation(
    current_turn: int,
    max_turns: int,
    last_customer_message: str | None = None,
) -> tuple[bool, str | None]:
    """Determine if the conversation should end.

    Args:
        current_turn: Current turn index (0-based).
        max_turns: Maximum number of turns allowed.
        last_customer_message: Most recent customer message (if any).

    Returns:
        Tuple of (should_end, reason). Reason is None if should not end.
    """
    # Check turn limit
    if current_turn >= max_turns:
        return True, "turn_limit"

    # Check exit keywords in customer message
    if last_customer_message and check_exit_keyword(last_customer_message):
        return True, "keyword_detected"

    return False, None
