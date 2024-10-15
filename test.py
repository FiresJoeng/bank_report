# Before running this script, please install docx2md first
# pip install docx2md

import subprocess

# 定义输入和输出文件路径
docx_file = './docx_files/仅页1_固定资产贷款调查报告模板.docx'
md_file = './md_files/仅页1_固定资产贷款调查报告模板.md'

# 构建命令行命令
command = f"python -m docx2md {docx_file} {md_file}"

# 调用命令行接口
subprocess.run(command, shell=True)

print(f"转换完成，输出文件保存在: {md_file}")