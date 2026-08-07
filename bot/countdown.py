import html

from bot.constants import TIMER_FORMAT


def build_countdown_text(event_name: str, unix: int) -> str:
    """HTML for the live countdown message."""
    return TIMER_FORMAT.format(event_name=html.escape(event_name), unix=unix)


def build_event_message(format_str: str, event_name: str) -> str:
    """Format a completion/cancelled message with an HTML-escaped event name."""
    return format_str.format(event_name=html.escape(event_name))
