import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def get_element_text(soup, selector, class_name):
    """通用函数，用于提取元素文本"""
    element = soup.find(selector, class_name)
    return element.text.strip() if element else None

def search_and_extract_company_info(company_name):
    search_url = f"https://www.qizhidao.com/check?searchKey={company_name}&tagNum=0&scPageTitle=PC%E7%AB%99%E4%B8%BB%E7%AB%99&searchModeType=8&fromRoutePage=check&businessSourceDzlQuery="
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 等待页面加载
    time.sleep(5)

    # 使用通用函数提取信息
    company_info = {
        '统一社会信用代码': get_element_text(soup, 'span', {'class': 'copy-text'}),
        '曾用名': get_element_text(soup, 'span', {'class': 'value b-b0 b-t0 bgfff d_f_box'}),
        '法定代表人': get_element_text(soup, 'a', {'class': 'linkTextCommon'}),
        '注册资本': get_element_text(soup, 'span', {'class': 'test'}),
        '组织机构代码': get_element_text(soup, 'span', {'class': 'copy-text'}),
    }

    # 将信息保存到DataFrame
    df = pd.DataFrame([company_info])

    # 保存到Excel文件
    
    file_path = f"tyc_clawler\\{company_name}_信息表.csv"
    df.to_csv(file_path, index=False)

# 调用函数
search_and_extract_company_info("财付通支付科技有限公司")
