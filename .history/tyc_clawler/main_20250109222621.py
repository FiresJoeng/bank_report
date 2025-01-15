import os
import csv
import urllib3
import logging
from tyc_client import TycClient
from logging.handlers import TimedRotatingFileHandler

urllib3.disable_warnings()

key = input('键入要搜索的关键字 > ')


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


# 抓取企业信息
def crawler_start():
    # 打印所有结果到日志，并将结果保存到 CSV 文件中
    def __printall(items):
        # 打开 CSV 文件以写入
        with open(f'./csv_files/“{key}”的天眼查搜索结果.csv', mode='w', encoding='utf-8-sig', newline='') as csvfile:
            fieldnames = ['id', 'name', 'short_name', 'representative', 'found_time', 'company_address',
                          'register_address', 'province', 'city', 'district', 'biz_status', 'geoloc',
                          'emails', 'phones', 'contact', 'biz_scope', 'company_type', 'score',
                          'register_capital', 'websites', 'credit_code', 'taxpayer_code',
                          'register_code', 'organization_code', 'tags', 'industry', 'keyword',
                          'logo', 'company_desc', 'financing_round', 'competitions', 'english_name',
                          'register_institute', 'actual_capital', 'used_name', 'staffs',
                          'tax_address', 'taxpayer_bank', 'portraits']  # 表头
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()  # 写入表头

            for elem in items:
                logging.info(elem.__str__())
                writer.writerow(elem.__dict__)  # 写入每个公司的信息

    keys = globals().get('keywords', [])
    for key in keys:
        logging.info(f'[提示] 正在抓取关于“{key}”的结果...')
        companies = TycClient().search(key).companies
        __printall(companies)
    logging.info('[提示] 抓取完毕！')


def crawler_load_keys(keys: list):
    globals().setdefault('keywords', keys)


save_log(f'./logs/“{key}”的天眼查搜索结果.log')

if __name__ == '__main__':
    keys = [key]
    crawler_load_keys(keys)
    crawler_start()
