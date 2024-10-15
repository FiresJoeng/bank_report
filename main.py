# 模块导入
import os
import docx
import google.generativeai as genai

# API 设置
GEMINI_API_KEY = "AIzaSyDCNWIp1_9QqBfzYqAuRvzy4s8pfevQk5s"
genai.configure(api_key=GEMINI_API_KEY)

# 代理设置 (For Clash)
os.environ['https_proxy'] = 'http://127.0.0.1:7890'
os.environ['http_proxy'] = 'http://127.0.0.1:7890'

# 生成CFG设置
generation_config_dict = {
    "temperature": 1,  # 生成温度，值越高，对于同样的问题，给出不同回答的可能性越高
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,  # 生成的最大token数量，超过此值，会截断
    "response_mime_type": "text/plain",  # 应答格式，可替换为text/json
}


def read_docx(docx_files_path):
    doc = docx.Document(docx_files_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)


def convert_to_md(text):
    # 简单转换为标题 (假设每一段第一个单词为 'Heading' 表示为标题)
    # 将文档中类似标题的部分转为 Markdown 的 #
    md_text = text.replace('\nHeading', '\n# Heading')
    return md_text


# 模型设置
prompt = '''
你是广州银行的一名资深分析师，主要职责是评估企业或个人的信用风险，分析借款人的财务状况，并根据评估结果撰写授信报告，以供银行管理层或风险控制部门决策。
你具备一流的财务分析能力和风险管理能力，拥有多年的工作经验和丰富的专业技能。
现在，你的任务是遍历数据mapping表的内容，生成中间表格。
'''

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",  # 模型名称, 可替换为gemini-1.5-flash, gemini-1.5-pro-exp-0827等
    generation_config=generation_config_dict,  # 导入生成CFG字典
    system_instruction=prompt,  # Prompt 设置
)


# 聊天记录
history = []

# 对话循环体
while True:
    user_input = input("You > ")  # 输入端

    chat_session = model.start_chat(
        history=history
    )

    response = chat_session.send_message(user_input)
    print(f"Gemini > {response.text}")  # 输出端

    # 记录聊天历史
    history.append({"role": "user", "parts": [user_input]})
    history.append({f"role": "model", "parts": [response.text]})
