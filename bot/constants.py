# Do not change those within this
import datetime

ZERO_TIME_DELTA = datetime.timedelta(0)
BOT_NAME = "TimerBot"
COMMAND_FORMAT = "<code>/timer {dd/mm/yyyy} {24hr in (HOUR:MINUTE)} {Event Name}</code>"
CANCEL_FORMAT = "<code>/cancel {Event Name}</code>"
# Do not change those within this

# Enums
CMD_START = 'start'
CMD_HELP = 'help'
CMD_TIMER = 'timer'
CMD_CANCEL = 'cancel'

# Logger Format
LOGGER_FORMAT = '%(asctime)s %(levelname)s %(message)s'

# Format for Display
TIMER_FORMAT = '<b>{event_name}</b>\n⏳ <tg-time unix="{unix}" format="r">0</tg-time>'
EVENT_ENDED_FORMAT = "{event_name} has already ended :("
EVENT_CANCELLED_FORMAT = "{event_name} is cancelled :("

START_MSG = f'Welcome to the {BOT_NAME} bot, feel free to look around\n\nDo /help if you need help'
CANCEL_MSG = "{event_name} is cancelled."
HELP_MSG = f'''To use the bot just type {COMMAND_FORMAT} and the bot will start to countdown to the given date and time.
Do {CANCEL_FORMAT} to cancel the event'''
ERROR_CMD_MSG = f'Invalid format, the message is the format: {COMMAND_FORMAT}'
ERROR_CANCEL_MSG = f'Invalid format, the message is the format: {CANCEL_FORMAT}'
