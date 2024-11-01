# bank_report


### 智能银行报告生成


##### 底层逻辑:
  1. 使用爬虫程序抓取目标企业信息 —> 保存并转换为md文件
  2. 读取 报告模板、现有案例报告
  3. 读取 企业信息
  4. AI用markdown语言回应，生成报告并复查优化
  5. 保存AI输出的结果并留存为docx文件
##### 以上，从第一步到第五步，就是银行智能报告生成的整体框架。


##### 主线任务(必须完成)：
  1. 现有的"报告模板"和"已有的参考案例报告"全部转换并加工成方便LLM处理的Markdown(.md)文件

    (1) 注意，如果我们现有的案例报告越多，那么我们的报告生成会越智能。你可以把这些现有的reports理解为数据集，数据越多AI越懂得该怎么样做。所以一旦我们做好了这个程序，请务必在测试阶段将我们比较满意的报告留存作为数据集的一部分。
  2. MultiAgent

    (1) 模板填充模块 (银行报告初次生成)
    (2) 复查优化模块 (报告纠错、优化、加工)
  ~~3. 企业信息抓取，具体要获得哪些信息参考"md_files/mapping.md"~~  *已完成*
  
  4. 生成的md报告转换为docx报告
  5. 优化工作

    (1) Agent Prompts的优化
    (2) 代码整理和封装


##### 支线任务(选择性完成)：
  1. 寻找一个对信息和文稿工作处理能力强的LLM

    (1) 并能够独立编写一个程序将其对接python
    (2) 根据后续工作将其合并至我们现有的Agent当中


##### 注意事项：
  1. 每次对项目文件进行编辑时，请务必先同步GitHub的数据
  2. 每次完成项目文件的编辑时，请保存并上传数据至GitHub


### 参考资料:

**爬虫程序**:
##### [企查查天眼查爬虫](https://github.com/bouxin/company-crawler/tree/master?tab=readme-ov-file)
##### [伪造浏览器用户代理](https://github.com/fake-useragent/fake-useragent)
##### [Firecrawl](https://github.com/mendableai/firecrawl)


**LLM相关**:
##### [MultiAgent](https://github.com/starpig1129/ai-data-analysis-MulitAgent)
##### [Paper QA](https://github.com/Future-House/paper-qa)
##### [Storm](https://github.com/stanford-oval/storm)
##### [Gemini 配置教程](https://github.com/FiresJoeng/py_genai_tutorial)


**编辑器**:
##### [Typora 破解版](https://github.com/markyin0707/typora-activation)
##### [Microsoft Visual Studio Code](https://code.visualstudio.com/)
##### [Cursor](https://www.cursor.com/)

**工具**
##### [Clash](https://github.com/Z-Siqi/Clash-for-Windows_Chinese)
