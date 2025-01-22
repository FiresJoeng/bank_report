import requests
from bs4 import BeautifulSoup
import time

# 目标网页的URL
url = 'https://www.gsxt.gov.cn/index.html'

# 最大重试次数
max_retries = 3
retry_count = 0

while retry_count < max_retries:
    try:
        # 发送HTTP请求
        response = requests.get(url)
        response.encoding = 'utf-8'  # 根据网页的编码方式进行设置

        # 检查请求是否成功
        if response.status_code == 200:
            # 使用BeautifulSoup解析HTML内容
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取网页的标题
            title = soup.find('title').get_text()
            
            # 打印标题
            print(f'网页标题为: {title}')
            break  # 请求成功，跳出循环
        else:
            print(f'请求失败，错误码：{response.status_code}')
            retry_count += 1
            time.sleep(5)  # 等待5秒后重试
    except Exception as e:
        print(f'发生异常: {e}')
        retry_count += 1
        time.sleep(5)  # 等待5秒后重试

if retry_count == max_retries:
    print('达到最大重试次数，请求失败')
