from pyrogram.types import InlineKeyboardMarkup


class MsgPack(object):
    def __init__(self, text: str, markup: InlineKeyboardMarkup):
        self.msg = text
        self.markup = markup

    def get_msg(self):
        return self.msg

    def get_markup(self):
        return self.markup
