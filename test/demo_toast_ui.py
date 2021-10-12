"""
@Time   : 2021/3/2 10:25 上午
@Author : lan
@Mail   : lanzy.nice@gmail.com
@Desc   :
"""
import sys
import threading

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore


class Toast(QtWidgets.QWidget):

    TIME_DEFAULT = 3
    TIME_LONG = 5

    def __init__(self):
        super(Toast, self).__init__()

        # 设置窗体透明
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # 设置 toast 样式
        self.background_color = QtGui.QColor("#778899")
        self.text_color = QtCore.Qt.white
        self.font = QtGui.QFont('Simsun', 18)
        self.text = 'Hello World'
        self.min_height = 10
        self.min_width = 10
        self.pos = QtCore.QPointF(0, 0)

    def move_toast(self):
        # 计算气泡长宽及移动气泡到指定位置
        self.height = self.get_font_size() * 2
        self.width = len(self.text) * self.height * 0.8
        # 设置最小值
        if self.height < self.min_height:
            self.height = self.min_height
        if self.width < self.min_width:
            self.width = self.min_width
        self.resize(self.width, self.height)

        # 当设置坐标点时，将toast框的中心放在坐标点的位置
        if self.pos.x() != 0 or self.pos.y() != 0:
            self.move(self.pos.x() - self.width / 2, self.pos.y() - self.height / 2)

    def make_text(self, pos, text, times=None, background_color=None):
        if pos:
            self.pos = pos
        if text:
            self.text = text
        if background_color:
            self.background_color = background_color
        timeout = times if times else self.TIME_DEFAULT

        self.move_toast()
        self.repaint()
        self.show()

        # 设置超时自动关闭
        toast_timer = threading.Timer(timeout, lambda: self.close())
        toast_timer.start()
        # for i in range(5):
        #     print(i)
        #     import time
        #     time.sleep(1)

    def toast_timeout(self):
        self.close()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing)
        rect_line_path = QtGui.QPainterPath()
        rectangle = QtCore.QRectF(0, 0, self.width, self.height)
        rect_line_path.addRoundedRect(rectangle, self.height / 2, self.height / 2, QtCore.Qt.AbsoluteSize)
        painter.fillPath(rect_line_path, QtGui.QColor(self.background_color))

        pen = QtGui.QPen(QtGui.QColor(self.text_color))
        painter.setPen(pen)
        painter.setFont(self.font)
        self.draw_text(painter)

    def get_font_size(self):
        return self.font.pointSizeF()

    def draw_text(self, painter):
        painter.drawText(
            QtCore.QRectF(0, 0, self.width, self.height),
            QtCore.Qt.AlignCenter, self.text
        )

    def mousePressEvent(self, event):
        # 定义鼠标点击事件
        if event.button() == QtCore.Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        # 定义鼠标移动事件
        if event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()

    def setMessage(self, message):
        self.ui.label.setText(message)


def toast(message, timeout=3):
    t = Toast()
    # t.make_text(QtCore.QPointF(1000, 1000), message, timeout)
    t.make_text(None, message, timeout)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # to = Toast()
    # # to.make_text(QtCore.QPointF(1000, 1000), "我是提示", 5)
    # to.make_text(None, "我是提示", 5)

    toast("我是提示")

    sys.exit(app.exec_())
