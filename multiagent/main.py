# 模块导入
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from util.logger import setup_logger
from agents.enterprise_data_agent import create_enterprise_data_agent
from agents.report_generator import create_report_generator_agent
from agents.report_checker import create_report_checker_agent

logger = setup_logger()

# 提示
print('''
[提示] 请确保您的网络已连接到Clash代理（端口7890），否则无法正常使用。
[提示] 请确保您部署好了Python环境。
''')

# API 设置
GEMINI_API_KEY = "AIzaSyDCNWIp1_9QqBfzYqAuRvzy4s8pfevQk5s"

# 代理设置 (For Clash)
os.environ['https_proxy'] = 'http://127.0.0.1:7890'
os.environ['http_proxy'] = 'http://127.0.0.1:7890'

# 配置生成参数
generation_config_dict = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain"
}

# 创建 ChatGoogleGenerativeAI 实例
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    api_key=GEMINI_API_KEY,
    generation_config=generation_config_dict
)

enterprise_data_agent = create_enterprise_data_agent(llm)
