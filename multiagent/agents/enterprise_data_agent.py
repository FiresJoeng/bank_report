import pandas as pd
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor
from langchain.tools import tool
from util.logger import setup_logger

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
def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """处理DataFrame，只保留指定的列。"""
    columns_to_keep = [
        'name', 'representative', 'found_time', 'company_address',
        'register_address', 'biz_scope', 'company_type',
        'register_capital', 'tags', 'industry',
        'company_desc', 'register_institute', 'actual_capital',
        'used_name', 'staffs', 'tax_address', 'portraits'
    ]
    logger.info("处理DataFrame，保留指定的列")
    processed_df = df[columns_to_keep] if all(
        col in df.columns for col in columns_to_keep) else pd.DataFrame()
    logger.info(f"处理后的DataFrame行数: {len(processed_df)}")
    return processed_df


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
    tools = [read_csv_data, process_dataframe, save_to_csv, save_to_md]
    system_message = """
    您是一位企业数据处理专家，负责从提供的企业信息 CSV 文件中提取所需的数据，并生成只包含指定字段的新 CSV 和 Markdown 文件。请严格按照以下任务步骤进行操作：

    ### 任务目标：
    1. 您将接收一个包含企业信息的 CSV 文件，文件中可能包含大量与企业相关的字段。
    2. 您的任务是从中提取指定的字段，并生成一个新的 CSV 文件和一个 Markdown 文件，两个文件应只包含这些指定的字段。

    ### 数据处理：
    - 您需要从 CSV 文件中提取以下字段：
    - `name`（公司名称）
    - `representative`（法定代表人）
    - `found_time`（成立日期）
    - `company_address`（公司地址）
    - `register_address`（注册地址）
    - `biz_scope`（经营范围）
    - `company_type`（公司类型）
    - `register_capital`（注册资本）
    - `tags`（标签）
    - `industry`（行业）
    - `company_desc`（公司简介）
    - `register_institute`（登记机构）
    - `actual_capital`（实缴资本）
    - `used_name`（曾用名）
    - `staffs`（员工数）
    - `tax_address`（税务地址）
    - `portraits`（公司肖像）
  
    - 请确保在处理数据时，所有必要字段都存在。如果某些字段缺失或不完整，请记录该问题并在日志中注明。

    ### 输出格式：
    - 您需要生成两个输出文件：
    1. **CSV 文件**：包含上述指定字段的企业数据。请确保数据格式正确，输出文件以逗号分隔。
    2. **Markdown 文件**：以 Markdown 表格的形式展示相同的数据，表格中显示所有提取到的字段及其对应的值。

    ### 日志记录：
    - 请在处理的每一步记录日志，包括但不限于以下内容：
    1. 成功读取 CSV 文件。
     2. 成功提取指定字段。
     3. 成功生成 CSV 和 Markdown 文件。
     4. 任何字段缺失或错误的处理情况。

    ### 错误处理：
    - 如果在处理过程中遇到任何问题（如 CSV 文件无法读取，字段缺失，或保存文件时出错），请记录详细的错误信息，并在日志中报错。
    - 如果某个字段无法找到或数据不完整，请在日志中详细记录，并跳过该字段或使用默认值。

    您的目标是从企业信息 CSV 文件中提取准确的数据，并生成两个格式化良好的输出文件（CSV 和 Markdown）。确保数据的完整性和准确性，并提供详细的日志记录。
    """

    agent = AgentExecutor.from_agent_and_tools(
        agent=llm,
        tools=tools,
        prompt=system_message,
        verbose=True
    )

    logger.info("企业数据代理创建成功")
    return agent


# 示例用法 之后只运行main_multiagent.py
if __name__ == "__main__":
    llm = ChatGoogleGenerativeAI(model="gemini-pro")
    enterprise_agent = create_enterprise_data_agent(llm)

    # 读取CSV和Excel文件
    csv_data = read_csv_data("path/to/enterprise_data.csv")

    # 输出结果
    save_to_md(csv_data, "output/enterprise_data_summary.md")
