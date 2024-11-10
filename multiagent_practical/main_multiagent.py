import pandas as pd
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor
from logger import setup_logger


# 设置日志记录
logger = setup_logger()

# 验证和加载API密钥
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

if not GEMINI_API_KEY or not LANGCHAIN_API_KEY:
    raise ValueError("请确保设置了GEMINI_API_KEY和LANGCHAIN_API_KEY环境变量。")

# 引入企业数据代理、报告生成代理和报告检查代理的相关函数
from multiagent_practical.enterprise_data_agent import (
    read_csv_data,
    read_excel_data,
    merge_dataframes,
    save_to_csv,
    save_to_md,
    create_enterprise_data_agent
)

from multiagent_practical.report_generator import (
    fill_report_template,
    save_report_to_md,
    read_markdown_template,
    create_report_generator_agent
)

from multiagent_practical.report_checker import (
    check_report,
    save_final_report,
    create_report_checker_agent
)

def main_multiagent():
    # 初始化语言模型
    llm = ChatGoogleGenerativeAI(model="gemini-pro", api_key=GEMINI_API_KEY)
    
    # 创建企业数据代理
    enterprise_agent = create_enterprise_data_agent(llm)
    
    # 创建报告生成代理
    report_generator_agent = create_report_generator_agent(llm)
    
    # 创建报告检查代理
    report_checker_agent = create_report_checker_agent(llm)
    
    # 读取企业信息数据
    csv_data = read_csv_data("path/to/enterprise_data.csv")
    excel_data = read_excel_data("path/to/enterprise_data.xlsx")
    
    # 合并数据
    combined_data = merge_dataframes(csv_data, excel_data)
    
    # 保存合并后的数据
    save_to_csv(combined_data, "output/enterprise_data_summary.csv")
    save_to_md(combined_data, "output/enterprise_data_summary.md")
    
    # 读取报告模板
    report_template = read_markdown_template("path/to/your/template.md")
    
    # 生成报告
    filled_report = fill_report_template(combined_data, report_template)
    
    # 保存生成的报告
    save_report_to_md(filled_report, "output/enterprise_report.md")
    
    # 读取报告内容
    report_content = filled_report  # 使用生成的报告内容
    
    # 检查报告
    check_result = check_report(report_content)
    print(check_result)

    # 如果检查通过，保存最终报告
    if "通过" in check_result:
        save_final_report(report_content, "output/final_enterprise_report.md")

# 示例用法
if __name__ == "__main__":
    main_multiagent()
