"""
@Time   : 2021/3/1 11:15 上午
@Author : lan
@Mail   : lanzy.nice@gmail.com
@Desc   :

TODO: 提交 pr， wlan_ip() 里面没有做无权限设备获取IP的处理，可以添加上
"""
import re
import os
import logging
import platform
import datetime
import subprocess
from random import random

import adbutils
import functools
from MyQR import myqr
from time import sleep
from adbutils import adb

from utils import systemer


def check_device(func):
    """设备检测，判断仅有设备时继续执行"""
    @functools.wraps(func)
    def wrapper(*args, **kw):
        device_list = AdbKit.device_list()
        logging.debug(f"设备连接列表：{device_list}")
        if len(device_list) == 0:
            logging.error("没有设备")
            raise RuntimeError("Can't find any android device/emulator")
        return func(*args, **kw)
    return wrapper


class AdbKit:
    """
    https://github.com/openatx/adbutils
    https://developer.android.com/studio/command-line/adb
    """
    def __init__(self, serial=None):
        self.serial = serial
        self.adb = adb
        self.adb_path = adbutils.adb_path()
        self.adb_device = adb.device(self.serial)

        self.shell = systemer.shell
        logging.debug(f"AdbKit(serial={serial})")

    def __adb_client(self):
        """AdbClient() API，这个函数不供调用，仅做演示"""
        adb.server_version()  # adb 版本
        adb.server_kill()  # adb kill-server
        adb.connect("192.168.190.101:5555")

    def __adb_device(self):
        """AdbDevice() API，这个函数不供调用，仅做演示"""
        device = self.adb_device

        print(device.serial)  # 获取设备串号

        print(device.prop.model)
        print(device.prop.device)
        print(device.prop.name)
        print(device.prop.get("ro.product.manufacturer"))

        # 获取当前应用包名和 activity
        # {'package': 'com.android.settings', 'activity': 'com.android.settings.MainSettings'}
        print(device.current_app())

        # 安装
        device.install("apk_path...")
        # 卸载
        device.uninstall("com.esbook.reader")

        # 拉起应用
        device.app_start("com.android.settings")  # 通过 monkey 拉起
        device.app_start("com.android.settings", "com.android.settings.MainSettings")  # 通过 am start 拉起
        # 清空APP
        device.app_clear("com.esbook.reader")
        # 杀掉应用
        device.app_stop("com.esbook.reader")

        # 获取屏幕分辨率 1080*1920
        x, y = device.window_size()
        print(f"{x}*{y}")

        # 获取当前屏幕状态 亮/熄
        print(device.is_screen_on())  # bool

        device.switch_wifi(True)  # 需要开启 root 权限
        device.switch_airplane(False)  # 切换飞行模式
        device.switch_screen(True)  # 亮/熄屏

        # 获取 IP 地址
        print(device.wlan_ip())

        # 打开浏览器并跳转网页
        device.open_browser("http://www.baidu.com")

        device.swipe(500, 800, 500, 200, 0.5)
        device.click(500, 500)
        device.keyevent("HOME")  # 发送事件
        device.send_keys("hello world$%^&*")  # simulate: adb shell input text "hello%sworld\%\^\&\*"

        print(device.package_info("com.esbook.reader"))  # dict

        print(device.rotation())  # 屏幕是否转向 0, 1, 2, 3
        device.screenrecord().close_and_pull()  # 录屏

        device.list_packages()  # 包名列表 ["com.example.hello"]
    
    @staticmethod
    def device_list():
        try:
            return [d.serial for d in adb.device_list()]
        except RuntimeError:
            return []

    def state(self):
        """获取设备状态
        Returns:
            Iterator[DeviceEvent], DeviceEvent.status can be one of
            ['device', 'offline', 'unauthorized', 'absent']
        """
        return adb.track_devices().__next__()[-1]

    def model(self) -> str:
        """获取设备型号: ELE-AL00"""
        return self.adb_device.prop.model

    def manufacturer(self) -> str:
        """获取设备制造商: HUAWEI"""
        return self.adb_device.prop.get("ro.product.manufacturer")

    def device_version(self) -> str:
        """获取设备 Android 版本号，如 4.2.2"""
        return self.adb_device.prop.get("ro.build.version.release")

    def sdk_version(self) -> str:
        """获取设备 SDK 版本号，如 26"""
        return self.adb_device.prop.get("ro.build.version.sdk")

    def cpu_version(self):
        """获取cpu基带版本: arm64-v8a"""
        return self.adb_device.prop.get("ro.product.cpu.abi")

    def wifi_state(self):
        """获取WiFi连接状态"""
        return 'enabled' in self.shell('dumpsys wifi | grep ^Wi-Fi')

    def wifi(self) -> str:
        """获取设备当前连接的 Wi-Fi 名称"""
        # output: mWifiInfo SSID: wifi_name, BSSID: 70:f9:6d:b6:a4:81, ...
        output = self.adb_device.shell("dumpsys wifi | grep mWifiInfo")
        name = output.strip().split(",")[0].split()[-1]
        return name

    def ip(self) -> str:
        """Get device IP
        正常情况：inet addr:192.168.123.49  Bcast:192.168.123.255  Mask:255.255.255.0
        无权限情况：ifconfig: ioctl 8927: Permission denied （Android 10）
        """
        output = self.adb_device.shell("ifconfig wlan0")
        ip = re.findall(r'inet\s*addr:(.*?)\s', output, re.DOTALL)
        if not ip:
            return ""
        return ip[0]

    def connect(self, ip=None, port=5555) -> str:
        """基于 WI-FI 连接设备"""
        # TODO：判断手机与PC是否为同一网段，如果不是给出提示
        if not ip:
            ip = self.ip()
            if not ip:
                return '无线连接失败，请输入 IP 地址后重试！'

        # 设置端口
        dev = f"{ip.strip()}:{str(port).strip()}"
        logging.info(f"进行无线连接 ==> {dev}")
        self.shell(f'adb tcpip {port}')
        self.shell(f'adb connect {dev}')

        try:
            assert dev in self.device_list()
            return 'Successful wireless connection.'
        except AssertionError:
            return '无线连接失败，请确保手机和PC网络一致；或检查IP地址是否正确。'

    def device_info_complete(self):
        try:
            ip = self.ip()
        except RuntimeError as e:
            ip = str(e).split(":")[-1]
        device_info_dict = {
            "【设备型号】": f"{self.manufacturer()} | {self.model()}",
            "【设备串号】": self.adb_device.serial,
            "【系统版本】": f"Android {self.device_version()} (API {self.sdk_version()})",
            "【电池状态】": self.battery_info(),
            "【CPU版本】": self.cpu_version(),
            "【屏幕尺寸】": f"{self.window_size()[0]}x{self.window_size()[-1]}",
            "【IP地址】": ip,
        }
        output = ''
        for k, v in device_info_dict.items():
            output += f"{k}: {v}\n"
        return output

    def get_pid(self, pkg_name) -> str:
        """根据包名获取对应的 gid
        args:
            pkg_name -> 应用包名
        usage:
            get_pid("com.android.commands.monkey")  # monkey
        """
        pid_info = self.shell(f"adb -s {self.serial} shell ps | grep -w {pkg_name}")[0]
        if not pid_info:
            return "The process doesn't exist."
        pid = pid_info.split()[1]
        return pid

    def kill_pid(self, pid):
        """TODO：还没测试，杀死应用进程 monkey 进程
        usage:
            kill_pid(154)

        注：杀死系统应用进程需要root权限
        """
        print(self.adb_device.shell(f"kill {pid}"))
        # if self.shell("kill %s" % str(pid)).stdout.read().split(": ")[-1] == "":
        #     return "kill success"
        # else:
        #     return self.shell("kill %s" % str(pid)).stdout.read().split(": ")[-1]

    def pm_list_package(self, options="-3"):
        """输出所有软件包，可根据 options 进行过滤显示
        options:
            -s：进行过滤以仅显示系统软件包。
            -3：进行过滤以仅显示第三方软件包。
            -i：查看软件包的安装程序。
        """
        return self.adb_device.shell(f"pm list packages {options}")

    def pm_path_package(self, package):
        """输出给定 package 的 APK 的路径"""
        return self.adb_device.shell(f"pm path {package}")

    def install(self, apk):
        """安装应用，支持本地路径安装和URL安装"""
        self.shell(f"python3 -m adbutils -s {self.serial} -i {apk}")

    def uninstall(self, package):
        """卸载应用"""
        self.adb_device.uninstall(package)

    def delete_folder(self, folder):
        """删除 sdcard 上的文件夹"""
        self.adb_device.shell(f"rm -rf /sdcard/{folder}")

    def battery_info(self) -> str:
        """获取电池信息
        returns:
            100% (已充满, 29°)
        """
        output = (self.adb_device.shell("dumpsys battery"))

        m = re.compile(r'level: (?P<level>[\d.]+)').search(output)
        level = m.group("level")
        m = re.compile(r'status: (?P<status>[\d.]+)').search(output)
        status = int(m.group("status"))
        m = re.compile(r'temperature: (?P<temperature>[\d.]+)').search(output)
        temperature = int(m.group("temperature")) // 10

        # BATTERY_STATUS_UNKNOWN：未知状态
        # BATTERY_STATUS_CHARGING: 充电状态
        # BATTERY_STATUS_DISCHARGING: 放电状态
        # BATTERY_STATUS_NOT_CHARGING：未充电
        # BATTERY_STATUS_FULL: 充电已满
        status_dict = {
            1: "未知状态",
            2: "充电中",
            3: "放电中",
            4: "未充电",
            5: "已充满"
        }

        battery_info = f"{level}% ({status_dict[status]}, {temperature}°)"
        return battery_info

    def window_size(self):
        """获取设备屏幕分辨率"""
        x, y = self.adb_device.window_size()
        return x, y

    def qr_code(self, text):
        """生成二维码, pip3 install MyQR"""
        # TODO：支持本地路径可以内网访问 ，地址为：http://192.168.125.81:8000/path
        qr_path = systemer.get_abs_path("log", "qr_code.jpg")
        logging.info(f"二维码路径：{qr_path}")
        myqr.run(
            words=text,  # 不支持中文
            # pictures='2.jpg',  # 生成带图的二维码
            # colorized=True,
            save_name=qr_path,
        )
        return qr_path

    def reboot(self):
        """重启设备"""
        self.shell("adb reboot")

    def fast_boot(self):
        """进入fastboot模式"""
        self.shell("adb reboot bootloader")

    def current_app(self):
        """获取当前顶层应用的包名和activity，未命中系统应用，才返回值"""
        package_black_list = [
            "com.miui.home",  # 小米桌面
            "com.huawei.android.launcher"  # 华为桌面
        ]
        current_app = self.adb_device.current_app()
        logging.debug(current_app)
        package = current_app["package"]
        activity = current_app["activity"]

        if package in package_black_list:
            logging.info(f"Current package is System APP ==> {package}")
            return
        return package, activity

    def current_app_reset(self):
        """重置当前应用"""
        pkg_act = self.current_app()
        if not pkg_act:
            return "当前为系统应用，请启动应用后重试"
        package, activity = pkg_act
        self.adb_device.app_clear(package)
        logging.info(f"Reset APP ==> {package}")
        self.adb_device.app_start(package_name=package)
        logging.info(f"Restart APP ==> {package}")

    def app_info(self, pkg_name):
        return self.adb_device.package_info(pkg_name)

    def current_app_info(self):
        """
        return -> dict:
            version_name,
            version_code(去掉了最高和最低支持的 SDK 版本),
            flags,
            first_install_time,
            last_update_time,
            signature
        """
        package, activity = self.current_app()
        package_info = self.adb_device.package_info(package)
        return package_info

    def call_phone(self, number: int):
        """启动拨号器拨打电话"""
        self.adb_device.shell(f"am start -a android.intent.action.CALL -d tel:{number}")

    def get_focused_package_xml(self, save_path):
        file_name = random.randint(10, 99)
        self.shell(f'uiautomator dump /data/local/tmp/{file_name}.xml').communicate()
        self.adb_device(f'pull /data/local/tmp/{file_name}.xml {save_path}').communicate()

    def click_by_percent(self, x, y):
        """通过比例发送触摸事件"""
        if 0.0 < x+y < 2.0:
            wx, wy = self.window_size()
            x *= wx
            y *= wy
            logging.debug(f"点击坐标 ==> ({x}, {y})")
            return self.adb_device.click(x, y)
        else:
            logging.error("click_by_percent(x, y) 预期为小于等于1.0的值，请检查参数")

    def swipe_by_percent(self, sx, sy, ex, ey, duration: float = 1.0):
        """通过比例发送滑动事件，Android 4.4以上可选 duration(ms)"""
        wx, wy = self.window_size()
        sx *= wx
        sy *= wy
        ex *= wx
        ey *= wy
        logging.debug(f"滑动事件 ==> ({sx}, {sy}, {ex}, {ey}, duration={duration})")
        return self.adb_device.swipe(sx, sy, ex, ey, duration=duration)

    def swipe_to_left(self):
        """左滑屏幕"""
        self.swipe_by_percent(0.8, 0.5, 0.2, 0.5)

    def swipe_to_right(self):
        """右滑屏幕"""
        self.swipe_by_percent(0.2, 0.5, 0.8, 0.5)

    def swipe_to_up(self):
        """上滑屏幕"""
        self.swipe_by_percent(0.5, 0.8, 0.5, 0.2)

    def swipe_to_down(self):
        """下滑屏幕"""
        self.swipe_by_percent(0.5, 0.2, 0.5, 0.8)

    def gen_file_name(self, suffix=None):
        """生成文件名称，用于给截图、日志命名"""
        now = datetime.datetime.now()
        str_time = now.strftime('%y%m%d_%H%M%S')
        device = self.manufacturer().lower()
        if not suffix:
            return f"{device}_{str_time}"
        return f"{device}_{str_time}.{suffix}"

    def screenshot(self, pc_path):
        """获取当前设备的截图，导出到指定目录
        usage:
            screenshot("/Users/lan/Downloads/")
        """
        try:
            self.adb_device.shell("mkdir sdcard/screenshot")
        except FileExistsError:
            logging.debug("截图保存位置 ==> sdcard/screenshot/")

        filename = self.gen_file_name("png")
        file = f"/sdcard/screenshot/{filename}"
        self.adb_device.shell(f"/system/bin/screencap -p {file}")
        self.adb_device.sync.pull(file, f"{pc_path}/{filename}")

    def screen_record(self):
        pass

    def app_usage(self, package):
        """获取当前应用 cpu、内存使用占比
        """
        # 安卓top命令仅显示16位包名，这里处理下方便 grep
        pkg = package[:15] + (package[15:] and "+")

        # -n 显示n次top的结果后命令就会退出
        # -d 更新间隔秒数
        # 各参数含义：https://blog.csdn.net/q1183345443/article/details/89920632
        output = self.adb_device.shell(f'top -n 1 -d 1 | grep {pkg}').split()
        logging.debug(f"返回数据 ==> {output}")

        cup, mem = output[8], output[9]
        return cup, mem

    def bigfile(self):
        """填充手机磁盘，直到满"""
        self.adb_device.shell('dd if=/dev/zero of=/mnt/sdcard/bigfile')

    def delete_bigfile(self):
        """删除填满磁盘的大文件"""
        self.adb_device.shell('rm -r /mnt/sdcard/bigfile')

    def backup_apk(self, package, path):
        """备份应用与数据(未测试)
        - all 备份所有 ｜ -f 指定路径 ｜ -system|-nosystem ｜ -shared 备份sd卡
        """
        self.adb_device.adb_output(f'backup -apk {package} -f {path}/mybackup.ab')

    def restore_apk(self, path):
        """恢复应用与数据(未测试)"""
        self.adb_device.adb_output('restore %s' % path)

    def logcat_c(self):
        self.adb_device.shell("logcat --clear")
        logging.info("logcat clear...")

    def logcat(self, filepath, timeout=5, flag=""):
        """获取 adb 日志
        Example:
            flag: '*:E'；过滤错误级别日志
        """
        command = f"{self.adb_path} -s {self.serial} logcat -v time {flag} > {filepath}"
        logging.info(f"==> {command}")
        output = subprocess.Popen(command, shell=True)
        pid = str(output.pid)
        sleep(timeout)
        logging.info(f"adb logcat finished... (PID: {pid}; time: {timeout}s)")

        system = platform.system()
        if system == "Darwin" or "Linux":
            output = subprocess.Popen(f"kill -9 {pid}", shell=True)
        else:
            # Windows 不知道能否生效，没有机器测试
            output = subprocess.Popen(f"taskkill /F /T /PID {pid}", shell=True)
        logging.info(f"Kill adb logcat process! ({system}:{output})")

    def dump_crash_log(self, filepath):
        """转储带有 crash pid 的日志
            filepath:
                日志存储的目录路径
        """
        # log 存储路径
        filename = self.gen_file_name()
        log_filename = f"{filename}.log"
        crash_filename = f"{filename}_crash.log"

        log_filepath = os.path.join(filepath, log_filename)
        crash_filepath = os.path.join(filepath, crash_filename)

        self.logcat(log_filepath, flag='*:E')
        logging.info(f"adb logcat *:E filepath ==> {log_filepath}")

        # 获取设备基础信息
        model = self.model()
        manufacturer = self.manufacturer()
        version = self.device_version()
        sdk_version = self.sdk_version()
        device_info = f"DeviceInfo: {manufacturer} {model} | Android {version} (API {sdk_version})"

        # 根据关键字找到出现 FATAL 错误的 pid
        keyword = "FATAL EXCEPTION: main"
        crash_pid_list = []
        with open(log_filepath, encoding="utf-8") as fr:
            for line in fr.readlines():
                if keyword in line:
                    data = re.findall(r"\d+", line)  # 提取出日志行内所有数字（日期 + PID）
                    pid = data[-1]
                    crash_pid_list.append(pid)

        logging.info(f"Crash PID list >>> {crash_pid_list}")

        # 根据 pid 过滤出错误日志，转储到新的文件内
        if crash_pid_list:
            with open(crash_filepath, "w+", encoding="utf-8") as f:  # 创建转储日志并写入
                f.write(f"{'-' * 50}\n")
                f.write(f"{device_info}\n共出现 {len(crash_pid_list)} 次闪退\n")
                f.write(f"{'-' * 50}\n")
                with open(log_filepath, encoding="utf-8") as f1:  # 读取原始日志
                    for line in f1.readlines():
                        for pid in crash_pid_list:
                            if pid in line:
                                if "FATAL" in line:
                                    f.write("\n# begging of crash --- >>>\n")
                                f.write(line)
            logging.info(f"Crash log path: {crash_filepath}")
            return crash_filename
        else:
            logging.info(f"Not found 'FATAL EXCEPTION: main' in {log_filepath}")
            return log_filename

    def find_process_id(self, pkg_name):
        """根据包名查询进程 PID
        :param pkg_name: Package Name
        :return: USER | PID | NAME
        """
        output = self.adb_device.shell("ps | grep %s" % pkg_name)
        process_list = str(output[1]).split('\n')
        for process in process_list:
            if process.count(pkg_name):
                while process.count('  ') > 0:
                    process = process.replace('  ', ' ')
                process_info = process.split(' ')
                user = process_info[0]
                pid = process_info[1]
                name = process_info[-1]
                return user, pid, name
        return None, None, None

    def find_and_kill_process(self, pkg_name):
        """查找并结束指定进程"""
        user, pid, process_name = self.find_process_id(pkg_name)
        if pid is None:
            return "None such process [ %s ]" % pkg_name
        if user == 'shell':
            kill_cmd = 'kill -9 %s' % pid
        else:
            kill_cmd = 'am force-stop %s' % pkg_name
        return self.shell(kill_cmd)


if __name__ == '__main__':
    pass
