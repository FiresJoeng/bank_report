import pandas as pd
from pydantic import BaseModel, ValidationError
from typing import List, Dict
from util.logger import setup_logger

# 设置日志记录
logger = setup_logger()

class DataModel(BaseModel):
    name: str
    representative: str
    found_time: str
    company_address: str
    register_address: str
    biz_scope: str
    company_type: str
    register_capital: float
    tags: List[str]
    industry: str
    company_desc: str
    register_institute: str
    actual_capital: float
    used_name: str
    staffs: int
    tax_address: str
    portraits: str

def read_csv_data(file_path: str) -> pd.DataFrame:
    """读取 CSV 文件并转换为 Pandas DataFrame。"""
    try:
        logger.info(f"读取 CSV 数据: {file_path}")
        df = pd.read_csv(file_path)
        logger.info(f"成功读取 CSV 数据，行数: {len(df)}")
        return df
    except Exception as e:
        logger.error(f"读取 CSV 数据时出错: {str(e)}")
        return pd.DataFrame()

def validate_and_clean_data(data: pd.DataFrame) -> List[Dict]:
    """使用 Pydantic 验证数据，清洗并转换为 JSON 格式。"""
    validated_data = []
    for index, row in data.iterrows():
        try:
            # 创建 DataModel 实例以验证数据
            validated_row = DataModel(**row.to_dict())
            validated_data.append(validated_row.dict())
        except ValidationError as e:
            logger.error(f"数据验证失败，行索引: {index}, 错误信息: {e}")
    logger.info(f"成功验证并清洗数据，验证后的数据条数: {len(validated_data)}")
    return validated_data