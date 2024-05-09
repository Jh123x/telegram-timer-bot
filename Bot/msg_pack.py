from pyrogram.types import InlineKeyboardMarkup


class MsgPack:
    def __init__(self: 'MsgPack', text: str, markup: InlineKeyboardMarkup) -> None:
        """MsgPack stores the message text and markup"""
        self.msg = text
        self.markup = markup

    def get_msg(self: 'MsgPack') -> str:
        """Returns the message text"""
        return self.msg

    def get_markup(self: 'MsgPack') -> InlineKeyboardMarkup:
        """Returns the message markup"""
        return self.markup
