import datetime
from typing import Optional


class Storage(object):
    def __init__(self):
        """Stores the infromation for each user"""
        # Load the shelve db if possible
        self.storage = {}

    def add_event(self, chat_id: int, event_name: str, event_time: str) -> Optional[datetime.datetime]:
        """
        Throws ValueError when the format is incorrect
        """
        if chat_id not in self.storage:
            self.storage[chat_id] = {}
        deadline = datetime.datetime.strptime(
            event_time, '%d/%m/%Y %H:%M')
        self.storage[chat_id][event_name] = deadline
        return deadline

    def get_events(self, chat_id: int) -> dict:
        return self.storage[chat_id]

    def delete_event(self, chat_id: int, event_name: str):
        del self.storage[chat_id][event_name]
