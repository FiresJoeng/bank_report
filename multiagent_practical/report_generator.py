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
def log_report_generation_step(step_description: str) -> None:
    """记录报告生成过程中的每一步操作。"""
    logger.info(step_description)

# 生成填写日志：在生成报告时，记录所有的操作步骤和结果，确保报告的生成过程是可追踪的。


@tool
def fill_report_template(data: pd.DataFrame, template: str, llm: ChatGoogleGenerativeAI) -> str:
    """
    根据企业信息总表填充调查报告模板，并允许LLM对模板做修改。
    
    Args:
        data (pd.DataFrame): 企业信息总表。
        template (str): 报告模板。
        llm (ChatGoogleGenerativeAI): 使用的语言模型。
    
    Returns:
        str: 填充并修改后的报告内容。
    """
    try:
        # 提取相关信息，确保字段存在
        required_fields = [
            'name', 'register_code', 'company_address', 'register_address',
            'representative', 'found_time', 'biz_scope', 'company_type',
            'register_capital', 'tags', 'industry', 'company_desc',
            'register_institute', 'actual_capital', 'used_name',
            'staffs', 'tax_address', 'portraits'
        ]
        
        for field in required_fields:
            if field not in data.columns:
                logger.error(f"缺少必要字段: {field}")
                return "缺少必要字段，无法生成报告。"

        # 填充模板
        filled_report = template.format(**{field: data[field].iloc[0] for field in required_fields})
        
        # 让LLM对填充后的模板进行合理的修改
        modified_report = llm(filled_report)
        
        logger.info("Report template filled and modified successfully.")
        return modified_report
    except Exception as e:
        logger.error(f"Error filling report template: {str(e)}")
        return "Error filling report template."

@tool
def save_report_to_md(report_content: str, output_path: str) -> None:
    """将生成的报告保存为Markdown文件。"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        logger.info(f"Report saved to Markdown at {output_path}")
    except Exception as e:
        logger.error(f"Error saving report to Markdown: {str(e)}")

def create_report_generator_agent(llm: ChatGoogleGenerativeAI) -> AgentExecutor:
    """创建报告生成代理。"""
    logger.info("Creating report generator agent")
    tools = [fill_report_template, save_report_to_md]
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

# 示例用法 之后只运行main_multiagent.py
if __name__ == "__main__":
    # 初始化语言模型
    llm = ChatGoogleGenerativeAI(model="gemini-pro", api_key=GEMINI_API_KEY)
    report_generator_agent = create_report_generator_agent(llm)

    # 读取企业信息总表
    enterprise_data = pd.read_csv("output/enterprise_data_summary.csv")

    # 读取报告模板
    report_template = read_markdown_template("path/to/your/template.md")

    # 填充报告
    filled_report = fill_report_template(enterprise_data, report_template, llm)

    # 保存报告
    save_report_to_md(filled_report, "output/enterprise_report.md")