"""
@Time   : 2020/8/6 下午12:37
@Author : lan
@Mail   : lanzy.nice@gmail.com
@Desc   : logging 模块初始化
"""

import os
import time
import logging
import colorlog
from logging.handlers import RotatingFileHandler


class Logger:
    """初始化日志记录器
    usage：
        # 默认记录器是 root，会输出到控制台且写入到日志文件 output.log
        >>> logger1 = Logger().logger
        >>> logger1.debug("this is debug message")
        >>> import logging
        >>> logging.warning("this is warning message")

        # 创建记录器 test，会输出到控制台且写入到日志文件 test.log
        # 可以设置 level 级别
        >>> logger2 = Logger("test", level=logging.INFO).logger
        >>> logger2.error("this is error message")

        # 仅在控制台输出
        >>> logger3 = Logger(Logger.CONSOLE).logger
        >>> logger3.info("this is info message")
    """
    CONSOLE = "console"

    __date_fmt = "%y%m%d %H:%M:%S"
    __fmt = "[ %(levelname)1.1s %(asctime)s %(module)s:%(lineno)d ] %(message)s"
    __color_fmt = '%(log_color)s[ %(levelname)1.1s %(asctime)s %(module)s:%(lineno)d ]%(black)s %(message)s'
    __filepath = os.path.dirname(os.path.dirname(__file__)) + "/"

    def __init__(self, filename=None, level=logging.INFO):
        """初始化 Logger"""

        """
        1. 创建记录器
        """
        self.logger = logging.getLogger(filename)  # 默认 ROOT
        self.logger.setLevel(level)

        """
        2. 定义输出格式
        """
        self.__colors_config = {
            'DEBUG': 'cyan',
            'INFO': 'blue',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }

        self.__datetime_fmt = "%y%m%d %H:%M:%S"
        self.__fmt_begin = "[ %(levelname)1.1s %(asctime)s %(module)s:%(lineno)d ]"
        self.__fmt_message = "%(message)s"
        self.__log_fmt = f"{self.__fmt_begin} {self.__fmt_message}"
        self.__log_colors_fmt = f'%(log_color)s{self.__fmt_begin}%(black)s {self.__fmt_message}'

        formatter = logging.Formatter(
            fmt=self.__log_fmt,
            datefmt=self.__datetime_fmt
        )
        color_formatter = colorlog.ColoredFormatter(
            fmt=self.__color_fmt,
            datefmt=self.__datetime_fmt,
            log_colors=self.__colors_config
        )

        """
        3. 创建处理器并关联输出格式
        # 如果没有给处理器指定日志级别，将使用记录器的日志级别
        # 如果没有给记录器指定日志级别，那么会使用默认「warning」级别
        # 如果两者都设置了指定日志级别，那么以记录器的级别为准
        """
        # 3.1 创建 控制台输出 处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(color_formatter)

        # 3.2 创建 文件输出 处理器
        __log_abs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "log")
        day_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))  # 2020-04-20
        __filename = f"{day_time}.log" if not filename or filename == Logger.CONSOLE \
            else f"{filename}_{day_time}.log"
        __file_path = os.path.join(__log_abs_path, __filename)
        if not os.path.exists(__log_abs_path):
            os.mkdir(__log_abs_path)

        # file_handler = logging.FileHandler(filename=__file_path)
        file_handler = RotatingFileHandler(
            filename=__file_path,
            mode="a+",
            maxBytes=1024*1024*5,  # 5M
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        """
        4. 记录器关联处理器
        """
        if filename == "console":
            self.logger.addHandler(console_handler)
        else:
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)

        """
        5. 创建 & 关联 过滤器
        # 仅输出设置的记录器下的日志，也可以对处理器进行设置过滤器
        # 这里设置为 test，就不会再输出日志了，因为只输出名为 "test" 记录器的日志
        """
        # filter_app = logging.Filter("test")
        # self.logger.addFil(filter_app)



if __name__ == '__main__':
    Logger()
    # 不会输出 DEBUG 日志，默认从 INFO 开始
    logging.debug("this is debug message")
    logging.info("this is info message")
    logging.warning("this is warning message")
    logging.error("this is error message")
    logging.critical("this is critical message")

    # 会打印出 debug 日志
    # Logger(level=logging.DEBUG)
    # logging.debug("this is debug message")

    # 创建新的记录器，输出日志到 output1.log 内
    # logging = Logger("output1").logger
    # logging.info("this is test output1 log")


