# -*- coding: utf8 -*-
"""
Created on 2019-08-17
"""
import os
import socket
import logging
import platform
import subprocess


def get_system() -> str:
    """获取当前系统名称
    Darwin | Windows | Linux
    """
    return platform.system()


def get_host_ip():
    """查询本机(PC) IP 地址
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def get_find_str() -> str:
    """根据系统类型选择 过滤 命令
    """
    system = get_system()
    return 'findstr' if system == 'Windows' else 'grep'


def shell(command, exec_code=False):
    """exec shell command.
    usage:
        >>> shell("ping www.baidu.com")  # doctest: +SKIP
        ...
        >>> shell("echo 'hello'", exec_code=True)
        (0, ['hello'])
    """
    if not isinstance(command, str):
        raise TypeError("command args type invalid", type(command))

    proc = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        shell=True,
        encoding="utf-8"
    )

    proc.stdin.write(command)
    proc.stdin.flush()
    proc.stdin.close()

    logging.info(f"[ shell ] {command}")

    # Real time stdout of subprocess
    stdout = []
    while True:
        line = proc.stdout.readline().strip()
        if line == "" and proc.poll() is not None:
            break
        stdout.append(line)
        logging.info(line)

    # Wait for child process and get return code
    # 0: 正常结束; 1: sleep; 2: 子进程不存在; -1/5: kill; None: 正在运行
    return_code = proc.wait()
    if not exec_code:
        return stdout
    return return_code, stdout


def get_abs_path(*args):
    """get current project abs path.
    usage:
        >>> get_abs_path()
        /Users/lan/workspace/pythonProject/toolkit
        >>> get_abs_path("log")
        /Users/lan/workspace/pythonProject/toolkit/log
    """
    abs_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if not args:
        return abs_path
    for path in args:
        abs_path = os.path.join(abs_path, path)
    return abs_path


def mkdir(dir_path):
    """创建目录"""
    # 去除首位空格
    _dir = dir_path.strip().rstrip("\\").rstrip("/")
    logging.info(f"初始化目录: {dir_path}")

    # 判断路径是否存在
    is_exists = os.path.exists(_dir)

    if not is_exists:
        try:
            os.makedirs(_dir)
            logging.info("Directory creation success：%s" % _dir)
        except Exception as e:
            logging.error("Directory creation failed：%s" % e)
    else:
        # 如果目录存在则不创建，并提示目录已存在
        logging.info("Directory already exists：%s" % str(_dir))


def touch_file(file_path, content):
    """创建文件并写入内容，当文件存在时
    """
    if os.path.exists(file_path):
        logging.info("{} is exists!".format(file_path))
        return
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def get_latest_file(dir):
    """获取当前目录下最新的文件"""
    file_list = os.listdir(dir)

    if not file_list:
        return

    file_list.sort(
        key=lambda fn: os.path.getmtime(os.path.join(dir, fn))
        if not os.path.isdir(os.path.join(dir, fn)) else 0
    )
    filename = os.path.join(dir, file_list[-1])
    return filename

def open_path(dir):
    """打开当前目录"""
    if not dir:
        return False

    if get_system() == "Windows":
        cmd = f"start explorer {dir}"
    else:
        cmd = f"open {dir}"

    shell(cmd)
    return True


if __name__ == '__main__':
    # print(get_abs_path())
    pass
