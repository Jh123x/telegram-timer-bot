from datetime import datetime
import json
import os
from typing import Optional
from logging import Logger

class Storage:
    def __init__(self, logger : Logger) -> None:
        """Stores the information for each user"""
        # Load the shelve db if possible
        if os.path.isfile(f"./database/storage.json"):
            logger.info("Loading stored events...")
            with open("./database/storage.json", "r") as storageFile:
                try:
                    self.storage = json.load(storageFile)
                except Exception as e:
                    logger.error("Error loading stored events", {str(e)})
                    self.storage = {}
        else:
            logger.info("No saved events found.")
            self.storage = {}
            os.makedirs("./database", exist_ok=True)
            with open("./database/storage.json", "w") as storageFile:
                json.dump(self.storage, storageFile, indent=4)
            

    def add_event(self, chat_id: int, event_name: str, event_time: str) -> datetime:
        """
        Throws ValueError when the format is incorrect
        """
        chat_id = str(chat_id)
        if chat_id not in self.storage:
            self.storage[chat_id] = {}
        deadline = datetime.strptime(
            event_time, '%d/%m/%Y %H:%M')
        self.storage[chat_id][event_name] = event_time
        with open("./database/storage.json", "w") as storageFile:
                json.dump(self.storage, storageFile, indent=4)
        return deadline

    def get_events(self, chat_id: int, event_name) -> Optional[datetime]:
        chat_id = str(chat_id)
        event_time = self.storage.get(chat_id, {}).get(event_name, None)
        if event_time is None: return None
        return datetime.strptime(event_time, '%d/%m/%Y %H:%M')

    def delete_event(self, chat_id: int, event_name: str) -> bool:
        chat_id = str(chat_id)
        try:
            del self.storage[chat_id][event_name]
            with open("./database/storage.json", "w") as storageFile:
                json.dump(self.storage, storageFile, indent=4)
            return True
        except:
            return False
