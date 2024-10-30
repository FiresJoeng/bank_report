from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, Tool
from langchain.prompts import ChatPromptTemplate

def create_google_genai_functions_agent(llm, tools, prompt):
    # 这里实现创建 Google Gemini 代理的逻辑
    # 可以使用 ChatGoogleGenerativeAI 和其他 langchain 组件
    gemini_llm = ChatGoogleGenerativeAI(model="gemini-pro")
    
    # 创建代理
    agent = AgentExecutor.from_agent_and_tools(
        agent=gemini_llm,
        tools=tools,
        prompt=prompt,
        verbose=True
    )
    
    return agent
#已弃用