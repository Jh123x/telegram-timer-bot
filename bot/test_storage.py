import unittest
from typing import Dict, Tuple
from datetime import datetime

from .storage import Storage


class TestStorage(unittest.TestCase):
    def setUp(self) -> None:
        self.storage = Storage()
        return super().setUp()

    def test_add_get_delete(self) -> None:
        """Test the add, get and delete methods"""
        tests: Dict[str, Tuple[int, str, str, datetime]] = {
            'test1': (1, 'event1', '01/01/2021 00:00', datetime(2021, 1, 1, 0, 0)),
            'test2': (2, 'event2', '02/02/2022 02:02', datetime(2022, 2, 2, 2, 2)),
            'test3': (3, 'event3', '03/03/2033 03:03', datetime(2033, 3, 3, 3, 3)),
        }

        for name, (chat_id, event_name, event_time, event_datetime) in tests.items():
            with self.subTest(name=name):
                assert self.storage.get_events(chat_id, event_name) is None
                assert self.storage.add_event(
                    chat_id, event_name, event_time) == event_datetime
                assert self.storage.get_events(
                    chat_id, event_name) == event_datetime
                assert self.storage.delete_event(chat_id, event_name)
                assert not self.storage.delete_event(chat_id, event_name)
