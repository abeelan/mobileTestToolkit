# -*- coding:utf-8 -*-

"""
@Author  :   Lan
@env     :   Python 3.7.2
@Time    :   2019/8/8 5:14 PM
@Desc    :   主窗口实现
"""
import os
import sys
import qtawesome

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from config import qss_cfg, config
from gui.right_window import RightStacked


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        """
         --------------
        |  1. 窗口设置  |
         --------------
        """
        self.setWindowTitle("测试工具")
        self.setFixedSize(900, 700)  # 设置窗体大小
        self.setWindowOpacity(0.96)  # 设置窗口透明度
        self.setAttribute(Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        self.setWindowFlag(Qt.FramelessWindowHint)  # 隐藏边框

        """
         --------------
        |  2. 布局设置  |
         --------------
        """
        '''2.1 创建主窗口部件'''
        self.main_widget = QWidget()  # 创建窗口主部件
        self.main_layout = QGridLayout()  # 创建主部件的网格布局
        self.main_layout.setSpacing(0)  # 设置左右侧部件间隙为0
        self.main_widget.setLayout(self.main_layout)  # 设置窗口主部件布局为网格布局

        '''2.2 创建左侧边栏部件'''
        self.left_sidebar = QWidget()  # 创建左侧部件
        self.left_sidebar.setObjectName('left_widget')

        # self.left_layout = QGridLayout()  # 创建左侧部件的网格布局层
        self.left_layout = QVBoxLayout()  # 创建左侧部件的网格布局层
        self.left_sidebar.setLayout(self.left_layout)  # 设置左侧部件布局为网格
        self.left_sidebar.setStyleSheet(qss_cfg.LEFT_STYLE)  # 设置左侧部件美化

        '''2.3 将左右侧部件添加到主窗口部件内'''
        self.right_stacked = RightStacked().right_stacked

        self.main_layout.addWidget(self.left_sidebar, 0, 0)  # 左侧部件在第0行第0列，占8行3列
        self.main_layout.addWidget(self.right_stacked, 0, 4)  # 右侧部件在第0行第3列，占8行9列
        self.setCentralWidget(self.main_widget)  # 设置窗口主部件

        """
         -----------------
        |  3. 左侧边栏设置  |
         -----------------
        """
        '''3.1 左上角 三个按钮'''
        # 创建按钮 按钮内文案为空
        self.btn_close = QPushButton("")  # 关闭
        self.btn_minimized = QPushButton("")  # 最小化
        self.btn_fullscreen = QPushButton("")  # 最大化
        # 设置按钮尺寸
        for btn in (self.btn_close,
                    self.btn_minimized,
                    self.btn_fullscreen):
            btn.setFixedSize(13, 13)
        # 设置按钮提示语
        self.btn_close.setToolTip("关闭窗口")
        self.btn_minimized.setToolTip("最小化暂不可用")
        self.btn_fullscreen.setToolTip("最大化暂不可用")
        # 设置按钮颜色
        self.btn_close.setStyleSheet(qss_cfg.BTN_COLOR_RED)
        self.btn_minimized.setStyleSheet(qss_cfg.BTN_COLOR_YELLOW)
        self.btn_fullscreen.setStyleSheet(qss_cfg.BTN_COLOR_GREEN)

        '''3.2 分类大标题设置'''
        self.left_label_android = QPushButton(qtawesome.icon('fa.android', color='white'), " AdbKit")
        self.left_label_ios = QPushButton(qtawesome.icon('fa.apple', color='white'), " iOSKit")
        self.left_label_fastbot = QPushButton(qtawesome.icon('fa.rocket', color='white'), " FastBot")

        for label in (
                self.left_label_android,
                self.left_label_ios,
                self.left_label_fastbot
        ):
            label.setObjectName('left_label')


        self.btn_layout = QHBoxLayout()
        self.btn_layout.addWidget(self.btn_close)
        self.btn_layout.addWidget(self.btn_minimized)
        self.btn_layout.addWidget(self.btn_fullscreen)

        self.left_layout.addLayout(self.btn_layout)
        self.left_layout.addStretch(3)
        self.left_layout.addWidget(self.left_label_android)
        self.left_layout.addStretch(1)
        self.left_layout.addWidget(self.left_label_ios)
        self.left_layout.addStretch(1)
        self.left_layout.addWidget(self.left_label_fastbot)
        self.left_layout.addStretch(10)

        """3.4 左侧边栏按钮事件绑定"""
        self.btn_close.clicked.connect(QCoreApplication.instance().quit)
        self.btn_minimized.clicked.connect(lambda: self.clicked_btn_minimized())
        self.btn_fullscreen.clicked.connect(lambda: self.clicked_btn_fullscreen())

        self.left_label_android.clicked.connect(lambda: self.switch_adbkit())
        self.left_label_ios.clicked.connect(lambda: self.switch_ios())
        self.left_label_fastbot.clicked.connect(lambda: self.switch_fastbot())

    """
     --------------
    | 点击后切换页面 |
     --------------
    """

    def switch_adbkit(self):
        self.right_stacked.setCurrentIndex(0)

    def switch_ios(self):
        self.right_stacked.setCurrentIndex(1)

    def switch_fastbot(self):
        self.right_stacked.setCurrentIndex(2)

    def clicked_btn_minimized(self):
        """窗口最小化"""
        # self.showMinimized()
        pass

    def clicked_btn_fullscreen(self):
        """窗口最大化"""
        # self.showFullScreen()
        # self.btn_fullscreen.clicked.connect(lambda: NotificationWindow.info('提示', '这是一条会自动关闭的消息'))
        pass

    """
     -----------------------
    | 重写鼠标移动事件
    | 目的：支持无边框窗体移动
     -----------------------
    """
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))  # 更改鼠标图标

    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.m_flag:
            self.move(QMouseEvent.globalPos() - self.m_Position)  # 更改窗口位置
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(QPixmap(config.APP_ICON)))  # 设置 app icon
    gui = MainWindow()
    gui.setWindowTitle("ToolKit")
    gui.show()
    sys.exit(app.exec_())
