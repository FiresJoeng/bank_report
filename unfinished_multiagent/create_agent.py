from langchain.agents import AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import Tool,tool
from langchain.agents import initialize_agent, AgentType , AgentExecutor, Tool
import google.generativeai as genai
from typing import List
import os
from logger import setup_logger
from state_1 import NoteState 
from langchain.output_parsers import PydanticOutputParser

# Set up logger
logger = setup_logger()

@tool
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

def list_directory_contents(directory: str = './data_storage/') -> str:
    """
    List the contents of the specified directory.
    
    Args:
        directory (str): The path to the directory to list. Defaults to the data storage directory.
    
    Returns:
        str: A string representation of the directory contents.
    """
    try:
        logger.info(f"Listing contents of directory: {directory}")
        contents = os.listdir(directory)
        logger.debug(f"Directory contents: {contents}")
        return f"Directory contents:\n" + "\n".join(contents)
    except Exception as e:
        logger.error(f"Error listing directory contents: {str(e)}")
        return f"Error listing directory contents: {str(e)}"

def create_agent(
    llm: ChatGoogleGenerativeAI,
    tools: List[Tool],
    system_message: str,
    team_members: List[str],
    working_directory: str = './data_storage/'
) -> AgentExecutor:
    """
    Create an agent with the given language model, tools, system message, and team members.
    
    Parameters:
        llm (ChatGoogleGenerativeAI): The language model to use for the agent.
        tools (List[Tool]): A list of tools the agent can use.
        system_message (str): A message defining the agent's role and tasks.
        team_members (List[str]): A list of team member roles for collaboration.
        working_directory (str): The directory where the agent's data will be stored.
        
    Returns:
        AgentExecutor: An executor that manages the agent's task execution.
    """
    
    logger.info("Creating agent")

    # Ensure the ListDirectoryContents tool is available
    if list_directory_contents not in tools:
        tools.append(list_directory_contents)

    # Prepare the tool names and team members for the system prompt
    tool_names = ", ".join([tool.name for tool in tools])
    team_members_str = ", ".join(team_members)

    # List the initial contents of the working directory
    initial_directory_contents = list_directory_contents(working_directory)

    # Create the system prompt for the agent
    system_prompt = (
        "You are a specialized AI assistant in a data analysis team. "
        "Your role is to complete specific tasks in the research process. "
        "Use the provided tools to make progress on your task. "
        "If you can't fully complete a task, explain what you've done and what's needed next. "
        "Always aim for accurate and clear outputs. "
        f"You have access to the following tools: {tool_names}. "
        f"Your specific role: {system_message}\n"
        "Work autonomously according to your specialty, using the tools available to you. "
        "Do not ask for clarification. "
        "Your other team members (and other teams) will collaborate with you based on their specialties. "
        f"You are one of the following team members: {team_members_str}.\n"
        f"The initial contents of your working directory are:\n{initial_directory_contents}\n"
        "Use the ListDirectoryContents tool to check for updates in the directory contents when needed."
    )

    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        agent_kwargs={
            "system_message": system_prompt,
            "extra_prompt_messages": [MessagesPlaceholder(variable_name="messages")]
        }
    )
    
    logger.info("Agent created successfully")
    return agent

def create_note_agent(
    llm: ChatGoogleGenerativeAI,
    tools: List[Tool],
    system_prompt: str,
) -> AgentExecutor:
    """
    Create a note agent using the Gemini model.
    """
    logger.info("Creating note agent")
    
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        agent_kwargs={
            "system_message": system_prompt,
            "extra_prompt_messages": [MessagesPlaceholder(variable_name="messages")]
        }
    )
    
    logger.info("Note agent created successfully")
    return agent

logger.info("Agent creation module initialized")

#main版本的代码