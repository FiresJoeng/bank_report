import os
from langchain_google_genai import ChatGoogleGenerativeAI
from util.logger import setup_logger
from agents.enterprise_data_agent import create_enterprise_data_agent
from agents.report_generator import create_report_generator_agent
from agents.report_checker import create_report_checker_agent

# 设置日志记录
logger = setup_logger()

# 验证和加载API密钥
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

if not GEMINI_API_KEY or not LANGCHAIN_API_KEY:
    raise ValueError("请确保设置了GEMINI_API_KEY和LANGCHAIN_API_KEY环境变量。")

# 设置代理
os.environ['https_proxy'] = 'http://127.0.0.1:7890'
os.environ['http_proxy'] = 'http://127.0.0.1:7890'


def main():
    # 初始化语言模型
    llm = ChatGoogleGenerativeAI(model="gemini-pro", api_key=GEMINI_API_KEY)

    # 创建代理
    data_agent = create_enterprise_data_agent(llm)
    report_agent = create_report_generator_agent(llm)
    checker_agent = create_report_checker_agent(llm)

    # 读取企业数据
    enterprise_data = data_agent.read_csv_data("path/to/enterprise_data.csv")
    if enterprise_data.empty:
        logger.error("未能读取企业数据，程序终止。")
        return

    # 读取报告模板
    try:
        report_template = report_agent.read_markdown_template(
            "path/to/template.md")
    except FileNotFoundError:
        logger.error("报告模板文件未找到，请检查路径。")
        return

    # 填充报告
    filled_report = report_agent.fill_report_template(
        enterprise_data, report_template, llm)

    # 检查报告
    check_result = checker_agent.check_report(filled_report)
    print(check_result)

    # 如果检查通过，保存最终报告
    if "通过" in check_result:
        report_agent.save_report_to_md(
            filled_report, "output/final_enterprise_report.md")


if __name__ == "__main__":
    main()
