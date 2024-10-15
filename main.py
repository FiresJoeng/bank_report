# 模块导入
import os
import google.generativeai as genai
import pypandoc
import docx_to_md

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

# 函数: 转换docx文件为md文件
def load_file(docx_input, md_output):
    try:
        pypandoc.convert_file(docx_input, 'md', outputfile=md_output)
    except Exception as error:
        print(f"[错误] 转换{docx_input}失败! 原因: {error}")
        return None
    with open(md_output, 'r', encoding='utf-8') as load_md_file:
        md_content = load_md_file.read()
    return md_content

def load_file_2(docx_input, md_output):
    try:
        docx_to_md.convert(docx_input, md_output)
    except Exception as error:
        print(f"[错误] 转换{docx_input}失败! 原因: {error}")
        return None
    with open(md_output, 'r', encoding='utf-8') as load_md_file:
        md_content = load_md_file.read()
    return md_content


# report_template
docx_path = "./docx_files/仅页1_固定资产贷款调查报告模板.docx"
md_path = "./md_files/仅页1_固定资产贷款调查报告模板.md"
report_template = load_file(docx_path, md_path)

# reference_report
docx_path = "./docx_files/仅页1_晶正鑫：固定资产贷款调查报告20220512.docx"
md_path = "./md_files/仅页1_晶正鑫：固定资产贷款调查报告20220512.md"
reference_report = load_file_2(docx_path, md_path)

# enterprise_info
docx_path = "./docx_files/广东省电子信息产业集团有限公司-企业基础信用报告-20241015155110.docx"
md_path = "./md_files/广东省电子信息产业集团有限公司-企业基础信用报告-20241015155110.md"
enterprise_info = load_file(docx_path, md_path)

# prompt
prompt = f'''
你是广州银行的一名资深分析师，主要职责是评估企业或个人的信用风险，分析借款人的财务状况，并根据评估结果撰写贷款调查报告，以供银行管理层或风险控制部门决策。
你具备一流的财务分析能力和风险管理能力，拥有多年的工作经验和丰富的专业技能。
现在，你需要运用你的专业知识和技能，仔细研究现有的固定资产贷款调查报告的参考文件，并准备好完成我接下来提出的任务。

文件名：仅页1_晶正鑫：固定资产贷款调查报告20220512.md
---文件头分隔符---
{reference_report}
---文件尾分隔符---

以上是参考文件，请仔细阅读。
'''

# 模型设置
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",  # 模型名称, 可替换为gemini-1.5-flash, gemini-1.5-pro-exp-0827等
    generation_config=generation_config_dict,  # 导入生成CFG字典
    system_instruction=prompt,  # Prompt 设置
)

# 输入端
user_input = f'''
接下来，你需要根据我提供的"企业信息"，并参考"你刚刚阅读的报告文件的内容"，填充"固定贷款调查报告模板"。

文件名：仅页1_固定资产贷款调查报告模板.md
---文件头分隔符---
{report_template}
---文件尾分隔符---

文件名：企业信息.md
---文件头分隔符---
{enterprise_info}
---文件尾分隔符---

以上是工作需要用到的材料文件，请开始你的工作，生成一份markdown格式的报告，其标题应该替换为"该企业的固定资产贷款调查报告"。
注意，你只需要输出报告内容，不需要输出文件头和文件尾以及其他说明信息和语句。
'''

chat_history = []
chat_session = model.start_chat(history=chat_history)

# 输出端
response = chat_session.send_message(user_input)
print(f'''---文件头分隔符---
{response.text}
---文件尾分隔符---''')
try:
    generated_md_report = './md_files/已生成_固定资产贷款调查报告.md'
    generated_docx_report = './docx_files/已生成_固定资产贷款调查报告.docx'
    with open(generated_md_report, 'w', encoding='utf-8') as save_md_file:
        save_md_file.write(response.text)
    pypandoc.convert_file(generated_md_report, 'docx', outputfile=generated_docx_report)
except Exception as error:
    print(f"[错误] 保存文件失败! 原因: {error}")

chat_history.append({"role": "user", "parts": [user_input]})
chat_history.append({f"role": "model", "parts": [response.text]})
