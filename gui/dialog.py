"""
@Time   : 2021/3/1 7:27 下午
@Author : lan
@Mail   : lanzy.nice@gmail.com
@Desc   : 
"""

from PyQt5.QtWidgets import *


class DiaLog(object):
    def __init__(self, widget):
        self.widget = widget
        self.box = QMessageBox()

    def about(self, body, title=''):
        self.box.about(self.widget, title, body)

    def warning(self, body):
        self.box.warning(self.widget, 'title', '\n%s' % body)

    def error(self, text, title='错误'):
        self.box.critical(self.widget, title, text)


