import pandas as pd
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor
from langchain.tools import tool
from util.logger import setup_logger

# 设置日志记录
logger = setup_logger()

@tool
def log_report_generation_step(step_description: str) -> None:
    """记录报告生成过程中的每一步操作。"""
    logger.info(step_description)

# 生成填写日志：在生成报告时，记录所有的操作步骤和结果，确保报告的生成过程是可追踪的。

# 读取Markdown模板文件
@tool
def read_markdown_template(file_path: str) -> str:
    """读取Markdown模板文件。"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


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
    system_message ="""
    你是一名报告生成代理，负责根据提供的企业信息表格填充调查报告模板。你的任务是确保企业的关键信息被准确地填入模板的指定部分，并根据需要对模板内容进行合理的修改，使其更加连贯和符合实际情况。

    ### 任务目标：
    - 你将接收一个包含企业信息的表格（通常是 CSV 或 DataFrame 格式）和一个 Markdown 模板文件。
    - 你的核心任务是将表格中的数据准确填入模板的相应部分，具体是申请人的企业基本信息部分。

    ### 数据匹配：
    - 请注意，模板中的字段名称与企业信息表格中的字段名称可能不完全一致。你需要仔细比对字段，并确保将正确的数据填入正确的位置。例如：
    - 表格中可能使用 `name` 表示公司名称，而模板中则使用 "公司名称"。
    - 类似地，`register_code` 对应 "注册号"，`company_address` 对应 "公司地址" 等。
    - 在填充时，请确保所有必要的信息都被正确地填入。如果某个字段在表格中缺失，请记录该问题，并在日志中注明。

    ### 日志记录：
    - 你需要记录生成报告过程中的每个步骤。包括但不限于：
     1. 开始填充模板。
     2. 数据字段的匹配结果。
      3. 模板修改后的结果。
     4. 报告成功保存的路径。
    - 如果遇到任何错误或缺失字段，需要及时记录并处理。

    ### 错误处理：
    - 如果在报告生成过程中发现任何错误（例如字段缺失、不匹配等），请记录详细的错误信息，并在日志中报错。
    - 不要生成有严重缺陷的报告。确保数据的完整性和准确性是你的首要任务。

    你的目标是生成一份完整、准确且可读的企业调查报告。请确保每一步都被详细记录，并确保最终输出符合要求。
    """
    
    agent = AgentExecutor.from_agent_and_tools(
        agent=llm,
        tools=tools,
        prompt=system_message,
        verbose=True
    )
    
    logger.info("Report generator agent created successfully.")
    return agent


# 示例用法 之后只运行main_multiagent.py
if __name__ == "__main__":
    # 初始化语言模型
    llm = ChatGoogleGenerativeAI(model="gemini-pro")
    report_generator_agent = create_report_generator_agent(llm)

    # 读取企业信息总表
    enterprise_data = pd.read_csv("output/enterprise_data_summary.csv")

    # 读取报告模板
    report_template = read_markdown_template("path/to/your/template.md")

    # 填充报告
    filled_report = fill_report_template(enterprise_data, report_template, llm)

    # 保存报告
    save_report_to_md(filled_report, "output/enterprise_report.md")