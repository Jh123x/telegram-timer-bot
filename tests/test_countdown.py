import unittest

from bot.constants import EVENT_CANCELLED_FORMAT, EVENT_ENDED_FORMAT
from bot.countdown import build_countdown_text, build_event_message


class TestCountdown(unittest.TestCase):
    def test_build_countdown_text(self) -> None:
        self.assertEqual(
            build_countdown_text("New Year party", 1798761599),
            '<b>New Year party</b>\n⏳ <tg-time unix="1798761599" format="r">0</tg-time>',
        )

    def test_build_countdown_text_escapes_event_name(self) -> None:
        self.assertEqual(
            build_countdown_text("A <B> & C", 1),
            '<b>A &lt;B&gt; &amp; C</b>\n⏳ <tg-time unix="1" format="r">0</tg-time>',
        )

    def test_build_countdown_text_escapes_quotes_and_zero_unix(self) -> None:
        self.assertEqual(
            build_countdown_text('A "Q" <B>', 0),
            '<b>A &quot;Q&quot; &lt;B&gt;</b>\n⏳ <tg-time unix="0" format="r">0</tg-time>',
        )

    def test_build_event_message_escapes_event_name(self) -> None:
        self.assertEqual(
            build_event_message(EVENT_ENDED_FORMAT, "A <B> & C"),
            "A &lt;B&gt; &amp; C has already ended :(",
        )
        self.assertEqual(
            build_event_message(EVENT_CANCELLED_FORMAT, "Party"),
            "Party is cancelled :(",
        )
