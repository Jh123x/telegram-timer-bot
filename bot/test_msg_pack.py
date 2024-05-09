import unittest
from .msg_pack import MsgPack
from .constants import HELP


class TestMsgPack(unittest.TestCase):
    def setUp(self) -> None:
        self.msg_pack = MsgPack('Hello', HELP)
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_get_msg(self) -> None:
        """Test the get_msg method"""
        assert self.msg_pack.get_msg() == str('Hello')

    def test_get_markup(self) -> None:
        """Test the get_markup method"""
        assert self.msg_pack.get_markup() == HELP
