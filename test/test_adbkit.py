"""
@Time   : 2021/3/16 10:49 上午
@Author : lan
@Mail   : lanzy.nice@gmail.com
@Desc   : 
"""
import pytest

from utils.adbkit import AdbKit


class TestAdbKit:

    def test_adb_device(self):
        """测试 adbutils 提供的 API
        """
        adb = AdbKit().adb_device

        # 获取设备串号
        print(adb.serial)

        # 获取当前界面应用的act
        # {'package': 'com.android.settings', 'activity': 'com.android.settings.MainSettings'}
        print(adb.current_app())

        # 安装
        # adb.install("apk_path...")
        # 卸载
        # adb.uninstall("com.esbook.reader")

        # 拉起应用
        # adb.app_start("com.android.settings")  # 通过 monkey 拉起
        # adb.app_start("com.android.settings", "com.android.settings.MainSettings")  # 通过 am start 拉起
        # 清空APP
        # adb.app_clear("com.esbook.reader")
        # 杀掉应用
        # adb.app_stop("com.esbook.reader")

        # 获取屏幕分辨率
        # x, y = adb.window_size()
        # print(f"{x}*{y}")  # 1080*1920

        # 获取当前屏幕状态 亮/熄
        # print(adb.is_screen_on())  # bool

        # adb.switch_wifi(True)  # 需要开启 root 权限
        # adb.switch_airplane(False)  # 切换飞行模式
        # adb.switch_screen(True)  # 亮/熄屏

        # 获取 IP 地址
        # print(adb.wlan_ip())

        # 打开浏览器并跳转网页
        # adb.open_browser("http://www.baidu.com")

        # adb.swipe(500, 800, 500, 200, 0.5)
        # adb.click(500, 500)

        # print(adb.package_info("com.esbook.reader"))  # dict

        # print(adb.rotation())  # 屏幕是否转向
        # adb.screenrecord()  # 录屏

    def test_current_wifi_name(self):
        assert AdbKit().wifi() == "easou2"

    def test_serial(self):
        assert AdbKit().serial == "GBG5T19731003744"

    def test_model(self):
        assert AdbKit().model() == "ELE-AL00"

    def test_manufacturer(self):
        assert AdbKit().manufacturer() == "HUAWEI"

    def test_state(self):
        assert AdbKit().state() == "device"

    def test_device_version(self):
        assert AdbKit().device_version() == "10"

    def test_sdk_version(self):
        assert AdbKit().sdk_version() == "29"

    def test_device_info(self):
        print(AdbKit().device_info_complete())

    def test_get_pkg_pid(self):
        assert len(AdbKit().get_pid("com.android.settings")) == 5

    def test_pm_list_package(self):
        # print(AdbKit().adb_device.list_packages())
        print(AdbKit().list_packages())

    def test_pm_path_package(self):
        print(AdbKit().pm_path_package("com.android.settings"))


if __name__ == '__main__':
    pytest.main()
