import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

def get_element_text(soup, selector, class_name):
    """通用函数，用于提取元素文本"""
    element = soup.find(selector, class_=class_name)  # 使用 class_=class_name 以符合BeautifulSoup的API
    return element.text.strip() if element else None

def search_and_extract_company_info(company_name):
    search_url = f"https://www.qizhidao.com/check?searchKey={company_name}&tagNum=0&scPageTitle=PC%E7%AB%99%E4%B8%BB%E7%AB%99&searchModeType=8&fromRoutePage=check&businessSourceDzlQuery="
    try:
        response = requests.get(search_url)
        response.raise_for_status()  # 检查请求是否成功
    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    company_info = {
        '统一社会信用代码': get_element_text(soup, 'span', 'copy-text'),
        '曾用名': get_element_text(soup, 'span', 'value b-b0 b-t0 bgfff d_f_box'),  # 注意：多个类名应以空格分隔，但这里可能需要根据实际HTML调整
        '法定代表人': get_element_text(soup, 'a', 'linkTextCommon'),
        '注册资本': get_element_text(soup, 'span', 'test'),  # 'test' 类名看起来不具体，可能需要调整
        '组织机构代码': get_element_text(soup, 'span', 'copy-text'),
    }

    # 清理字典中的None值（可选）
    # company_info = {k: v for k, v in company_info.items() if v is not None}

    # 将信息保存到DataFrame
    df = pd.DataFrame([company_info])

    # 保存到Excel文件,根据公司名称创建文件名
    base_directory = './output'  # 定义输出目录
    os.makedirs(base_directory, exist_ok=True)  # 确保目录存在
    filename = f"{company_name}.csv"
    filepath = os.path.join(base_directory, filename)
    df.to_csv(filepath, index=False)

# 调用函数
search_and_extract_company_info("财付通支付科技有限公司")