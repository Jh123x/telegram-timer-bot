import os
import datetime
import logging
from time import sleep
from dotenv import load_dotenv
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message, CallbackQuery

from bot.storage import Storage
from bot.constants import (
    CALLBACK_DICT, ERROR_CMD_MSG, ZERO_TIME_DELTA, TIMER_FORMAT,
    EVENT_ENDED_FORMAT, POLLING_INTERVAL, TIME_FORMAT, CANCEL_MSG,
    ERROR_CANCEL_MSG, EVENT_CANCELLED_FORMAT, CMD_START, CMD_DEFAULT,
    CMD_CANCEL, CMD_TIMER, BOT_NAME, LOGGER_FORMAT,
)

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

        time_left: datetime.timedelta = deadline - datetime.datetime.now()
        if time_left < ZERO_TIME_DELTA:
            await message.reply(
                text=EVENT_ENDED_FORMAT.format(event_name=event_name),
            )
            return

        event_string = get_event_string(time_left, event_name)
        msg = await app.send_message(message.chat.id, event_string)

        await refresh_msg(msg, deadline, event_name)

    except (ValueError, TypeError):
        await message.reply(text=ERROR_CMD_MSG)


async def refresh_msg(msg, deadline: datetime.datetime, event_name: str) -> None:
    """Updates the event message until it is pass the deadline"""
    while True:
        sleep(POLLING_INTERVAL)
        time_left = deadline - datetime.datetime.now()
        if storage.get_events(msg.chat.id, event_name) is None:
            format = EVENT_CANCELLED_FORMAT
            logger.info(f"Event {event_name} was cancelled")
            break

        if time_left.total_seconds() < 0:
            format = EVENT_ENDED_FORMAT
            logger.info(f"Event {event_name} has ended")
            break

        event_string = get_event_string(time_left, event_name)
        await msg.edit(event_string)

        logger.info(f"Event {event_name} updated for {time_left}")

    await msg.edit(format.format(event_name=event_name))


def get_event_string(time: datetime.timedelta, event_name: str) -> str:
    """Get the string format for event message"""
    return TIMER_FORMAT.format(time=get_time_string(time), event_name=event_name)


def get_time_string(time: datetime.timedelta) -> str:
    """Returns the time in the format of TIME_FORMAT"""
    hours = time.seconds // 3600
    minutes = (time.seconds % 3600) // 60
    seconds = time.seconds % 60
    return TIME_FORMAT.format(days=time.days, hours=hours, minutes=minutes, seconds=seconds)


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
