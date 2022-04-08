"""
@Time   : 2020/6/18 11:15 上午
@Author : lan
@Mail   : lanzy.nice@gmail.com
@Desc   :
"""
import os
import re
import sys
import time
from threading import Thread
from xml.dom import minidom

import yaml
import ctypes
import socket
import logging
import inspect
import datetime
import linecache

from MyQR import myqr

from config import config
from utils import systemer


class MyThread(Thread):

    def __init__(self,func,args=()):
        super(MyThread,self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            # 如果子线程不使用join方法，此处可能会报没有self.result的错误
            return self.result
        except Exception:
            return None


def get_pc_ip():
    """获取电脑的 IP 地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def sleep(secs):
    return time.sleep(secs)


def get_current_time(t=0):
    """
    四种输出格式：t=0 默认输出格式：2016-07-19 18:54:18.282000
    t=3 返回当前日期：2018-04-01
    :param t: 入参
    :return: 按格式返回当前系统时间戳
    """
    curr_time = datetime.datetime.now()
    if t == 0:
        return curr_time  # 格式：2016-07-19 18:54:18.282000
    elif t == 1:
        return curr_time.strftime('%Y-%m-%d %H:%M:%S')  # 格式：2016-07-19 18:11:04
    elif t == 2:
        return curr_time.strftime('%Y%m%d-%H%M%S')  # 格式：20160719-181104
    elif t == 3:
        return curr_time.strftime('%Y-%m-%d')  # 格式：2016-07-19
    else:
        print("[warning]: no format matches...pls check!")


def time_diff(start_time, stop_time):
    """
    求时间差用datetime模块，不能用time()模块，且不能使用格式化的输出
    start_time和stop_time需datetime.datetime.now()获取
    """
    t = (stop_time - start_time)
    time_day = t.days
    s_time = t.seconds
    ms_time = t.microseconds / 1000000
    used_time = int(s_time + ms_time)
    time_hour = used_time / 60 / 60
    time_minute = (used_time - time_hour * 3600) / 60
    time_second = used_time - time_hour * 3600 - time_minute * 60
    time_microsecond = (t.microseconds - t.microseconds / 1000000) / 1000
    ret_str = "%d天%d小时%d分%d秒%d毫秒" % (time_day, time_hour, time_minute, time_second, time_microsecond)
    return ret_str


def create_timestamp_folder(path='', t=3):
    """
    create timestamp folder and return the folder name
    :param path: 默认时，在当前目录创建
    :param t:
    :return: folder name
    """
    folder_name = path + get_current_time(t)
    # check file is exists or not.
    try:
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)
    except Exception as e:
        print(str(e) + "  Error : Failed to create folder...")
    return folder_name


def gen_file_name(before_name=None, suffix=None):
    """生成文件名称，用于给截图、日志命名"""
    now = datetime.datetime.now()
    str_time = now.strftime('%y%m%d_%H%M%S')
    before = before_name.lower()
    if not suffix:
        return f"{before}_{str_time}"
    return f"{before}_{str_time}.{suffix}"


def parse_yml(file_path):
    """解析给定路径的yml文件并返回内容"""
    f = open(file_path)
    yam_content = yaml.load(f)
    f.close()
    return yam_content


def get_yml_value(file_path, section):
    """
    解析给定路径的yml文件并返回内容具体选择区域的section列表数据
    """
    f = open(file_path)
    yml_value = yaml.load(f)[section]
    f.close()
    return yml_value


def open_xml_file(file_name, first_node, second_node):
    """ 读取xml文件 """
    # 使用minidom打开文档
    # 从内存空间为该文件申请内存
    xml_file = minidom.parse("../config/" + file_name)
    # 一级标签（标签可重复，加角标区分）
    one_node = xml_file.getElementsByTagName(first_node)[0]
    # 二级标签
    two_node = one_node.getElementsByTagName(second_node)[0].childNodes[0].nodeValues
    return two_node


def __line__(file=''):
    """获取调用处的文件名称，代码行数
    ex：
        call method: __line__(__file__)
    """
    try:
        raise Exception
    except:
        f = sys.exc_info()[2].tb_frame.f_back
    func_name = str(f.f_code.co_name)+'()'
    line = str(f.f_lineno)
    if file == '':
        return "[%s | %s]" % (func_name, line)
    else:
        return "[%s | %s | %s]" % (file, func_name, line)


def modify_config(keyword: str, expected: str):
    """
    修改配置文件中关键字所在行的内容
    :param keyword: 查找配置文件的关键字
    :param expected: expected result 想替换的预期字符串（替换行）
    :return:
    """
    # 添加以下代码目的是: 将当前项目目录临时添加到环境变量
    cur_path = os.path.abspath(os.path.dirname(__file__))
    root_path = os.path.split(cur_path)[0]
    sys.path.append(root_path)
    with open('./config/config.py', 'r+') as f, open('./config/config1.py', 'w') as fw:
        for line in f:
            if keyword in line:
                line = '%s\n' % expected
            fw.write(line)
    os.remove('./config/config.py')
    os.rename('./config/config1.py', './config/config.py')


def _async_raise(tid, exc_type):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exc_type):
        exc_type = type(exc_type)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exc_type))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    """杀死子线程"""
    _async_raise(thread.ident, SystemExit)


def get_line_context(file_path, line_num):
    """读取文件某行"""
    return linecache.getline(file_path, line_num).strip()


def perf_timer(func):
    def call_func(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        end_time = time.time()
        total_time = end_time - start_time
        logging.info(
            f"[{func.__name__}] Time elapsed：{int(total_time // 60)}min & {total_time % 60:.2f}s！"
        )
    return call_func


def qr_code(text):
    """生成二维码, pip3 install MyQR"""
    qr_path = systemer.get_abs_path("log", "qr_code.jpg")
    logging.info(f"二维码路径：{qr_path}")
    myqr.run(
        words=text,  # 不支持中文
        # pictures='2.jpg',  # 生成带图的二维码
        # colorized=True,
        save_name=qr_path,
    )
    return qr_path


if __name__ == "__main__":
    pass
    # user_info = get_yml_value('../config/data.yml', 'phone_login')
    # print(user_info)
    # print(user_info[0]['phone1'])
    # print(create_timestamp_folder())
    # print("oscar test001")
    # __line__(__file__)
    get_pc_ip()




