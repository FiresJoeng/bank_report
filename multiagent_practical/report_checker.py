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
def initial_check(report_content: str) -> str:
    """
    对报告进行初步检查，确保格式无误。
    
    Args:
        report_content (str): 报告内容。
    
    Returns:
        str: 检查结果和建议。
    """
    logger.info("Performing initial check on the report.")
    if "企业调查报告" not in report_content:
        return "报告缺少标题，请添加 '企业调查报告'。"
    return "初步检查通过，格式无误。"

@tool
def detail_check(report_content: str) -> str:
    """
    对报告内容进行细节检查，确保信息准确。
    
    Args:
        report_content (str): 报告内容。
    
    Returns:
        str: 检查结果和建议。
    """
    logger.info("Performing detail check on the report.")
    if "公司名称" not in report_content or "注册号" not in report_content:
        return "报告缺少重要字段：公司名称或注册号，请确认。"
    return "细节检查通过，内容准确。"

@tool
def generate_modification_suggestions(report_content: str) -> str:
    """
    生成针对报告的修改建议。
    
    Args:
        report_content (str): 报告内容。
    
    Returns:
        str: 修改建议。
    """
    logger.info("Generating modification suggestions for the report.")
    suggestions = []
    if "公司名称" not in report_content:
        suggestions.append("公司名称缺失，请添加。")
    if "注册号" not in report_content:
        suggestions.append("注册号缺失，请添加。")
    return "\n".join(suggestions) if suggestions else "没有发现需要修改的地方。"

@tool
def check_report(report_content: str) -> str:
    """
    进行多次检查，直到报告符合标准。
    
    Args:
        report_content (str): 报告内容。
    
    Returns:
        str: 最终检查结果。
    """
    logger.info("Starting report check process.")
    initial_result = initial_check(report_content)
    if "缺失" in initial_result:
        return initial_result

    detail_result = detail_check(report_content)
    if "缺失" in detail_result:
        return detail_result

    suggestions = generate_modification_suggestions(report_content)
    if "没有发现" in suggestions:
        return "报告检查通过，所有问题已解决。"
    
    return f"报告检查未通过，建议修改如下：\n{suggestions}"

@tool
def save_final_report(report_content: str, output_path: str) -> None:
    """
    保存最终版本的报告为Markdown文件。
    
    Args:
        report_content (str): 最终报告内容。
        output_path (str): 输出Markdown文件路径。
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        logger.info(f"Final report saved to Markdown at {output_path}")
    except Exception as e:
        logger.error(f"Error saving final report to Markdown: {str(e)}")

def create_report_checker_agent(llm: ChatGoogleGenerativeAI) -> AgentExecutor:
    """
    创建报告检查代理。
    
    Args:
        llm (ChatGoogleGenerativeAI): 使用的语言模型。
    
    Returns:
        AgentExecutor: 代理执行器。
    """
    logger.info("Creating report checker agent")
    tools = [check_report, save_final_report]#之后添加了函数需要在这里添加
    system_message = "您是一位报告检查专家，负责检查和修改调查报告。"
    
    agent = AgentExecutor.from_agent_and_tools(
        agent=llm,
        tools=tools,
        prompt=system_message,
        verbose=True
    )
    
    logger.info("Report checker agent created successfully.")
    return agent

# 示例用法 之后只运行main_multiagent.py
if __name__ == "__main__":
    # 初始化语言模型
    llm = ChatGoogleGenerativeAI(model="gemini-pro", api_key=GEMINI_API_KEY)
    # 初始化语言模型
    llm = ChatGoogleGenerativeAI(model="gemini-pro", api_key=GEMINI_API_KEY)
    report_checker_agent = create_report_checker_agent(llm)

    # 读取报告内容
    report_content = open("output/enterprise_report.md", "r", encoding="utf-8").read()

    # 检查报告
    check_result = check_report(report_content)
    print(check_result)

    # 如果检查通过，保存最终报告
    if "通过" in check_result:
        save_final_report(report_content, "output/final_enterprise_report.md") 