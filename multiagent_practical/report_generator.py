import pandas as pd
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor
from langchain.tools import tool
from logger import setup_logger

# 设置日志记录
logger = setup_logger()

# 验证和加载API密钥
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

if not GEMINI_API_KEY or not LANGCHAIN_API_KEY:
    raise ValueError("请确保设置了GEMINI_API_KEY和LANGCHAIN_API_KEY环境变量。")

@tool
def fill_report_template(data: pd.DataFrame, template: str) -> str:
    """
    根据企业信息总表填充调查报告模板。
    
    Args:
        data (pd.DataFrame): 企业信息总表。
        template (str): 报告模板。
    
    Returns:
        str: 填充后的报告内容。
    """
    try:
        # 提取相关信息
        company_name = data.get('公司名称', [''])[0]
        registration_number = data.get('注册号', [''])[0]
        address = data.get('地址', [''])[0]
        contact_person = data.get('联系人', [''])[0]
        contact_number = data.get('联系电话', [''])[0]
        
        # 填充模板
        filled_report = template.format(
            company_name=company_name,
            registration_number=registration_number,
            address=address,
            contact_person=contact_person,
            contact_number=contact_number
        )
        
        logger.info("Report template filled successfully.")
        return filled_report
    except Exception as e:
        logger.error(f"Error filling report template: {str(e)}")
        return "Error filling report template."

@tool
def save_report_to_md(report_content: str, output_path: str) -> None:
    """
    将生成的报告保存为Markdown文件。
    
    Args:
        report_content (str): 报告内容。
        output_path (str): 输出Markdown文件路径。
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        logger.info(f"Report saved to Markdown at {output_path}")
    except Exception as e:
        logger.error(f"Error saving report to Markdown: {str(e)}")

def create_report_generator_agent(llm: ChatGoogleGenerativeAI) -> AgentExecutor:
    """
    创建报告生成代理。
    
    Args:
        llm (ChatGoogleGenerativeAI): 使用的语言模型。
    
    Returns:
        AgentExecutor: 代理执行器。
    """
    logger.info("Creating report generator agent")
    tools = [fill_report_template, save_report_to_md]#之后添加了函数需要在这里添加
    system_message = "您是一位报告生成专家，负责根据企业信息生成调查报告。"
    
    agent = AgentExecutor.from_agent_and_tools(
        agent=llm,
        tools=tools,
        prompt=system_message,
        verbose=True
    )
    
    logger.info("Report generator agent created successfully.")
    return agent

# 读取Markdown模板文件
def read_markdown_template(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

# 示例用法
if __name__ == "__main__":
    # 初始化语言模型
    llm = ChatGoogleGenerativeAI(model="gemini-pro", api_key=GEMINI_API_KEY)
    report_generator_agent = create_report_generator_agent(llm)

    # 读取企业信息总表
    enterprise_data = pd.read_csv("output/enterprise_data_summary.csv")

    # 读取报告模板
    report_template = read_markdown_template("path/to/your/template.md")

    # 填充报告
    filled_report = fill_report_template(enterprise_data, report_template)

    # 保存报告
    save_report_to_md(filled_report, "output/enterprise_report.md") 