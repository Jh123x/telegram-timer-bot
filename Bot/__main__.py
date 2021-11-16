import os
import datetime
import multiprocessing as mp

from time import sleep
from Storage import Storage
from dotenv import load_dotenv
from pyrogram import Client, filters
from constants import CALLBACK_DICT, ERROR_CMD_MSG, ZERO_TIME_DELTA, TIMER_FORMAT, EVENT_ENDED_FORMAT, POLLING_INTERVAL, TIME_FORMAT, CANCEL_MSG, ERROR_CANCEL_MSG, EVENT_CANCELLED_FORMAT

load_dotenv()
storage = Storage()

app = Client(
    "Timer Bot",
    api_id=os.environ.get('API_ID', None),
    api_hash=os.environ.get('API_HASH', None),
    bot_token=os.environ.get("BOT_TOKEN", None),
)


@app.on_message(filters.command('start'))
async def start(_, message):
    await message.reply(
        text=CALLBACK_DICT['start'].get_msg(),
        reply_markup=CALLBACK_DICT['start'].get_markup()
    )


@app.on_message(filters.command('cancel'))
async def cancel(_, message):
    try:
        _, event_name = message.text.split(' ', 1)
        if not storage.delete_event(message.chat.id, event_name):
            raise Exception(ERROR_CANCEL_MSG)
        await message.reply(
            text=CANCEL_MSG.format(event_name=event_name),
        )
    except:
        await message.reply(
            text=ERROR_CANCEL_MSG,
        )


@app.on_message(filters.command('timer'))
async def start_timer(_, message):
    """The main method for the timer message"""
    try:
        # [command, date, time, event_name]
        _, date, time, event_name = message.text.split(' ', 3)
        deadline = storage.add_event(
            message.chat.id, event_name, f"{date} {time}")

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
        await message.reply(
            text=ERROR_CMD_MSG
        )
        return


async def refresh_msg(msg, deadline: datetime.datetime, event_name: str):
    """Updates the event message until it is pass the deadline"""
    while True:
        sleep(POLLING_INTERVAL)
        time_left = deadline - datetime.datetime.now()
        if storage.get_events(msg.chat.id, event_name) is None:
            format = EVENT_CANCELLED_FORMAT
            break
        if time_left.total_seconds() < 0:
            format = EVENT_ENDED_FORMAT
            break
        event_string = get_event_string(time_left, event_name)
        await msg.edit(event_string)
    await msg.edit(format.format(event_name=event_name))


def get_event_string(time: datetime.timedelta, event_name: str):
    """Get the string format for event message"""
    return TIMER_FORMAT.format(time=get_time_string(time), event_name=event_name)


def get_time_string(time: datetime.timedelta):
    hours = time.seconds // 3600
    minutes = (time.seconds % 3600) // 60
    seconds = time.seconds % 60
    return TIME_FORMAT.format(days=time.days, hours=hours, minutes=minutes, seconds=seconds)


@app.on_callback_query()
async def callback(_, query):
    msgpack = CALLBACK_DICT.get(query.data,)

    # Get the message
    text = msgpack.get_msg()
    markup = msgpack.get_markup()

    # Update the message
    await query.edit_message_text(
        text,
        reply_markup=markup
    )

if __name__ == "__main__":
    app.run()
