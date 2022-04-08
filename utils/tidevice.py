"""
使用 tidevice 与 ios 设备进行交互
"""

import logging
import platform
import subprocess
import time
import tidevice
import threading

from config import config
from utils import systemer, common
from utils.common import perf_timer, gen_file_name
from utils.logger import Logger


class TiDevice:

    def __init__(self, device: str = None):
        self.device = f"-u {device}" if device else ""

    def shell(self, args, exec_code=False):
        cmd = f"tidevice {self.device} {args}"
        return systemer.shell(cmd, exec_code=exec_code)

    def version(self):
        """show current version
        :return
            tidevice version 0.1.11
        """
        return self.shell("version")

    def list(self, name=False):
        """show connected iOS devices
        :return
            List of apple devices attached
            7017c3493f7a50f2c90a8ec56f1556b92089732c iPhone
        """
        udid_list = []
        name_list = []
        output = self.shell("list")
        for device in output:
            device = device.split(" ", 1)
            udid_list.append(device[0])
            name_list.append(device[-1])
        if name:
            return name_list
        else:
            return udid_list

    def info(self):
        """show device info
        """
        return self.shell("info")

    def sysinfo(self):
        """show device system info (json)
        """
        return self.shell("sysinfo")

    @perf_timer
    def install(self, path):
        """install application
        """
        return self.shell(f"install {path}", exec_code=True)

    def uninstall(self, pkg_name):
        """uninstall application
        """
        return self.shell(f"uninstall {pkg_name}")

    def launch(self, pkg_name):
        return self.shell(f"launch {pkg_name}")

    def kill(self, pkg_name):
        return self.shell(f"kill {pkg_name}")

    def app_list(self):
        """获取该已安装 APP 列表
        """
        return self.shell("applist")

    def screenshot(self):
        """take screenshot
        """
        self.shell(f"screenshot")

        if len(self.list(name=True)) > 0:
            device = self.list(name=True)[0]
        else:
            device = "iphone"
        device = device.replace(" ", "")
        filename = gen_file_name(before_name=device, suffix="jpg")
        filepath = f"{config.SCREEN_PATH}/{filename}"

        output = systemer.shell(
            f"mv {config.get_abs_path()}/screenshot.jpg {filepath}",
            exec_code=True
        )
        if output[0] == 0:
            logging.info(f"截图保存路径：{filepath}")
            return filepath
        else:
            logging.error("截图失败")
            return

    def reboot(self):
        """reboot device
        """
        self.shell("reboot")

    def parse(self, uri):
        """parse ipa bundle id
        usage:
            tidevice parse [-h] uri
        """
        self.shell(f"parse -h {uri}")

    def watch(self):
        """watch device 监听设备连接
        """
        self.shell("watch")

    def wait_for_device(self):
        """wait for device attached
        """
        self.shell("wait-for-device")

    def xctest(self, args):
        """run XCTest
        usage:
            # 修改监听端口为8200
            xctest("-B com.facebook.wda.WebDriverAgent.Runner -e USB_PORT:8200")
        """
        self.shell(f"xctest {args}")

    def fastbot(self, bundle_id, duration, throttle=300, debug=False):
        """执行 fastbot 测试
        args:
            BUNDLEID: 包名
            dataPort:
            launchenv:
            duration: 执行时间
            throttle: 间隔时间
        """
        fast_runner = "-B bytedance.FastbotRunner.lan.xctrunner"
        _debug = "--debug" if debug else ""
        _bundle_id = f"-e BUNDLEID:{bundle_id}"
        _duration = f"-e duration:{duration}"
        _throttle = f"-e throttle:{throttle}"
        # tidevice xctest -B bytedance.FastbotRunner.lan.xctrunner -e BUNDLEID:com.easou.esbook -e duration:3
        return self.xctest(f"{fast_runner} {_debug} {_bundle_id} {_duration} {_throttle}")

    def logcat(self, bundle_id, duration=10):
        """根据 bundle id 过滤日志"""
        duration = int(duration) * 60

        grep = systemer.get_find_str()

        phone = self.shell("info")[0].split(":")[-1].strip().replace(" ", "_")
        name = common.gen_file_name(before_name=phone, suffix="log")
        log_path = f"{config.LOGCAT_PATH}/{name}"

        command = f"tidevice syslog > {log_path}"
        logging.info(f"tidevice log command ==> {command}")
        output = subprocess.Popen(command, shell=True)

        pid = str(output.pid)
        logging.info(f"tidevice log pid ==> {pid}")

        time.sleep(int(duration))
        logging.info(f"adb logcat finished... ({duration}s)")

        # 杀掉 logcat 进程
        system = platform.system()
        if system == "Darwin" or "Linux":
            subprocess.Popen(f"kill -9 {pid}", shell=True)
            logging.info(f"Kill tidevice logcat process! ({system})")
        else:
            # Windows 不知道能否生效，没有机器测试
            subprocess.Popen(f"taskkill /F /T /PID {pid}", shell=True)
        return log_path

    def fastbot_and_logcat(self, **kwargs):
        """执行fastbot命令，同时输出日志"""
        bundle = kwargs["bundle_id"]
        duration = kwargs["duration"]
        throttle = kwargs["throttle"] if "throttle" in kwargs.keys() else 300

        fastbot = threading.Thread(target=self.fastbot, args=(bundle, duration, throttle))
        logcat = threading.Thread(target=self.logcat, args=(bundle, duration))

        fastbot.start()
        logcat.start()

        fastbot.join()
        logging.info("fastbot thread has ended!")

        logcat.join()
        logging.info("tidevice log thread has ended!")

        logging.info("fastbot_and_logcat() function has ended!")

    def performance(self):
        # TODO: 暂不可用
        # 命令行执行：tidevice perf -B com.lan.fishing
        t = tidevice.Device()
        perf = tidevice.Performance(t)

        def callback(_type: tidevice.DataType, value: dict):
            print("R:", _type.value, value)

        perf.start("com.easou.esbook", callback=callback)
        time.sleep(10)
        perf.stop()

if __name__ == '__main__':
    Logger()
    d = TiDevice()
    # d.fastbot(bundle_id="com.lan.fishing", duration=1)
    # d.fastbot_and_logcat(bundle_id="com.easou.esbook", duration=1)

    d.screenshot()



