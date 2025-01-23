import requests
from bs4 import BeautifulSoup
import pandas as pd

# 定义一个函数来执行整个流程
def search_and_extract_company_info(company_name):
    # 搜索企业并获取页面内容
    search_url = f"https://www.qizhidao.com/check?searchKey={company_name}&tagNum=0&scPageTitle=PC%E7%AB%99%E4%B8%BB%E7%AB%99&searchModeType=8&fromRoutePage=check&businessSourceDzlQuery="
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 获取统一社会信用代码
    # credit_code = soup.find('span', {'class': 'copy-text'}).text

    # 获取曾用名
    former_name = soup.find('span', {'class': 'value b-b0 b-t0 bgfff d_f_box'}).text

    # 获取法定代表人
    legal_representative = soup.find('a', {'class': 'linkTextCommon'}).text

    # 获取注册资本
    registered_capital = soup.find('span', {'class': 'test'}).text

    # 获取组织机构代码
    organization_code = soup.find('span', {'class': 'copy-text'}).text

    # 将信息保存到DataFrame
    company_info = pd.DataFrame({
        '公司名称': [company_name],
        # '统一社会信用代码': [credit_code],
        '曾用名': [former_name],
        '法定代表人': [legal_representative],
        '注册资本': [registered_capital],
        '组织机构代码': [organization_code]
    })

    # 保存到Excel文件
    file_path = f"tyc_clawler\\{company_name}_信息表.xlsx"
    company_info.to_excel(file_path, index=False)

# 调用函数，传入企业名称
search_and_extract_company_info("企业名称")
