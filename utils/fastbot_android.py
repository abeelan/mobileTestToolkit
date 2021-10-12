"""
@lan

# 基础配置
max.config

max.schema
max.strings 随机输入字符串配置
max.path.actions 自定义事件序列；场景覆盖不全，通过人工配置到达fastbot遍历不到的场景
max.widget.black 屏蔽控件或区域
max.tree.pruning 树剪枝屏蔽控件；效率更高，通常与黑控件同时屏蔽

# 黑白名单不能同时配置，非黑即白
awl.strings 白名单配置
abl.strings 黑名单配置

TODO: 与 u2 冲突，都需要 uiautomator 服务，启停 u2 的功能，后续看是否需要添加
"""
import os
import logging

from adbutils import adb

from config import config
from utils import systemer
from utils import logger


class FastbotAndroid:

    def __init__(self, package, duration, serial=None, throttle=300, output="fastbot"):

        self.pkg_name = f"-p {package}" if package else None  # 遍历APP的包名
        self.duration = f"--running-minutes {duration}" if duration else None  # 遍历时长，单位：分钟
        self.throttle = f"--throttle {throttle}" if throttle else None  # 遍历事件频率，建议为500-800，单位：毫秒
        self.output = output
        self.output_dir = f"--output-directory /sdcard/{output}" if output else None  # log/crash 另存目录
        # /sdcard/crash-dump.log  # crash default path
        # /sdcard/oom-traces.log  # OOM default path

        self.awl = f"--act-whitelist-file /sdcard/awl.strings"

        self.adb = adb.device(serial=serial)  # 多个设备需要指定设备号
        self.adb.shell(f"rm -rf /sdcard/{output}")


    def check_rely(self):
        # 推送所有依赖到设备
        jar = ["monkeyq.jar", "framework.jar"]
        conf = [
            "max.config",
            "max.strings",  # 随机输入字符配置
            "awl.strings",  # 白名单配置  --act-whitelist-file
            # "abl.strings",  # 黑名单配置  --act-blacklist-file
            "max.widget.black",
            "max.tree.pruning",
            "max.xpath.actions",
        ]

        jar_path = config.FASTBOT_PATH

        for i in jar:
            name = self.adb.shell(f"ls sdcard | grep '{i}'")
            if not name:
                self.adb.push(f"{jar_path}/{i}", "/sdcard/")
                logging.info(f"adb push >>> sdcard/{i}")
        for i in conf:
            self.adb.push(f"{jar_path}/{i}", "/sdcard/")
            logging.info(f"adb push >>> sdcard/{i}")

        # 清空设备日志；缓冲区自动清理，不清理也行
        # self.adb.shell("logcat --clear")

    def set_keyboard(self, name="ADBKeyboard"):
        """自定义输入法 + 屏蔽输入栏"""
        if name == "ADBKeyboard":
            if "com.android.adbkeyboard" not in self.adb.list_packages():
                apk = os.path.join(config.FASTBOT_PATH, "ADBKeyBoard.apk")
                self.adb.install(apk)
            self.adb.shell("ime set com.android.adbkeyboard/.AdbIME")  # 设置为 adbKeyboard 输入法
        else:
            # TODO: 这里的输入法是华为的，可能不兼容其他厂商，先这样吧
            self.adb.shell("ime set com.baidu.input_huawei/.ImeService")  # 设置为百度输入法

    def exec_fastbot(self):
        # 执行入口（固定不变)
        jar = "CLASSPATH=/sdcard/monkeyq.jar:/sdcard/framework.jar"  # jar 包路径
        exec = "exec app_process /system/bin com.android.commands.monkey.Monkey"  # 执行入口
        mode = "--agent robot"  # 遍历模式，无需更改
        bug_report = "--bugreport"  # 崩溃时保存 bug report log
        log_level = "-v -v -v"

        """
        monkey 参数：
            https://developer.android.com/studio/test/monkey
            https://www.cnblogs.com/sunzzc/p/13185573.html
        
        # 下面是 maxim 参数
        --pct-rotation 0  # 取消旋转屏幕；在这里设置后依然见过出现屏幕旋转情况
        --pct-back 5      # 设置 BACK 占比，默认占比 10%
        --pct-touch 100   # 设置点击比例
        --pct-reset 0     # fastbot不支持，别设置，会报错
        """
        monkey_params = "--pct-rotation 0 --pct-motion 50"

        cmd = f"{jar} {exec} {self.pkg_name} {mode} {monkey_params} " \
              f"{self.awl} {self.duration} {self.throttle} {log_level} {self.output_dir}"

        # utils shell
        systemer.shell(f"adb shell {cmd}")

    def log_dump(self):
        """如果出现闪退，则将日志拉到 PC"""
        crash = self.adb.shell(f"ls sdcard/{self.output} | grep -i 'crash'")
        oom = self.adb.shell(f"ls sdcard/{self.output} | grep -i 'oom'")

        if crash:
            logging.info(f"Crash log: sdcard/{crash}")
            # self.adb.sync.pull(crash, config.LOGCAT_PATH)
            logging.info(f"已拉取: {config.LOGCAT_PATH}")
        if oom:
            logging.info(f"Oom log: sdcard/{oom}")
            # self.adb.sync.pull(oom, config.LOGCAT_PATH)
            logging.info(f"已拉取: {config.LOGCAT_PATH}")

    def run(self):
        # 检测运行环境
        self.check_rely()
        # 设置adbKeyboard
        self.set_keyboard()
        # 执行 fastbot
        self.exec_fastbot()
        # 拉取日志
        self.log_dump()

if __name__ == '__main__':
    logger.Logger()
    fastbot = FastbotAndroid(package="com.esbook.reader", duration=1)
    fastbot.run()

