# 提示: 在运行此脚本之前，请先安装 docx2md
# pip install docx2md


# 模块导入

import os
import docx
import subprocess
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


# 函数封装部分
def DOCXtoMD(docx_file_path, md_file_path):
    try:
        docx2md_command = f"python -m docx2md {docx_file_path} {md_file_path}"
        subprocess.run(docx2md_command, shell=True)
        print(f"[提示] 转换成功，输出文件保存在: {md_file_path}")
    except Exception as e:
        print(f"[错误] 转换失败，原因: {e}")


# 预设提示词
prompt = '''
'''

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",  # 模型名称, 可替换为gemini-1.5-flash, gemini-1.5-pro-exp-0827等
    generation_config=generation_config_dict,  # 导入生成CFG字典
    system_instruction=prompt,  # Prompt 设置
)


# LLM部分
chat_history = []

user_input = input("You > ")  # 输入端

chat_session = model.start_chat(history=chat_history)

response = chat_session.send_message(user_input)
print(f"Gemini > {response.text}")  # 输出端

chat_history.append({"role": "user", "parts": [user_input]})
chat_history.append({f"role": "model", "parts": [response.text]})
