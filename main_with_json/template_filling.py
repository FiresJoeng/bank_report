#要根据模板需要填充的位置修改代码
from docx import Document
from util.logger import setup_logger

# 设置日志记录
logger = setup_logger()

def fill_static_fields(doc: Document, static_data: dict) -> None:
    """
    在模板的固定占位符中填入静态字段值。

    Args:
        doc (Document): 模板对象。
        static_data (dict): 静态数据字典，包含要填充的字段值。
    """
    logger.info("开始填充静态字段。")
    for key, value in static_data.items():
        placeholder = f"{{{{ {key} }}}}"  # 假设占位符格式为 {{ key }}
        for paragraph in doc.paragraphs:
            if placeholder in paragraph.text:
                paragraph.text = paragraph.text.replace(placeholder, str(value))
                logger.info(f"填充字段: {key}，值: {value}")

    logger.info("静态字段填充完成。")

def fill_dynamic_analysis(doc: Document, dynamic_analysis: str) -> None:
    """
    在模板的分析段落占位符中填入 AI 生成的语句。

    Args:
        doc (Document): 模板对象。
        dynamic_analysis (str): AI 生成的分析语句。
    """
    logger.info("开始填充动态分析语句。")
    analysis_placeholder = "{{ dynamic_analysis }}"  # 假设分析段落占位符为 {{ dynamic_analysis }}
    for paragraph in doc.paragraphs:
        if analysis_placeholder in paragraph.text:
            paragraph.text = paragraph.text.replace(analysis_placeholder, dynamic_analysis)
            logger.info("动态分析语句填充完成。")
            break  # 假设只需填充第一个找到的占位符

    logger.info("动态分析填充完成。")

# 设置日志记录
logger = setup_logger()

def save_report(doc: Document, output_path: str) -> None:
    """
    将填充完成的模板文档保存为 DOCX 文件。

    Args:
        doc (Document): 填充完成的模板对象。
        output_path (str): 目标保存路径。
    """
    try:
        doc.save(output_path)
        log_process_step(f"报告成功保存为: {output_path}")
    except Exception as e:
        log_process_step(f"保存报告时出错: {str(e)}")

def log_process_step(description: str) -> None:
    """
    记录报告生成过程中每个步骤的状态和结果，用于调试和审计。

    Args:
        description (str): 日志描述。
    """
    logger.info(description)