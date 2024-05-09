import datetime
from typing import Optional, Dict


class Storage:
    def __init__(self: 'Storage') -> None:
        """Stores the information for each user"""
        # Load the shelve db if possible
        self.storage: Dict[int, Dict[str, datetime.datetime]] = {}

    def add_event(self: 'Storage', chat_id: int, event_name: str, event_time: str) -> datetime.datetime:
        """
        Throws ValueError when the format is incorrect
        """
        if chat_id not in self.storage:
            self.storage[chat_id] = {}

        deadline = datetime.datetime.strptime(
            event_time,
            '%d/%m/%Y %H:%M',
        )
        self.storage[chat_id][event_name] = deadline

        return deadline

    def get_events(self: 'Storage', chat_id: int, event_name: str) -> Optional[datetime.datetime]:
        """Returns the event time if it exists, None otherwise"""
        return self.storage.get(chat_id, {}).get(event_name, None)

    def delete_event(self: 'Storage', chat_id: int, event_name: str) -> bool:
        """Deletes the event if it exists, returns True if it was deleted, False if it does not exist"""
        try:
            del self.storage[chat_id][event_name]
            return True
        except KeyError:
            return False
