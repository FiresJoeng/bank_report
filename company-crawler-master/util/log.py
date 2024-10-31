import logging
import os
from logging.handlers import TimedRotatingFileHandler


def set_file(filename):
    """
    设置日志文件并配置日志记录器。

    参数:
        filename (str): 日志文件名。

    返回:
        None

    示例:
        >>> set_file('test.log')
    """
    # 获取根日志记录器
    logger = logging.getLogger()
    # 获取当前工作目录
    os.getcwd()
    # 创建一个按天滚动的文件日志处理器
    handler = TimedRotatingFileHandler(filename, 'D', 1, 7)
    # 设置日志格式化字符串
    fmt = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
    formatter = logging.Formatter(fmt=fmt, datefmt='%m/%d/%Y %H:%M:%S')

    # 设置文件日志处理器的格式化器
    handler.setFormatter(formatter)
    # 设置文件日志处理器的日志级别
    handler.setLevel(logging.INFO)
    # 创建一个控制台日志处理器
    console = logging.StreamHandler()
    # 设置控制台日志处理器的格式化器
    console.setFormatter(formatter)
    # 设置控制台日志处理器的日志级别
    console.setLevel(logging.INFO)
    # 将文件日志处理器添加到根日志记录器a
    logger.addHandler(console)
    # 将控制台日志处理器添加到根日志记录器
    logger.addHandler(handler)
    # 设置根日志记录器的日志级别
    logger.setLevel(logging.INFO)
