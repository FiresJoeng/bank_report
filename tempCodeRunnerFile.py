# Todo:
# 1. 绕过异常流量捕获
# 2. 报错处理

# import modules
import requests
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# 获取搜索词
key = input('搜索词 > ')
qcc_url = f'https://www.qcc.com/web/search?key={key}'

# 设置Chrome选项
chrome_options = Options()
chrome_options.add_argument('--start-maximized')  # 最大化窗口
# chrome_options.add_argument('--headless')  # 无头模式（登录时需要注释掉）

# 初始化浏览器
driver = webdriver.Chrome(options=chrome_options)

# 打开登录页面
print("请在浏览器中完成登录...")
driver.get(qcc_url)

# 等待用户手动登录
input("登录完成后按回车继续...")

# 获取cookies
cookies = driver.get_cookies()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 构建requests的cookies
cookies_dict = {}
for cookie in cookies:
    cookies_dict[cookie['name']] = cookie['value']

# 关闭浏览器
driver.quit()

# 使用requests获取搜索页面内容
response = requests.get(qcc_url, headers=headers, cookies=cookies_dict)
html_content = response.text

# 使用正则表达式匹配内容
pattern = r'(?:"[^"]*")?<em>' + re.escape(key) + r'</em>(?:"[^"]*")?'
matches = re.findall(pattern, html_content)

# 打印匹配结果
for match in matches:
    print(match)
