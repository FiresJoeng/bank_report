import os
from dotenv import load_dotenv

load_dotenv()

# 数据存储路径（绝对路径）
WORKING_DIRECTORY = "C:\\datasets\\"

# Anaconda 安装路径（绝对路径）
CONDA_PATH = "C:\\Users\\how\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Anaconda3 (64-bit)\\"

# Conda 环境名称
CONDA_ENV = "data_assistant"

# ChromeDriver 可执行文件路径（绝对路径）
CHROMEDRIVER_PATH = "C:\\Program Files\\chromedriver-win64\\chromedriver.exe"

# Firecrawl API 密钥（可选）
FIRECRAWL_API_KEY = "fc-3d9c44896d964e99a58f5b7f61a1039a"

# Google Gemini API 密钥（必需）
GEMINI_API_KEY = "AIzaSyBGbQ0y8IwyQVdm7xF2TTJnC-rPST319h4"

# 设置环境变量
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

# LangChain API 密钥（如果有的话）
LANGCHAIN_API_KEY = "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"

# SERPAPI 密钥（如果有的话）
SERPAPI_KEY = os.getenv('SERPAPI_KEY')

# 如果 SERPAPI_KEY 为 None，给它一个默认值
if SERPAPI_KEY is None:
    SERPAPI_KEY = "默认值或空字符串"

# 设置代理（如果需要）
os.environ['https_proxy'] = 'http://127.0.0.1:7890'
os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['all_proxy'] = 'socks5://127.0.0.1:7890'

# 确保在文件末尾有 __all__ 声明
__all__ = ['GEMINI_API_KEY', 'LANGCHAIN_API_KEY', 'WORKING_DIRECTORY', 'SERPAPI_KEY']
print(f"SERPAPI_KEY in load_cfg.py: {SERPAPI_KEY}")