import docx

# 读取 Word 文档
def read_docx(file_path):
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

# 转换为 Markdown 格式
def convert_to_md(text):
    md_text = text
    # 简单转换为标题 (假设每一段第一个单词为 'Heading' 表示为标题)
    md_text = md_text.replace('\nHeading', '\n# Heading')  # 将文档中类似标题的部分转为 Markdown 的 #
    return md_text

# 保存为 Markdown 文件
def save_md(md_text, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_text)

# 示例用法
docx_file = 'your_word_file.docx'
md_file = 'output_file.md'

word_text = read_docx(docx_file)
md_text = convert_to_md(word_text)
save_md(md_text, md_file)

print(f"Markdown 文件已保存至: {md_file}")
