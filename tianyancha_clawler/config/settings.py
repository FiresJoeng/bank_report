ENV = "dev"

# 全局代理控制
GLOBAL_PROXY = True
PROXY_POOL_URL = "http://127.0.0.1:7890"

# MySQL 配置
MysqlConfig = {
    'dev': {
        'host': '',
        'port': 3306,
        'db': '',
        'password': ''
    },
    'test': {

        'username': 'root',
    },
    'prod': {

    }
}
