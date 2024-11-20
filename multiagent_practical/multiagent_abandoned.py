import pandas as pd
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor
from langchain.tools import tool
from logger import setup_logger


# 引入企业数据代理、报告生成代理和报告检查代理的相关函数
from multiagent_practical.enterprise_data_agent import (
    read_csv_data,
    save_to_csv,
    save_to_md,
    create_enterprise_data_agent
)

from multiagent_practical.report_generator import (
    fill_report_template,
    save_report_to_md,
    create_report_generator_agent
)

from multiagent_practical.report_checker import (
    check_report,
    save_final_report,
    create_report_checker_agent
)

# 设置日志记录
logger = setup_logger()

# 验证和加载API密钥
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

if not GEMINI_API_KEY or not LANGCHAIN_API_KEY:
    raise ValueError("请确保设置了GEMINI_API_KEY和LANGCHAIN_API_KEY环境变量。")

@tool
def read_enterprise_data(csv_path: str, excel_path: str) -> pd.DataFrame:
    """读取和合并企业数据。"""
    logger.info("Reading enterprise data from CSV and Excel.")
    try:
        csv_data = pd.read_csv(csv_path)
        excel_data = pd.read_excel(excel_path)
        combined_data = pd.concat([csv_data, excel_data]).drop_duplicates().reset_index(drop=True)
        
        # 检查数据完整性
        required_fields = ['name', 'register_code', 'company_address', 'register_time']
        for field in required_fields:
            if field not in combined_data.columns:
                logger.error(f"缺少必要字段: {field}")
                raise ValueError(f"缺少必要字段: {field}")
        
        logger.info("Enterprise data read and merged successfully.")
        return combined_data
    except Exception as e:
        logger.error(f"Error reading enterprise data: {str(e)}")
        return pd.DataFrame()  # 返回空DataFrame以防止后续错误

def create_enterprise_data_agent(llm: ChatGoogleGenerativeAI) -> AgentExecutor:
    """创建企业数据处理代理。"""
    logger.info("Creating enterprise data processing agent.")
    tools = [read_enterprise_data]
    system_message = "您是一位数据处理专家，负责读取和处理企业数据。"
    
    agent = AgentExecutor.from_agent_and_tools(
        agent=llm,
        tools=tools,
        prompt=system_message,
        verbose=True
    )
    
    logger.info("Enterprise data processing agent created successfully.")
    return agent

@tool
def fill_report_template(data: pd.DataFrame, template: str, llm: ChatGoogleGenerativeAI) -> str:
    """根据企业信息总表填充报告模板。"""
    logger.info("Filling report template.")
    try:
        fields = {field: data[field].iloc[0] for field in data.columns if field in data.columns}
        filled_report = template.format(**fields)
        modified_report = llm(filled_report)  # 让LLM修改
        logger.info("Report template filled and modified successfully.")
        return modified_report
    except Exception as e:
        logger.error(f"Error filling report template: {str(e)}")
        return "Error filling report template."

def create_report_generator_agent(llm: ChatGoogleGenerativeAI) -> AgentExecutor:
    """创建报告生成代理。"""
    logger.info("Creating report generation agent.")
    tools = [fill_report_template]
    system_message = "您是一位报告生成专家，负责根据企业数据生成报告。"
    
    agent = AgentExecutor.from_agent_and_tools(
        agent=llm,
        tools=tools,
        prompt=system_message,
        verbose=True
    )
    
    logger.info("Report generation agent created successfully.")
    return agent

@tool
def initial_check(report_content: str) -> str:
    """对报告进行初步检查，确保格式无误。"""
    logger.info("Performing initial check on the report.")
    if "企业调查报告" not in report_content:
        return "报告缺少标题，请添加 '企业调查报告'。"
    return "初步检查通过，格式无误。"

@tool
def detail_check(report_content: str) -> str:
    """对报告内容进行细节检查，确保信息准确。"""
    logger.info("Performing detail check on the report.")
    missing_fields = []
    if "公司名称" not in report_content:
        missing_fields.append("公司名称")
    if "注册号" not in report_content:
        missing_fields.append("注册号")
    
    if missing_fields:
        return f"报告缺少重要字段：{', '.join(missing_fields)}，请确认。"
    
    return "细节检查通过，内容准确。"

@tool
def generate_modification_suggestions(report_content: str) -> str:
    """生成针对报告的修改建议。"""
    logger.info("Generating modification suggestions for the report.")
    suggestions = []
    if "公司名称" not in report_content:
        suggestions.append("公司名称缺失，请添加。")
    if "注册号" not in report_content:
        suggestions.append("注册号缺失，请添加。")
    
    return "\n".join(suggestions) if suggestions else "没有发现需要修改的地方。"

def create_report_checker_agent(llm: ChatGoogleGenerativeAI) -> AgentExecutor:
    """创建报告检查代理。"""
    logger.info("Creating report checker agent.")
    tools = [initial_check, detail_check, generate_modification_suggestions]
    system_message = "您是一位报告检查专家，负责检查和修改调查报告。"
    
    agent = AgentExecutor.from_agent_and_tools(
        agent=llm,
        tools=tools,
        prompt=system_message,
        verbose=True
    )
    
    logger.info("Report checker agent created successfully.")
    return agent

@tool
def save_final_report(report_content: str, output_path: str) -> None:
    """保存最终版本的报告为Markdown文件。"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        logger.info(f"Final report saved to Markdown at {output_path}")
    except Exception as e:
        logger.error(f"Error saving final report to Markdown: {str(e)}")

def main():
    # 初始化语言模型
    llm = ChatGoogleGenerativeAI(model="gemini-pro", api_key=GEMINI_API_KEY)

    # 创建代理
    data_agent = create_enterprise_data_agent(llm)
    report_agent = create_report_generator_agent(llm)
    checker_agent = create_report_checker_agent(llm)

    # 读取企业数据
    enterprise_data = read_enterprise_data("path/to/enterprise_data.csv", "path/to/enterprise_data.xlsx")
    if enterprise_data.empty:
        logger.error("未能读取企业数据，程序终止。")
        return

    # 读取报告模板
    try:
        with open("path/to/template.md", "r", encoding="utf-8") as f:
            report_template = f.read()
    except FileNotFoundError:
        logger.error("报告模板文件未找到，请检查路径。")
        return

    # 填充报告
    filled_report = fill_report_template(enterprise_data, report_template, llm)

    # 检查报告
    check_result = check_report(filled_report)
    print(check_result)

    # 如果检查通过，保存最终报告
    if "通过" in check_result:
        save_final_report(filled_report, "output/final_enterprise_report.md")

if __name__ == "__main__":
    main()