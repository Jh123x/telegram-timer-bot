import asyncio
import datetime
import logging
import os

import httpx
from dotenv import load_dotenv
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import CallbackQuery, Message

from bot.constants import (
    BOT_NAME,
    CALLBACK_DICT,
    CANCEL_MSG,
    CMD_CANCEL,
    CMD_DEFAULT,
    CMD_START,
    CMD_TIMER,
    ERROR_CANCEL_MSG,
    ERROR_CMD_MSG,
    EVENT_CANCELLED_FORMAT,
    EVENT_ENDED_FORMAT,
    LOGGER_FORMAT,
    ZERO_TIME_DELTA,
)
from bot.countdown import build_countdown_text, build_event_message
from bot.storage import Storage

load_dotenv()
storage = Storage()

app = Client(
    BOT_NAME,
    api_id=os.environ.get('API_ID', ""),
    api_hash=os.environ.get('API_HASH', ""),
    bot_token=os.environ.get("BOT_TOKEN", ""),
)

logging.basicConfig(format=LOGGER_FORMAT)
logger = logging.getLogger(__name__)

_http_client: httpx.AsyncClient | None = None


def _get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(timeout=10)
    return _http_client


async def api_send_message(chat_id: int, text: str) -> int:
    """POST sendMessage to the Bot API with parse_mode=HTML; returns message_id."""
    client = _get_http_client()
    resp = await client.post(
        f"https://api.telegram.org/bot{os.environ.get('BOT_TOKEN', '')}/sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
    )
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(data)
    return data["result"]["message_id"]


async def api_edit_message(chat_id: int, message_id: int, text: str) -> None:
    """POST editMessageText to the Bot API with parse_mode=HTML."""
    client = _get_http_client()
    resp = await client.post(
        f"https://api.telegram.org/bot{os.environ.get('BOT_TOKEN', '')}/editMessageText",
        json={"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "HTML"},
    )
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(data)


# (chat_id, event_name) -> message_id of the live countdown message
event_messages: dict[tuple[int, str], int] = {}
# (chat_id, event_name) -> asyncio task that edits the message at the deadline
event_tasks: dict[tuple[int, str], asyncio.Task] = {}


@app.on_message(filters.command(CMD_START))
async def start(_, message: Message) -> None:
    """The main method for the start message"""
    await message.reply(
        text=CALLBACK_DICT[CMD_START].get_msg(),
        reply_markup=CALLBACK_DICT[CMD_START].get_markup()
    )


@app.on_message(filters.command(CMD_CANCEL))
async def cancel(_, message: Message) -> None:
    """The main method for the cancel message"""
    try:
        _, event_name = message.text.split(' ', 1)
        if not storage.delete_event(message.chat.id, event_name):
            raise ValueError(ERROR_CANCEL_MSG)
        await message.reply(
            text=CANCEL_MSG.format(event_name=event_name),
        )
        key = (message.chat.id, event_name)
        task = event_tasks.pop(key, None)
        if task:
            task.cancel()
        message_id = event_messages.pop(key, None)
        if message_id is not None:
            try:
                await api_edit_message(
                    message.chat.id,
                    message_id,
                    build_event_message(EVENT_CANCELLED_FORMAT, event_name),
                )
            except Exception:
                logger.exception(
                    "Failed to edit cancelled message for event %s", event_name)
    except ValueError:
        await message.reply(
            text=ERROR_CANCEL_MSG,
        )


@app.on_message(filters.command(CMD_TIMER))
async def start_timer(_, message: Message) -> None:
    """The main method for the timer message"""
    try:
        # [command, date, time, event_name]
        _, date, time, event_name = message.text.split(' ', 3)
        deadline = storage.add_event(
            message.chat.id, event_name, f"{date} {time}")
        logger.info(f"Event {event_name} added for {deadline}")

        if deadline - datetime.datetime.now() < ZERO_TIME_DELTA:
            await message.reply(
                text=build_event_message(EVENT_ENDED_FORMAT, event_name),
            )
            return

        unix = int(deadline.timestamp())
        text = build_countdown_text(event_name, unix)
        try:
            message_id = await api_send_message(message.chat.id, text)
        except Exception:
            logger.exception(
                "Failed to send countdown message for event %s", event_name)
            await message.reply(text=ERROR_CMD_MSG)
            return

        key = (message.chat.id, event_name)
        event_messages[key] = message_id
        event_tasks[key] = asyncio.create_task(
            end_countdown(message.chat.id, event_name, deadline))

    except (ValueError, TypeError):
        await message.reply(text=ERROR_CMD_MSG)


async def end_countdown(chat_id: int, event_name: str, deadline: datetime.datetime) -> None:
    """Waits until the deadline, then edits the countdown message to the ended message."""
    key = (chat_id, event_name)
    delay = (deadline - datetime.datetime.now()).total_seconds()
    if delay > 0:
        await asyncio.sleep(delay)
    if storage.get_events(chat_id, event_name) is None:
        # Event was cancelled; the cancel handler already edited the message.
        event_messages.pop(key, None)
        event_tasks.pop(key, None)
        return
    storage.delete_event(chat_id, event_name)
    message_id = event_messages.pop(key, None)
    event_tasks.pop(key, None)
    if message_id is None:
        return
    try:
        await api_edit_message(
            chat_id,
            message_id,
            build_event_message(EVENT_ENDED_FORMAT, event_name),
        )
    except Exception:
        logger.exception("Failed to edit countdown message for event %s", event_name)


@app.on_callback_query()
async def callback(_, query: CallbackQuery) -> None:
    msgpack = CALLBACK_DICT.get(str(query.data), CALLBACK_DICT[CMD_DEFAULT])

    # Get the message
    text = msgpack.get_msg()
    markup = msgpack.get_markup()

    # Update the message
    await query.edit_message_text(text, reply_markup=markup)
    logger.info(f"Callback {query.data} is called")

if __name__ == "__main__":
    logger.info("Starting the bot")
    app.run()
