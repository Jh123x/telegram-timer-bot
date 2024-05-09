import unittest
from msg_pack import MsgPack

class TestMsgPack(unittest.TestCase):
    def setUp(self) -> None:
        self.msg_pack = MsgPack('Hello', None)
        return super().setUp()
    
    def tearDown(self) -> None:
        self.msg_pack = None
        return super().tearDown()
    
    def test_get_msg(self) -> None:
        """Test the get_msg method"""
        assert self.msg_pack.get_msg() == 'Hello'
    
    def test_get_markup(self) -> None:
        """Test the get_markup method"""
        assert self.msg_pack.get_markup() == None

if __name__ == '__main__':
    unittest.main()