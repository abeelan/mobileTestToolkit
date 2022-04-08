# -*- coding:utf-8 -*-

"""
@Author  :   lan
@env     :   Python 3.7.2
@Time    :   2019/8/14 4:46 PM
"""

from utils.systemer import get_abs_path, mkdir

# 绝对路径
LOGCAT_PATH = get_abs_path("logcat")  # 日志路径
SCREEN_PATH = get_abs_path("screen")  # 截图路径
FASTBOT_PATH = get_abs_path("config/fastbot")

# 使用 pyinstall 打包，必须使用绝对路径才能显示出图片来
APP_ICON = get_abs_path("favicon.ico")  # APP ICON

mkdir(LOGCAT_PATH)
mkdir(SCREEN_PATH)

# fastbot 填写待测包名
PKG_NAME = [
    "com.android.settings",
]

# 删除文件夹名称列表
DEL_FOLDER_NAME = [
    "baidu",
]

# 执行 fastbot 事件间隔
THROTTLE_LIST = [
    '100',
    '200',
    '300',
    '400',
    '500',
]

