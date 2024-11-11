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
    """读取企业信息CSV文件并返回DataFrame。"""
    try:
        logger.info(f"读取CSV数据: {file_path}")
        df = pd.read_csv(file_path)
        logger.info(f"成功读取CSV数据，行数: {len(df)}")
        return df
    except Exception as e:
        logger.error(f"读取CSV数据时出错: {str(e)}")
        return pd.DataFrame()

@tool
def read_excel_data(file_path: str) -> pd.DataFrame:
    """读取企业信息Excel文件并返回DataFrame。"""
    try:
        logger.info(f"读取Excel数据: {file_path}")
        df = pd.read_excel(file_path)
        logger.info(f"成功读取Excel数据，行数: {len(df)}")
        return df
    except Exception as e:
        logger.error(f"读取Excel数据时出错: {str(e)}")
        return pd.DataFrame()

@tool
def merge_dataframes(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """合并两个DataFrame，确保没有重复信息。"""
    logger.info("合并DataFrames")
    merged_df = pd.concat([df1, df2]).drop_duplicates().reset_index(drop=True)
    logger.info(f"成功合并，结果行数: {len(merged_df)}")
    return merged_df

@tool
def save_to_csv(df: pd.DataFrame, output_path: str) -> None:
    """将DataFrame保存为CSV文件。"""
    try:
        df.to_csv(output_path, index=False)
        logger.info(f"数据已保存为CSV: {output_path}")
    except Exception as e:
        logger.error(f"保存CSV时出错: {str(e)}")

@tool
def save_to_md(df: pd.DataFrame, output_path: str) -> None:
    """将DataFrame保存为Markdown文件。"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(df.to_markdown(index=False))
        logger.info(f"数据已保存为Markdown: {output_path}")
    except Exception as e:
        logger.error(f"保存Markdown时出错: {str(e)}")

def create_enterprise_data_agent(llm: ChatGoogleGenerativeAI) -> AgentExecutor:
    """创建企业数据代理。"""
    logger.info("创建企业数据代理")
    tools = [read_csv_data, read_excel_data, merge_dataframes, save_to_csv, save_to_md]
    system_message = "您是一位企业数据处理专家，负责读取和合并企业信息数据。"
    
    agent = AgentExecutor.from_agent_and_tools(
        agent=llm,
        tools=tools,
        prompt=system_message,
        verbose=True
    )
    
    logger.info("企业数据代理创建成功")
    return agent

# 示例用法
if __name__ == "__main__":
    llm = ChatGoogleGenerativeAI(model="gemini-pro")
    enterprise_agent = create_enterprise_data_agent(llm)

    # 读取CSV和Excel文件
    csv_data = read_csv_data("path/to/enterprise_data.csv")
    excel_data = read_excel_data("path/to/enterprise_data.xlsx")

    # 合并数据
    combined_data = merge_dataframes(csv_data, excel_data)

    # 输出结果
    save_to_csv(combined_data, "output/enterprise_data_summary.csv")
    save_to_md(combined_data, "output/enterprise_data_summary.md")