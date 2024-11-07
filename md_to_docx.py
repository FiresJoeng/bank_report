# Before running this script, please install python-docx first
# pip install python-docx

from docx import Document


def convert_md_to_docx(input_md, output_docx):
    try:
        with open(input_md, 'r', encoding='utf-8') as file:
            content = file.read()
        doc = Document()
        doc.add_paragraph(content)
        doc.save(output_docx)
        print(f"[提示] 转换{output_docx}成功!")
    except Exception as e:
        print(f"[错误] 转换{input_md}失败! 原因: {e}")
        exit()
