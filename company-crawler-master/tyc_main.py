from tianyancha import crawler
from util import log
import urllib3
urllib3.disable_warnings()


key = input("键入要搜索的关键字 > ")
log.set_file("./logs/tianyancha.log")


if __name__ == '__main__':
    keys = [key]
    crawler.load_keys(keys)
    crawler.start()
