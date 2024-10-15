reference_report = './md_files/仅首页_晶正鑫：固定资产贷款调查报告20220512.md'
with open(reference_report, 'r', encoding='utf-8') as load_md_file:
    reference_report = load_md_file.read()
print(reference_report)
