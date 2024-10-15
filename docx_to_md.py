# Before running this script, please install docx2md first
# pip install docx2md

import subprocess

def convert(input_docx, output_md):
    try:
        docx2md_command = f"python -m docx2md {input_docx} {output_md}"
        subprocess.run(docx2md_command, shell=True, check=True)
        print(f"[提示] 转换成功，输出文件保存在: {output_md}\n")
    except Exception as e:
        print(f"[错误] 转换失败，原因: {e}")
        exit()