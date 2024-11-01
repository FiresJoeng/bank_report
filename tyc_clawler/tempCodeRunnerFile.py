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
        with open(f'./csv_files/“{key}”的天眼查搜索结果.csv', mode='w', encoding='utf-8', newline='') as csvfile:
            fieldnames = ['编号（id）',
                          '名称（name）',
                          '简称（short_name）',
                          '法人代表（representative）',
                          '成立时间（found_time）',
                          '公司地址（company_address）',
                          '注册地址（register_address）',
                          '省份（province）',
                          '城市（city）',
                          '区县（district）',
                          '经营状态（biz_status）',
                          '地理位置（geoloc）',
                          '电子邮件（emails）',
                          '联系电话（phones）',
                          '联系人（contact）',
                          '经营范围（biz_scope）',
                          '公司类型（company_type）',
                          '评分（score）',
                          '注册资本（register_capital）',
                          '网站（websites）',
                          '统一社会信用代码（credit_code）',
                          '纳税人识别号（taxpayer_code）',
                          '工商注册号（register_code）',
                          '组织机构代码（organization_code）',
                          '标签（tags）',
                          '行业（industry）',
                          '关键词（keyword）',
                          '标志（logo）',
                          '公司简介（company_desc）',
                          '融资轮次（financing_round）',
                          '竞争对手（competitions）',
                          '英文名称（english_name）',
                          '登记机关（register_institute）',
                          '实缴资本（actual_capital）',
                          '曾用名（used_name）',
                          '员工人数（staffs）',
                          '税务地址（tax_address）',
                          '纳税人开户银行（taxpayer_bank）',
                          '公司肖像（portraits）']  # 表头
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
