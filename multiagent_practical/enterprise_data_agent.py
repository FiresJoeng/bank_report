import pandas as pd
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor
from langchain.tools import tool
from logger import setup_logger

# 设置日志记录
logger = setup_logger()

@tool
def read_csv_data(file_path: str) -> pd.DataFrame:
    """
    读取企业信息CSV文件并返回DataFrame。
    
    Args:
        file_path (str): CSV文件路径。
    
    Returns:
        pd.DataFrame: 解析后的企业信息DataFrame。
    """
    try:
        logger.info(f"Reading CSV data from {file_path}")
        df = pd.read_csv(file_path)
        logger.info("CSV data read successfully.")
        return df
    except Exception as e:
        logger.error(f"Error reading CSV data: {str(e)}")
        return pd.DataFrame()  # 返回空DataFrame以防止后续错误

@tool
def read_excel_data(file_path: str) -> pd.DataFrame:
    """
    读取企业信息Excel文件并返回DataFrame。
    
    Args:
        file_path (str): Excel文件路径。
    
    Returns:
        pd.DataFrame: 解析后的企业信息DataFrame。
    """
    try:
        logger.info(f"Reading Excel data from {file_path}")
        df = pd.read_excel(file_path)
        logger.info("Excel data read successfully.")
        return df
    except Exception as e:
        logger.error(f"Error reading Excel data: {str(e)}")
        return pd.DataFrame()  # 返回空DataFrame以防止后续错误

@tool
def merge_dataframes(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """
    合并两个DataFrame，确保没有重复信息。
    
    Args:
        df1 (pd.DataFrame): 第一个DataFrame。
        df2 (pd.DataFrame): 第二个DataFrame。
    
    Returns:
        pd.DataFrame: 合并后的DataFrame。
    """
    logger.info("Merging DataFrames")
    merged_df = pd.concat([df1, df2]).drop_duplicates().reset_index(drop=True)
    logger.info("DataFrames merged successfully.")
    return merged_df

@tool
def save_to_csv(df: pd.DataFrame, output_path: str) -> None:
    """
    将DataFrame保存为CSV文件。
    
    Args:
        df (pd.DataFrame): 要保存的DataFrame。
        output_path (str): 输出CSV文件路径。
    """
    try:
        df.to_csv(output_path, index=False)
        logger.info(f"Data saved to CSV at {output_path}")
    except Exception as e:
        logger.error(f"Error saving to CSV: {str(e)}")

@tool
def save_to_md(df: pd.DataFrame, output_path: str) -> None:
    """
    将DataFrame保存为Markdown文件。
    
    Args:
        df (pd.DataFrame): 要保存的DataFrame。
        output_path (str): 输出Markdown文件路径。
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(df.to_markdown(index=False))
        logger.info(f"Data saved to Markdown at {output_path}")
    except Exception as e:
        logger.error(f"Error saving to Markdown: {str(e)}")

def create_enterprise_data_agent(llm: ChatGoogleGenerativeAI) -> AgentExecutor:
    """
    创建企业数据代理。
    
    Args:
        llm (ChatGoogleGenerativeAI): 使用的语言模型。
    
    Returns:
        AgentExecutor: 代理执行器。
    """
    logger.info("Creating enterprise data agent")
    tools = [read_csv_data, read_excel_data, merge_dataframes, save_to_csv, save_to_md]
    system_message = "您是一位企业数据处理专家，负责读取和合并企业信息数据。"
    
    agent = AgentExecutor.from_agent_and_tools(
        agent=llm,
        tools=tools,
        prompt=system_message,
        verbose=True
    )
    
    logger.info("Enterprise data agent created successfully.")
    return agent

# 示例用法
if __name__ == "__main__":
    # 假设llm已经初始化
    llm = ChatGoogleGenerativeAI(model="gemini-pro")
    enterprise_agent = AgentExecutor.from_agent_and_tools(
        agent=llm,
        tools=[read_csv_data, read_excel_data, merge_dataframes, save_to_csv, save_to_md],
        prompt="您是一位企业数据处理专家，负责读取和合并企业信息数据。",
        verbose=True
    )

    # 读取CSV和Excel文件
    csv_data = read_csv_data("path/to/enterprise_data.csv")
    excel_data = read_excel_data("path/to/enterprise_data.xlsx")

    # 合并数据
    combined_data = merge_dataframes(csv_data, excel_data)

    # 输出结果
    save_to_csv(combined_data, "output/enterprise_data_summary.csv")
    save_to_md(combined_data, "output/enterprise_data_summary.md") 