"""
@Time   : 2021/8/6 上午9:16
@Author : lan
@Mail   : lanzy.nice@gmail.com
@Desc   : 
"""
from utils.tidevice import TiDevice
import logging
from utils import logger

logger.Logger()


class TestTiDevice:

    def setup_class(self):

        self.d = TiDevice()

    def test_shell(self):
        self.d.shell("version")

    def test_list(self):
        print(self.d.list(name=True))
