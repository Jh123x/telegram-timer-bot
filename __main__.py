import datetime
import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    Job,
)

from bot.constants import (
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

logging.basicConfig(format=LOGGER_FORMAT, level=logging.INFO)
logger = logging.getLogger(__name__)

# (chat_id, event_name) -> message_id of the live countdown message
event_messages: dict[tuple[int, str], int] = {}
# (chat_id, event_name) -> scheduled Job that edits the message at the deadline
event_jobs: dict[tuple[int, str], Job] = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """The main method for the start message"""
    await update.message.reply_text(
        text=CALLBACK_DICT[CMD_START].get_msg(),
        reply_markup=CALLBACK_DICT[CMD_START].get_markup(),
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """The main method for the cancel message"""
    message = update.message
    try:
        _, event_name = message.text.split(' ', 1)
        if not storage.delete_event(message.chat_id, event_name):
            raise ValueError(ERROR_CANCEL_MSG)
        await message.reply_text(
            text=CANCEL_MSG.format(event_name=event_name),
        )
        key = (message.chat_id, event_name)
        job = event_jobs.pop(key, None)
        if job:
            try:
                job.schedule_removal()
            except Exception:
                logger.exception("Failed to remove job for event %s", event_name)
        message_id = event_messages.pop(key, None)
        if message_id is not None:
            try:
                await context.bot.edit_message_text(
                    chat_id=message.chat_id,
                    message_id=message_id,
                    text=build_event_message(EVENT_CANCELLED_FORMAT, event_name),
                    parse_mode=ParseMode.HTML,
                )
            except Exception:
                logger.exception("Failed to edit cancelled message for event %s", event_name)
    except (AttributeError, ValueError):
        await message.reply_text(
            text=ERROR_CANCEL_MSG,
        )


async def start_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """The main method for the timer message"""
    message = update.message
    try:
        # [command, date, time, event_name]
        _, date, time, event_name = message.text.split(' ', 3)
        deadline = storage.add_event(
            message.chat_id, event_name, f"{date} {time}")
        logger.info("Event %s added for %s", event_name, deadline)

        if deadline - datetime.datetime.now() < ZERO_TIME_DELTA:
            await message.reply_text(
                text=build_event_message(EVENT_ENDED_FORMAT, event_name),
                parse_mode=ParseMode.HTML,
            )
            return

        unix = int(deadline.timestamp())
        text = build_countdown_text(event_name, unix)
        try:
            msg = await context.bot.send_message(
                chat_id=message.chat_id, text=text, parse_mode=ParseMode.HTML)
        except Exception:
            logger.exception("Failed to send countdown message for event %s", event_name)
            storage.delete_event(message.chat_id, event_name)
            await message.reply_text(text=ERROR_CMD_MSG)
            return

        key = (message.chat_id, event_name)
        # A pending timer with the same event name must be removed before
        # registering the new one, otherwise the old deadline job would fire
        # and end the new timer early.
        old_job = event_jobs.pop(key, None)
        if old_job:
            try:
                old_job.schedule_removal()
            except Exception:
                logger.exception("Failed to remove old job for event %s", event_name)
        event_messages.pop(key, None)
        event_messages[key] = msg.message_id
        event_jobs[key] = context.job_queue.run_once(
            end_countdown, when=deadline.astimezone(), data=key)

    except (AttributeError, ValueError, TypeError):
        await message.reply_text(text=ERROR_CMD_MSG)


async def end_countdown(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Edits the countdown message to the ended message at the deadline."""
    key = context.job.data
    chat_id, event_name = key
    if storage.get_events(chat_id, event_name) is None:
        # Event was cancelled; the cancel handler already edited the message.
        event_messages.pop(key, None)
        event_jobs.pop(key, None)
        return
    storage.delete_event(chat_id, event_name)
    message_id = event_messages.pop(key, None)
    event_jobs.pop(key, None)
    if message_id is None:
        return
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=build_event_message(EVENT_ENDED_FORMAT, event_name),
            parse_mode=ParseMode.HTML,
        )
    except Exception:
        logger.exception("Failed to edit countdown message for event %s", event_name)


async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    # Answer first: the Telegram client shows a loading spinner on the button
    # until the callback query is answered.
    try:
        await query.answer()
    except Exception:
        logger.exception("Failed to answer callback query %r", query.data)
    msgpack = CALLBACK_DICT.get(str(query.data), CALLBACK_DICT[CMD_DEFAULT])
    try:
        await query.edit_message_text(
            text=msgpack.get_msg(), reply_markup=msgpack.get_markup())
    except Exception:
        logger.exception("Failed to edit message for callback %r", query.data)
    logger.info("Callback %r is called", query.data)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Logs exceptions raised in handlers with the update context."""
    logger.error(
        "Exception while handling update %s: %s",
        type(update).__name__ if update is not None else None,
        context.error,
        exc_info=context.error,
    )


def main() -> None:
    """Start the bot."""
    token = os.environ.get("BOT_TOKEN", "")
    if not token:
        raise SystemExit(
            "BOT_TOKEN is not set. Create a .env file with BOT_TOKEN=...")
    application = (
        Application.builder()
        .token(token)
        .build()
    )
    application.add_handler(CommandHandler(CMD_START, start))
    application.add_handler(CommandHandler(CMD_CANCEL, cancel))
    application.add_handler(CommandHandler(CMD_TIMER, start_timer))
    application.add_handler(CallbackQueryHandler(callback))
    application.add_error_handler(error_handler)
    logger.info("Starting the bot")
    application.run_polling()


if __name__ == "__main__":
    main()
