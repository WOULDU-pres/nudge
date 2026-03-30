"""Conversation rules: early exit detection and message constraints."""

# Korean purchase-intent keywords that signal early exit
EARLY_EXIT_KEYWORDS: list[str] = [
    "구매할게요",
    "주문할게요",
    "결제할게요",
    "바로 살게요",
]

MAX_MESSAGE_LENGTH: int = 500


def check_early_exit(message: str) -> bool:
    """Check if the customer message contains any early-exit keyword."""
    return any(keyword in message for keyword in EARLY_EXIT_KEYWORDS)


def truncate_message(message: str) -> str:
    """Truncate message to MAX_MESSAGE_LENGTH characters."""
    if len(message) <= MAX_MESSAGE_LENGTH:
        return message
    return message[:MAX_MESSAGE_LENGTH]
