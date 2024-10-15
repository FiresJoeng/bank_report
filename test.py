import docx_to_md

def load_file(docx_input, md_output):
    docx_to_md.convert(docx_input, md_output)
    with open(md_output, 'r', encoding='utf-8') as load_md_file:
        md_content = load_md_file.read()
    return md_content

docx_path = "./docx_files/广东省电子信息产业集团有限公司-企业基础信用报告-20241015155110.docx"
md_path = "./md_files/广东省电子信息产业集团有限公司-企业基础信用报告-20241015155110.md"
enterprise_info = load_file(docx_path, md_path)