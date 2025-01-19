import re
import requests
from langchain_community.document_loaders import BSHTMLLoader
from langchain_text_splitters import TokenTextSplitter
from pydantic import BaseModel, Field, ValidationError
from typing import List
from openai import OpenAI

# 确保 URL 请求有效
url = "https://en.wikipedia.org/wiki/Car"
response = requests.get(url)

# 检查请求是否成功
if response.status_code == 200:
    # 保存网页内容到本地文件，确保可以重复加载
    with open("car.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    
    # 使用 BSHTMLLoader 加载 HTML 文件
    loader = BSHTMLLoader("car.html", open_encoding="utf-8")
    document = loader.load()[0]  # 加载后的第一个文档
else:
    print("请求失败，状态码：", response.status_code)
    exit()

# 对页面内容进行简单清理，去除多余的换行
document.page_content = re.sub("\n\n+", "\n", document.page_content)

# 打印页面内容的长度（用于调试）
print(f"页面内容长度: {len(document.page_content)} 字符")

# 定义数据模型
class KeyDevelopment(BaseModel):
    """信息模型，用于表示历史发展的关键信息"""
    year: int = Field(
        ..., description="历史发展的年份"
    )
    description: str = Field(
        ..., description="该年份发生了什么发展事件？"
    )
    evidence: str = Field(
        ...,
        description="从文本中提取年份和描述的证据（原句）"
    )


class ExtractionData(BaseModel):
    """信息模型，用于表示从文本中提取的关键信息集合"""
    key_developments: List[KeyDevelopment]


# 定义 DeepSeek 的 API 调用函数
# 设置 DeepSeek API 密钥
DEEPSEEK_API_KEY = "sk-719d31085b36405f8b3c7747b46f58df"
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")


def extract_key_developments_from_text(text: str) -> List[KeyDevelopment]:
    """
    使用 DeepSeek API 提取文本中的关键信息
    :param text: 需要分析的文本
    :return: 提取的关键信息列表
    """
    # 调用 DeepSeek API 的消息体
    messages = [
        {"role": "system", "content": "You are an expert at identifying key historic developments in text. "
                                      "Only extract important historic developments. Extract nothing if no important information can be found in the text."},
        {"role": "user", "content": text},
    ]

    # 调用 DeepSeek API
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=False
    )

    # 提取返回的内容
    response_content = response.choices[0].message.content
    print("生成的内容:\n", response_content)  # 打印返回内容以便调试

    # 检查返回内容是否为有效的 JSON
    try:
        # 尝试解析为 JSON 格式
        extraction_data = ExtractionData.parse_raw(response_content)
        return extraction_data.key_developments
    except ValidationError as e:
        
       

        # 如果返回内容不是 JSON 格式，则逐行解析内容（应对非 JSON 的返回内容）
        key_developments = []
        for line in response_content.split("\n"):
            line = line.strip()
            if line:  # 跳过空行
                print(f" {line}")
        return key_developments
    except Exception as e:
        print(f"提取失败，发生未知错误：{e}")
        return []

# 定义文本分块逻辑
text_splitter = TokenTextSplitter(
    # 每个分块的大小
    chunk_size=2000,
    # 分块之间的重叠大小
    chunk_overlap=20,
)

# 将页面内容分块
texts = text_splitter.split_text(document.page_content)

# 仅处理前 3 个分块以节省时间
first_few = texts[:3]

# 初始化提取的关键信息列表
key_developments = []

# 遍历分块，并调用 DeepSeek 提取信息
for text in first_few:
    developments = extract_key_developments_from_text(text)
    key_developments.extend(developments)


for kd in key_developments[:10]:
    print(f"年份: {kd.year}, 描述: {kd.description}, 证据: {kd.evidence}")