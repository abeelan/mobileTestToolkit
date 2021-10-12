"""
@Time   : 2021/5/14 11:45 上午
@Author : lan
@Mail   : lanzy.nice@gmail.com
@Desc   :

1. 遍历安装包路径；
2. 安装包并打开
3. 获取当前版本号和版本名称
4. 存储
"""
import os
import logging
from time import sleep
from utils.adbkit import AdbKit


class GetApkInfo:

    def __init__(self):
        self.adb = AdbKit()

    def get_apk_path(self, dir_path):
        """获取所有历史包的路径，组成列表"""
        # 4.14.1 为测试环境，没有出线上环境的历史包
        filenames = [f for f in os.listdir(dir_path) if f.startswith("esbooks")]
        filenames.sort()
        return filenames

    def get_info(self, pkg_name):
        """获取当前版本号和版本名称"""
        pkg_info = self.adb.app_info(pkg_name)
        version_name = pkg_info["version_name"]
        version_code = pkg_info["version_code"]
        return version_name, version_code

    def save_as(self, filepath, message):
        with open(filepath, "a") as f:
            f.write(message)


if __name__ == '__main__':

    _apk_path = "/Users/lan/Downloads/"
    _pkg_name = "com.esbook.reader"

    app = GetApkInfo()
    filenames = app.get_apk_path(_apk_path)

    for f in filenames:
        apk = f"{_apk_path}{f}"
        app.adb.install(apk)
        logging.info(f"正在安装: {f}")
        sleep(5)

        message = app.get_info(_pkg_name)
        logging.info(f"获取信息: {message}")
        app.save_as("./data.yaml", f"{message[0]} -> {message[1]}\n")
        sleep(2)

        app.adb.uninstall(_pkg_name)
        sleep(1)
        logging.info("卸载完成...")
        logging.info("\nNext >>>\n")

