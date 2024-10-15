import os
import pandas as pd
import re
import json
import google.generativeai as genai
import typing_extensions as typing
from docx import Document as DocxDocument

# API 设置
GEMINI_API_KEY = "AIzaSyDCNWIp1_9QqBfzYqAuRvzy4s8pfevQk5s"
genai.configure(api_key=GEMINI_API_KEY)

# 代理设置 (For Clash)
os.environ['https_proxy'] = 'http://127.0.0.1:7890'
os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['all_proxy'] = 'socks5://127.0.0.1:7890'


class Scores(typing.TypedDict):
    消息面分析: int
    宏观面分析和产业分析: int
    基本面分析: int
    市场面分析: int
    资产选择决策: int
    投资组合构建: int
    投资绩效评估: int
    回测分析: int
    参考文献与附录: int


class EvaluationResult(typing.TypedDict):
    summary: str
    scores: Scores
    total_score: int
    comments: str


# 使用 `response_schema` 生成 JSON 输出
generation_config = {
    "response_mime_type": "application/json",
    "response_schema": EvaluationResult
}


# 定义生成评估的函数
def generate_evaluation(text):
    prompt = f"""
你是国际顶尖研究生金融科技前沿课的教授。你的任务是评估学生的生成式AI个人应用报告，报告部分包括消息面、宏观面、产业分析、基本面、市场面的分析和决策，进行投资组合优化和绩效评估。根据以下评分标准对报告进行评估：
1. 数据获取、分析与决策（50分）
  - 消息面分析（10分）
  - 宏观面分析和产业分析（10分）
  - 基本面分析（15分）
  - 市场面分析（10分）
  - 资产选择决策（5分）
2. 投资组合优化与绩效评估（50分）
  - 投资组合构建（20分）
  - 投资绩效评估（10分）
  - 回测分析（10分）
  - 参考文献与附录（10分）

请提供报告的简要总结（如应用什么工具、什么提示词，完成了什么场景问题的解决，注意需要有具体的工具和场景名）、每个评分标准的得分（即使得分为0，也请明确标出），总分和报告评语（150字），并以JSON格式输出。

输出格式：
{{
    "summary": "简要总结",
    "scores": {{
        "消息面分析": 0,
        "宏观面分析和产业分析": 0,
        "基本面分析": 0,
        "市场面分析": 0,
        "资产选择决策": 0,
        "投资组合构建": 0,
        "投资绩效评估": 0,
        "回测分析": 0,
        "参考文献与附录": 0
    }},
    "total_score": 0,
    "comments": "报告评语"
}}

报告文本：
"{text}"
"""
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config=generation_config)
    response = model.generate_content(prompt)
    return response.text


def extract_text_from_md(file_path):
    try:
        with open(file_path, 'rb') as file:
            reader = Pymd2.mdReader(file)
            text = ''
            for page in reader.pages:
                if page.extract_text():
                    text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error extracting text from md file {file_path}: {e}")
        return ""


def extract_text_from_docx(file_path):
    try:
        doc = DocxDocument(file_path)
        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        return '\n'.join(text)
    except Exception as e:
        print(f"Error extracting text from DOCX file {file_path}: {e}")
        return ""


def extract_info_from_filename(filename):
    # 正则表达式匹配学生学号（数字+可选字母+数字）和姓名（汉字），中间允许有空格
    match = re.match(r'(\d{5}[A-Z]?\d{3})[\s]?([\u4e00-\u9fa5\s]+)', filename)
    if not match:
        match = re.match(r'(\d{9})[\s]?([\u4e00-\u9fa5\s]+)', filename)

    report_title = filename.rsplit('.', 1)[0]  # 确保 report_title 总是被定义

    if match:
        student_id = match.group(1).strip()
        name = match.group(2).strip()
        return student_id, name, report_title
    else:
        return None, None, report_title


# 遍历文件夹中的md和DOCX文件
data = []
empty_files = []

for filename in os.listdir(md_folder):
    print(f"Found file: {filename}")  # Debugging output
    if filename.endswith('.md') or filename.endswith('.docx'):
        print(f"Processing file: {filename}")  # Debugging output
        file_path = os.path.join(md_folder, filename)
        student_id, name, report_title = extract_info_from_filename(filename)
        print(
            f"Extracted info - Student ID: {student_id}, Name: {name}, Report Title: {report_title}")  # Debugging output
        if report_title:  # student_id and name
            if filename.endswith('.md'):
                text = extract_text_from_md(file_path)
            elif filename.endswith('.docx'):
                print(f"Extracting text from DOCX file: {filename}")  # Debugging output
                text = extract_text_from_docx(file_path)
            print(f"Extracted text: {text[:100]}...")  # Print first 100 characters of text for debugging
            if not text or len(text.strip()) == 0:
                empty_files.append(filename)
            elif len(text) < 100:
                empty_files.append(filename)
            else:
                try:
                    evaluation = generate_evaluation(text)
                    print("Evaluation Output:", evaluation)  # Debugging output

                    evaluation_json = json.loads(evaluation)
                    # 添加学号、姓名和报告名称
                    evaluation_json.update({"学号": student_id, "姓名": name, "报告名称": report_title})
                    data.append(evaluation_json)
                except Exception as e:
                    print(f"Error processing evaluation for {filename}: {e}")
                    print("Full Evaluation Output for Debugging:", evaluation)  # Additional debugging output

# 将结果保存到Excel文件中
if data:
    df = pd.json_normalize(data)
    df.to_excel('summary_report.xlsx', index=False)
    print("摘要已成功生成并保存到 summary_report.xlsx")

# 将空文件保存到单独的Excel文件中
if empty_files:
    empty_df = pd.DataFrame(empty_files, columns=["filename"])
    empty_df.to_excel('empty_files.xlsx', index=False)
    print("空文件列表已保存到 empty_files.xlsx")
else:
    print("未生成任何评估结果。")
