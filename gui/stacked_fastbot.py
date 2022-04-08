"""
@Author  :   Lan
@env     :   Python 3.7.2
@Time    :   2021/8/6 10:00 AM
@Desc    :
"""
import logging
import threading

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from config import qss_cfg, config
from gui.dialog import DiaLog, Notice
from gui.stacked_adbkit import AdbKitPage
from gui.stacked_tidevice import TiDevicePage
from utils.adbkit import AdbKit
from utils.fastbot_android import FastbotAndroid
from utils.tidevice import TiDevice


class Fastbot(object):
    def __init__(self):

        self.widget = QWidget()
        self.layout = QVBoxLayout(self.widget)
        self.dialog = DiaLog(self.widget)
        self.notice = Notice()

        self.widget.setObjectName('right_widget')
        self.widget.setStyleSheet(qss_cfg.RIGHT_STYLE)  # 设置右侧部件美化

        self.init_ui()
        self.add_event()

    def init_ui(self):
        # Package
        self.label_package = QLabel("Package:")
        self.combox_package = QComboBox()  # 包名下拉框
        self.combox_package.setFixedSize(200, 25)
        self.combox_package.addItems(config.PKG_NAME)

        self.layout_package = QHBoxLayout()
        self.layout_package.addStretch(1)
        self.layout_package.addWidget(self.label_package)
        self.layout_package.addWidget(self.combox_package)
        self.layout_package.addStretch(1)

        # Duration
        self.label_duration = QLabel("Duration:")
        self.edit_duration = QLineEdit()
        self.edit_duration.setStyleSheet(qss_cfg.TEXT_EDIT_STYLE)
        self.edit_duration.setFixedSize(200, 25)

        self.layout_duration = QHBoxLayout()
        self.layout_duration.addStretch(1)
        self.layout_duration.addWidget(self.label_duration)
        self.layout_duration.addWidget(self.edit_duration)
        self.layout_duration.addStretch(1)

        # Throttle
        self.label_throttle = QLabel("Throttle:")
        self.combox_throttle = QComboBox()
        self.combox_throttle.setFixedSize(200, 25)
        self.combox_throttle.addItems(config.THROTTLE_LIST)
        self.combox_throttle.setCurrentIndex(3)

        self.layout_throttle = QHBoxLayout()
        self.layout_throttle.addStretch(1)
        self.layout_throttle.addWidget(self.label_throttle)
        self.layout_throttle.addWidget(self.combox_throttle)
        self.layout_throttle.addStretch(1)

        # output dir
        self.label_output = QLabel("安卓设备日志目录:")
        self.edit_output = QLineEdit()
        self.edit_output.setFixedSize(200, 25)
        self.edit_output.setStyleSheet(qss_cfg.TEXT_EDIT_STYLE)
        self.edit_output.setText("sdcard/fastbot")

        self.layout_output = QHBoxLayout()
        self.layout_output.addStretch(1)
        self.layout_output.addWidget(self.label_output)
        self.layout_output.addWidget(self.edit_output)
        self.layout_output.addStretch(1)

        # android btn
        self.btn_android = QPushButton("Android Runner")
        self.btn_android.setFixedSize(150, 30)
        self.btn_android.setStyleSheet(qss_cfg.BTN_COLOR_GREEN_NIGHT)

        # ios btn
        self.btn_ios = QPushButton("iOS Runner")
        self.btn_ios.setFixedSize(150, 30)
        self.btn_ios.setStyleSheet(qss_cfg.BTN_COLOR_GREEN_NIGHT)

        self.layout_btn = QHBoxLayout()
        self.layout_btn.addStretch(1)
        self.layout_btn.addWidget(self.btn_android)
        self.layout_btn.addWidget(self.btn_ios)
        self.layout_btn.addStretch(1)

        # 添加到参数布局内
        self.layout_settings = QVBoxLayout()
        self.layout_settings.addStretch(1)
        self.layout_settings.addLayout(self.layout_package)
        self.layout_settings.addStretch(1)
        self.layout_settings.addLayout(self.layout_duration)
        self.layout_settings.addStretch(1)
        self.layout_settings.addLayout(self.layout_throttle)
        self.layout_settings.addStretch(1)
        self.layout_settings.addLayout(self.layout_output)
        self.layout_settings.addStretch(2)
        self.layout_settings.addLayout(self.layout_btn)
        self.layout_settings.addStretch(2)

        # 创建控制台布局
        self.edit_console = QTextEdit()
        self.edit_console.append(f"日志目录: {config.LOGCAT_PATH}")
        self.edit_console.append(f"安卓如果出现闪退或者 OOM，日志会自动推送到该目录下！")
        self.edit_console.append(f"苹果运行日志会自动存储在该目录下，需要人工查看是否出错！")
        self.edit_console.append(f"TODO：抱歉，由于多线程之前互相调用原因，这里暂时还不能实时输出日志。")
        self.edit_console.setReadOnly(True)
        self.edit_console.setStyleSheet(qss_cfg.TEXT_EDIT_STYLE)

        self.layout_console = QVBoxLayout()
        self.layout_console.addWidget(self.edit_console)

        # 将参数布局 和 控制台布局 添加到总布局
        self.layout.addLayout(self.layout_settings)
        self.layout.addLayout(self.layout_console)

    def add_event(self):
        if AdbKitPage().current_device():
            self.btn_android.clicked.connect(lambda: threading.Thread(target=self.android_fastbot().run).start())
        else:
            self.btn_android.clicked.connect(lambda: self.notice.error("Can't find any android device/emulator"))

        if TiDevicePage().current_device():
            self.btn_ios.clicked.connect(lambda: threading.Thread(target=self.ios_fastbot).start())
        else:
            self.btn_ios.clicked.connect(lambda: self.notice.error("Can't find any iOS device/emulator"))


    def android_fastbot(self):
        package = self.combox_package.currentText()
        duration = self.edit_duration.text()
        throttle = self.combox_throttle.currentText()
        output = self.edit_output.text()

        if AdbKitPage().adb():
            self.edit_console.append("Fastbot - Android - Running ...")

            try:
                fastbot = FastbotAndroid(
                    package=package,
                    duration=duration,
                    throttle=throttle,
                    output=output
                )
                # fastbot.run()
                return fastbot
            except Exception as e:
                self.dialog.error(e)

    def ios_fastbot(self):
        package = self.combox_package.currentText()
        duration = self.edit_duration.text()
        throttle = self.combox_throttle.currentText()

        self.edit_console.append("Fastbot - iOS - Running ...")

        try:
            TiDevice().fastbot_and_logcat(
                bundle_id=package,
                duration=duration,
                throttle=throttle,
            )
        except Exception as e:
            self.dialog.error(e)

