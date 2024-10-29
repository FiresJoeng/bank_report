import docx_to_md

def f_docx_to_md(docx_input, md_output):
    try:
        docx_to_md.convert_file(docx_input, md_output)
    except Exception as error:
        print(f"[错误] 转换{docx_input}失败! 原因: {error}")
        return None
    with open(md_output, 'r', encoding='utf-8') as load_md_file:
        md_content = load_md_file.read()
    return md_content


docx_path = "./docx_files/temp.docx"
md_path = "./md_files/temp.md"
enterprise_info = f_docx_to_md(docx_path, md_path)
print(enterprise_info)
