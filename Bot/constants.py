
##################### Do not change those within this ###################################
import datetime
from MsgPack import MsgPack
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


ZERO_TIME_DELTA = datetime.timedelta(0)
BOT_NAME = "TimerBot"
COMMAND_FORMAT = "`/timer {dd/mm/yyyy} {24hr in (HOUR:MINUTE)} {Event Name}`"
CANCEL_FORMAT = "`/cancel {Event Name}`"
##################### Do not change those within this ###################################

# Enums
CMD_START = 'start'
CMD_HELP = 'help'
CMD_DEFAULT = 'default'
CMD_TIMER = 'timer'
CMD_CANCEL = 'cancel'

# Logger Format
LOGGER_FORMAT = '%(asctime)s %(clientip)-15s %(user)-8s %(message)s'

# Interval to edit the message (Default 30 seconds)
POLLING_INTERVAL = 10

# Format for Display
TIMER_FORMAT = "**{event_name}**\n⏳{time}\nThis updates every " + \
    str(POLLING_INTERVAL) + " seconds."
EVENT_ENDED_FORMAT = "{event_name} has already ended :("
EVENT_CANCELLED_FORMAT = "{event_name} is cancelled :("
TIME_FORMAT = "{days} Days, {hours} Hours, {minutes} Minutes {seconds} Seconds left"

START_MSG = f'Welcome to the {BOT_NAME} bot, feel free to look around'
CANCEL_MSG = "{event_name} is cancelled."
HELP_MSG = f'To use the bot just type {COMMAND_FORMAT} and the bot will start to countdown to the given date and time.\nDo {CANCEL_FORMAT} to cancel the event'
ERROR_MSG = 'This function is not implemented yet. Press back to go back.'
ERROR_CMD_MSG = f'Invalid format, the message is the format: {COMMAND_FORMAT}'
ERROR_CANCEL_MSG = f'Invalid format, the message is the format: {CANCEL_FORMAT}'


# Menu format (Change this if you know what you are doing)
# Call back 'help' -> MsgPack(helpmsg, help)
# Create your own buttons with `callback_name` `MsgPack(callback_name, callback_data)``

START = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton('HELP ❓', callback_data=CMD_HELP)
        ],
    ]
)


HELP = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton('Back ⬅️', callback_data=CMD_START)
        ],
    ]
)

ERROR = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton('Back ⬅️', callback_data=CMD_START)
        ],
    ]
)

CALLBACK_DICT = {
    CMD_START: MsgPack(START_MSG, START),
    CMD_HELP: MsgPack(HELP_MSG, HELP),
    CMD_DEFAULT: MsgPack(ERROR_MSG, ERROR),
}
