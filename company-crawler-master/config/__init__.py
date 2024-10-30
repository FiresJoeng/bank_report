
"""
:author: lubosin
:date: 03/28/2019
"""
import logging as log
import sys

import config
from config.settings import *

sys.path.append("..")


class MysqlEnviron:
    CONFIG = MysqlConfig.get(ENV)
    if not CONFIG:
        log.error('no active environment')
        exit(0)

    @property
    def host(self):
        return self.CONFIG.get('host')

    @property
    def port(self):
        return self.CONFIG.get('port')

    @property
    def database(self):
        return self.CONFIG.get('db')

    @property
    def username(self):
        return self.CONFIG.get('username')

    @property
    def password(self):
        return self.CONFIG.get('password')


