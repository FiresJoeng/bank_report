import requests
from typing import Dict
from util.logger import setup_logger

# 设置日志记录
logger = setup_logger()

DEEPSEEK_API_URL = "https://api.deepseek.com/generate"  # 假设的 DeepSeek API URL

def generate_analysis_with_ai(data: dict) -> dict:
    """调用 DeepSeek API，为指定字段生成分析语句，并返回生成的段落内容。"""
    try:
        # 准备请求数据
        payload = {
            "register_capital": data.get("register_capital"),
            "industry": data.get("industry"),
            "company_desc": data.get("company_desc"),
            # 可以根据需要添加更多字段
        }
        
        logger.info("调用 DeepSeek API 生成分析语句...")
        response = requests.post(DEEPSEEK_API_URL, json=payload)
        response.raise_for_status()  # 检查请求是否成功

        # 解析响应
        analysis_result = response.json()
        data["dynamic_analysis"] = analysis_result.get("analysis", "未生成分析内容")
        logger.info("成功生成分析语句。")
    except Exception as e:
        logger.error(f"调用 DeepSeek API 时出错: {str(e)}")
        data["dynamic_analysis"] = "分析生成失败"
    
    return data

def process_static_data(data: dict) -> dict:
    """从 JSON 数据中提取静态字段并格式化，用于直接填充模板的固定位置。"""
    static_fields = [
        "name",
        "found_time",
        "register_capital",
        "company_address",
        "representative",
        "industry",
        # 可以根据需要添加更多字段
    ]
    
    processed_data = {field: data.get(field) for field in static_fields}
    logger.info("成功提取静态字段。")
    
    return processed_data