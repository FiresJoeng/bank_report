# 导入模块
from tools.FileEdit import create_document, read_document, edit_document, collect_data
from tools.basetool import execute_code, execute_command
from tools.internet import google_search, scrape_webpages_with_fallback
from langchain_community.utilities import WikipediaAPIWrapper

from langchain_community.tools import WikipediaQueryRun
from langchain.agents import load_tools
from node import agent_node, human_choice_node, note_agent_node, human_review_node, refiner_node
from router import QualityReview_router, hypothesis_router, process_router
from create_agent import create_agent, create_supervisor
from state import State

from langgraph.graph import StateGraph
import os
from logger import setup_logger
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from load_cfg import GOOGLE_API_KEY, LANGCHAIN_API_KEY, WORKING_DIRECTORY

# Env 配置
os.environ['https_proxy'] = 'http://127.0.0.1:7890'
os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['all_proxy'] = 'socks5://127.0.0.1:7890'

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Multi-Agent Data Analysis System"

# logger 配置
logger = setup_logger()

# genai config 配置
generation_config_dict = {
    "temperature": 1,  # 生成温度，值越高，对于同样的问题，给出不同回答的可能性越高
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,  # 生成的最大token数量，超过此值，会截断
    "response_mime_type": "text/plain",  # 应答格式，可替换为text/json
}

# 提示词
prompt = '''
你是广州银行的一名资深分析师，主要职责是评估企业或个人的信用风险，分析借款人的财务状况，并根据评估结果撰写授信报告，以供银行管理层或风险控制部门决策。
你具备一流的财务分析能力和风险管理能力，拥有多年的工作经验和丰富的专业技能。
现在，你的任务是遍历数据mapping表的内容，生成中间表格。
'''

# LLM 初始化配置
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro", temperature=0, max_tokens=4096)
    power_llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro", temperature=0.5, max_tokens=4096)
    json_llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",  # 模型名称, 可替换为gemini-1.5-flash, gemini-1.5-pro-exp-0827等
        generation_config=generation_config_dict,  # 导入生成CFG字典
        system_instruction=prompt,  # Prompt 设置
    )
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    logger.info("LLM初始化完毕.")
except Exception as e:
    logger.error(f"LLM初始化过程中发生了一个错误: {str(e)}")
    raise

# 工作目录检查
if not os.path.exists(WORKING_DIRECTORY):
    os.makedirs(WORKING_DIRECTORY)
    logger.info(f"工作目录已创建: {WORKING_DIRECTORY}")


logger.info("程序初始化完毕.")

# 测试
model = genai.GenerativeModel('gemini-1.5-pro')
response = model.generate_content(prompt)
print(str(response))

# 工作流
workflow = StateGraph(State)
members = ["Hypothesis", "Process", "Visualization",
           "Search", "Coder", "Report", "QualityReview", "Refiner"]

# 创建agent
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
hypothesis_agent = create_agent(
    llm,
    [collect_data, wikipedia, google_search,
        scrape_webpages_with_fallback]+load_tools(["arxiv"],),
    '''
As an esteemed expert in data analysis, your task is to formulate a set of research hypotheses and outline the steps to be taken based on the information table provided. Utilize statistics, machine learning, deep learning, and artificial intelligence in developing these hypotheses. Your hypotheses should be precise, achievable, professional, and innovative. To ensure the feasibility and uniqueness of your hypotheses, thoroughly investigate relevant information. For each hypothesis, include ample references to support your claims.

Upon analyzing the information table, you are required to:

1. Formulate research hypotheses that leverage statistics, machine learning, deep learning, and AI techniques.
2. Outline the steps involved in testing these hypotheses.
3. Verify the feasibility and uniqueness of each hypothesis through a comprehensive literature review.

At the conclusion of your analysis, present the complete research hypotheses, elaborate on their uniqueness and feasibility, and provide relevant references to support your assertions. Please answer in structured way to enhance readability.
Just answer a research hypothesis.
''',
    members, WORKING_DIRECTORY)
