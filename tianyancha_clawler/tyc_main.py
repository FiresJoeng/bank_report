import os
import urllib3
import logging
from tianyancha_client import TycClient
from db.mysql_connector import *
from logging.handlers import TimedRotatingFileHandler

urllib3.disable_warnings()

key = input("键入要搜索的关键字 > ")


class UTF8TimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stream = self._open()

    def _open(self):
        # 以 UTF-8 编码打开文件
        return open(self.baseFilename, self.mode, encoding='utf-8')


def save_log(filename):
    os.getcwd()

    # Vars
    handler = UTF8TimedRotatingFileHandler(filename, 'D', 1, 7)
    console = logging.StreamHandler()
    logger = logging.getLogger()
    fmt = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
    formatter = logging.Formatter(fmt=fmt, datefmt='%m/%d/%Y %H:%M:%S')

    # UTF8TimedRotatingFileHandler()
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)

    # logging.StreamHandler()
    console.setFormatter(formatter)
    console.setLevel(logging.INFO)

    # logger.GetLogger()
    logger.addHandler(console)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def crawler_start():
    # 入口函数
    def __printall(items):
        for elem in items:
            logging.info(elem.__str__())

    keys = globals().get('keywords', [])
    for key in keys:
        logging.info(f'[提示] 正在抓取关于“{key}”的结果...')
        companies = TycClient().search(key).companies
        # 写入db
        # insert_company(companies)
        __printall(companies)
    logging.info("completed")


def crawler_load_keys(keys: list):
    globals().setdefault('keywords', keys)

save_log(f'./logs/“{key}”的天眼查搜索结果.log')

if __name__ == '__main__':
    keys = [key]
    crawler_load_keys(keys)
    crawler_start()
    client = TycClient()
    client.save_to_csv(f'./csv_files/“{key}”的天眼查搜索结果.csv')
