from pyrogram.types import InlineKeyboardMarkup


class MsgPack:
    def __init__(self: 'MsgPack', text: str, markup: InlineKeyboardMarkup) -> None:
        self.msg = text
        self.markup = markup

    def get_msg(self: 'MsgPack') -> str:
        return self.msg

    def get_markup(self: 'MsgPack') -> InlineKeyboardMarkup:
        return self.markup
