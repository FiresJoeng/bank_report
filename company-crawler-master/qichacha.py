"""
:author: lubosson
:date: 2019-04-16
:desc:
"""
from qichacha import crawler as QccCrawler
from util import log
import urllib3
import os

os.makedirs('./logs', exist_ok=True)

urllib3.disable_warnings()


log.set_file("./logs/qichacha.log")
app = QccCrawler

if __name__ == '__main__':
    keys = ['腾讯']
    app.load_keys(keys)
    app.start()

