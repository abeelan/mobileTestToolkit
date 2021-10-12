# -*- coding:utf-8 -*-

"""
@Author  :   Lan
@env     :   Python 3.7.2
@Time    :   2019/9/25 10:00 AM
@Desc    :
"""
import os
import logging
import threading

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from gui.dialog import DiaLog

from utils import common, systemer
from utils.common import MyThread
from utils.tidevice import TiDevice
from config import qss_cfg, config


class TiDevicePage:
    def __init__(self):
        self.widget = QWidget()  # 创建页面布局
        self.widget.setObjectName('right_widget')
        self.widget.setStyleSheet(qss_cfg.RIGHT_STYLE)  # 设置右侧部件美化

        self.layout = QVBoxLayout(self.widget)
        self.dialog = DiaLog(self.widget)

        self.init_ui()
        self.add_event()

    def init_ui(self):
        """"""
        """1. 设备选择区域"""
        self.label_device_choose = QLabel("连接设备列表：")

        self.cmb_device_choose = QComboBox()
        self.cmb_device_choose.setFixedSize(200, 30)
        # self.cmb_device_choose.addItems(self.device_list())  # 下拉框添加数据

        self.btn_refresh_device = QPushButton('刷新')
        self.btn_refresh_device.setFixedSize(40, 20)
        self.btn_refresh_device.setStyleSheet(qss_cfg.BTN_COLOR_YELLOW)

        self.layout_device_choose = QHBoxLayout()
        self.layout_device_choose.addWidget(self.label_device_choose)
        self.layout_device_choose.addWidget(self.cmb_device_choose)
        self.layout_device_choose.addWidget(self.btn_refresh_device)
        self.layout_device_choose.addStretch(1)

        """2. 获取设备信息按钮区域"""
        # 标签
        self.label_device = QLabel("设备操作")
        self.label_device.setObjectName('right_label')
        self.layout.addWidget(self.label_device)

        # 设备信息
        self.btn_device_info = QPushButton('设备信息')
        self.btn_device_info.setFixedSize(100, 30)
        self.btn_device_info.setStyleSheet(qss_cfg.BTN_COLOR_GREEN_NIGHT)

        # 安装列表
        self.btn_install_app_list = QPushButton("安装应用列表")
        self.btn_install_app_list.setFixedSize(100, 30)
        self.btn_install_app_list.setStyleSheet(qss_cfg.BTN_COLOR_GREEN_NIGHT)

        layout_00 = QHBoxLayout()
        layout_00.addWidget(self.btn_device_info)
        layout_00.addWidget(self.btn_install_app_list)
        layout_00.addStretch(1)

        # 安装APK
        self.btn_install = QPushButton('安装应用')
        self.btn_choose_apk = QPushButton('选择IPA')
        self.btn_qrcode = QPushButton('生成二维码')
        self.edit_apk_path = QLineEdit()

        self.btn_install.setToolTip('复制包链接 或者 选择路径')
        self.edit_apk_path.setPlaceholderText('请粘贴安装包下载链接 或 选择路径～')
        self.edit_apk_path.setFixedSize(400, 25)
        self.edit_apk_path.setStyleSheet(qss_cfg.TEXT_EDIT_STYLE)
        self.btn_choose_apk.setFixedSize(70, 20)
        self.btn_qrcode.setFixedSize(70, 20)

        self.btn_install.setStyleSheet(qss_cfg.BTN_COLOR_GREEN)
        self.btn_choose_apk.setStyleSheet(qss_cfg.BTN_COLOR_YELLOW)
        self.btn_qrcode.setStyleSheet(qss_cfg.BTN_COLOR_YELLOW)

        layout_01 = QHBoxLayout()
        layout_01.addWidget(self.btn_install)
        layout_01.addWidget(self.edit_apk_path)
        layout_01.addWidget(self.btn_choose_apk)
        layout_01.addWidget(self.btn_qrcode)
        layout_01.addStretch(1)

        # 包 启动、杀死进程、卸载
        self.btn_uninstall_app = QPushButton('卸载应用')
        self.btn_start_app = QPushButton('启动应用')
        self.btn_kill_app = QPushButton('杀死应用')

        self.edit_pkg_name = QLineEdit()
        self.edit_pkg_name.setFixedSize(160, 25)
        self.edit_pkg_name.setPlaceholderText('com.easou.esbook')
        self.edit_pkg_name.setText('com.easou.esbook')
        self.edit_pkg_name.setStyleSheet(qss_cfg.TEXT_EDIT_STYLE)

        layout_02 = QHBoxLayout()
        layout_02.addWidget(self.btn_uninstall_app)
        layout_02.addWidget(self.btn_start_app)
        layout_02.addWidget(self.btn_kill_app)
        layout_02.addWidget(self.edit_pkg_name)
        layout_02.addStretch(1)

        # 截图
        self.btn_screenshot = QPushButton('截图')
        self.btn_open_screenshot = QPushButton('打开截图')
        self.btn_open_screenshot_dir = QPushButton('打开目录')

        layout_03 = QHBoxLayout()
        layout_03.addWidget(self.btn_screenshot)
        layout_03.addWidget(self.btn_open_screenshot)
        layout_03.addWidget(self.btn_open_screenshot_dir)
        layout_03.addStretch(1)

        # 输出台
        self.label_output = QLabel("输出")
        self.label_output.setObjectName('right_label')
        self.layout.addWidget(self.label_output)

        self.edit_output = QTextEdit()
        self.edit_output.setReadOnly(True)  # 只读
        self.edit_output.setStyleSheet(qss_cfg.TEXT_EDIT_STYLE)
        self.edit_output.resize(600, 500)

        layout_04 = QHBoxLayout()
        layout_04.addWidget(self.edit_output)

        """设置页面通用按钮大小和颜色"""
        btn_list = [
            self.btn_install,
            self.btn_uninstall_app, self.btn_start_app, self.btn_kill_app,
            self.btn_screenshot, self.btn_open_screenshot, self.btn_open_screenshot_dir,
        ]
        for btn in btn_list:
            btn.setFixedSize(100, 30)
            btn.setStyleSheet(qss_cfg.BTN_COLOR_GREEN_NIGHT)

        '''添加各部件到主布局'''
        self.layout.addStretch(1)
        self.layout.addLayout(self.layout_device_choose)
        self.layout.addStretch(1)
        self.layout.addWidget(self.label_device)
        self.layout.addLayout(layout_00)  # 设备信息
        self.layout.addLayout(layout_01)  # 安装
        self.layout.addLayout(layout_02)  # 打开网页
        self.layout.addLayout(layout_03)  # 截图
        self.layout.addStretch(1)
        self.layout.addWidget(self.label_output)  # 输入控制台信息
        self.layout.addLayout(layout_04)  # 输入控制台信息
        self.layout.addStretch(1)

    def add_event(self):
        # 设备选择框
        self.cmb_device_choose.currentIndexChanged.connect(lambda: self.current_device())
        self.btn_refresh_device.clicked.connect(lambda: self.clicked_devices_check())

        # 获取设备信息
        self.btn_device_info.clicked.connect(lambda: self.clicked_get_device_info())
        self.btn_install_app_list.clicked.connect(lambda: self.clicked_get_app_list())

        # 安装应用
        self.btn_install.clicked.connect(lambda: self.clicked_btn_install())
        self.btn_choose_apk.clicked.connect(lambda: self.clicked_btn_choose_apk_path())
        self.btn_qrcode.clicked.connect(lambda: self.clicked_btn_qrcode())
        
        # 卸载 启动 杀掉
        self.btn_uninstall_app.clicked.connect(lambda: self.clicked_btn_uninsatll())
        self.btn_start_app.clicked.connect(lambda: self.clicked_btn_start_app())
        self.btn_kill_app.clicked.connect(lambda: self.clicked_btn_kill_app())

        # 截图
        self.btn_screenshot.clicked.connect(lambda: self.clicked_btn_screenshot())
        self.btn_open_screenshot.clicked.connect(lambda: self.clicked_btn_open_screenshot_path())
        self.btn_open_screenshot_dir.clicked.connect(lambda: self.clicked_btn_open_screenshot_dir())

    def device(self):
        d = TiDevice()
        if len(d.list()) == 0:
            self.edit_output.append("当前设备为空，TiDevice 初始化失败！")
            self.edit_output.moveCursor(QTextCursor.End)
            self.dialog.error("当前设备为空，TiDevice 初始化失败！")
            return
        return d

    def device_list(self):
        if self.device():
            return self.device().list(name=True)
        return []

    def current_device(self):
        """获取当前列表选中的设备"""
        device = self.cmb_device_choose.currentText()
        # logging.info(f"current device: {None if not device else device}")
        return device

    def clicked_devices_check(self):
        """刷新设备列表"""
        if self.device():
            devices_list = self.device().list(name=True)
            self.cmb_device_choose.clear()
            self.cmb_device_choose.addItems(devices_list)
            self.cmb_device_choose.setCurrentIndex(0)
            logging.info(f"Device checking... Now device list: {devices_list}")
            self.edit_output.append(f"Device checking... \nNow device list: {devices_list}")
            self.edit_output.moveCursor(QTextCursor.End)

    def clicked_get_device_info(self):
        """获取设备信息"""
        if self.device():
            output = "\n".join(self.device().info())
            self.edit_output.setText(output)

    def clicked_get_app_list(self):
        """获取已安装应用列表"""
        if self.device():
            output = "\n".join(self.device().app_list())
            self.edit_output.setText(output)

    def clicked_btn_install(self):
        """点击 安装应用 按钮"""
        text = self.edit_apk_path.text()
        if text.isspace() or len(text) == 0:
            info = "请输入安装包链接或本地路径～"
            logging.info(info)
            self.dialog.warning(info)
            return

        info = f"安装链接：{text}"
        logging.info(info)
        self.edit_output.append(info)
        self.edit_output.moveCursor(QTextCursor.End)

        if self.device():
            try:
                # t = threading.Thread(target=self.device().install, )
                t = MyThread(self.device().install, args=(text,))
                t.start()
                self.edit_output.setText("已启动子线程进行安装...请稍等...")
                t.join()
                self.edit_output.append(f"安装完成, 结果为 { t.get_result()}.")
            except Exception as e:
                self.dialog.error(f"安装失败, {e}.")

    def clicked_btn_uninsatll(self):
        if self.device():
            pkg_name = self.edit_pkg_name.text()
            info = f"卸载应用：{pkg_name}"
            self.edit_output.append(info)
            logging.info(info)
            output = self.device().uninstall(pkg_name)
            self.edit_output.append("\n".join(output))
            self.edit_output.moveCursor(QTextCursor.End)

    def clicked_btn_start_app(self):
        if self.device():
            pkg_name = self.edit_pkg_name.text()
            info = f"启动应用：{pkg_name}"
            self.edit_output.append(info)
            logging.info(info)
            output = self.device().launch(pkg_name)
            self.edit_output.append("\n".join(output))
            self.edit_output.moveCursor(QTextCursor.End)

    def clicked_btn_kill_app(self):
        if self.device():
            pkg_name = self.edit_pkg_name.text()
            info = f"关闭应用：{pkg_name}"
            self.edit_output.append(info)
            logging.info(info)
            output = self.device().kill(pkg_name)
            self.edit_output.append("\n".join(output))
            self.edit_output.moveCursor(QTextCursor.End)

    def clicked_btn_choose_apk_path(self):
        """点击 选择 IPA 按钮，通过 apk 文件选择框 选择安装路径，"""
        # 对话框的文件扩展名过滤器 filter，设置多个文件扩展名过滤，使用双引号隔开；
        # “All Files(*);;PDF Files(*.pdf);;Text Files(*.txt)”
        open_path = QFileDialog()
        path = open_path.getOpenFileName(filter='IPA Files(*.ipa);;')
        self.edit_apk_path.setText(path[0])

    def clicked_btn_qrcode(self):
        """点击生成二维码"""
        text = self.edit_apk_path.text()
        if text:
            try:
                os.system(f'open {common.qr_code(text)}')
            except OSError:
                os.system(f'start explorer {common.qr_code(text)}')
        else:
            logging.info("文本为空，不生成二维码！")
            self.dialog.about("文本框内容为空，不生成二维码！")

    def clicked_btn_screenshot(self):
        """截图"""
        # t = threading.Thread(target=self.device().screenshot, args=(config.SCREEN_PATH,))
        if self.device():
            t = threading.Thread(target=self.device().screenshot)
            t.start()
            self.edit_output.append("正在截图中... 请稍等...")
            t.join()
            self.edit_output.append("截图完成")
            self.dialog.about('截图完成')
            self.edit_output.moveCursor(QTextCursor.End)

    def clicked_btn_open_screenshot_path(self):
        """打开截图"""
        filename = systemer.get_latest_file(config.SCREEN_PATH)
        if not systemer.open_path(filename):
            self.dialog.warning("打开失败，当前目录为空！")

        self.edit_output.append(f"[ OPEN ] ==> {filename}")
        self.edit_output.moveCursor(QTextCursor.End)

    def clicked_btn_open_screenshot_dir(self):
        """打开截图目录"""
        screen_path = config.SCREEN_PATH
        systemer.open_path(screen_path)
        self.edit_output.append(f"[ OPEN ] ==> {screen_path}")
        self.edit_output.moveCursor(QTextCursor.End)
