import os
from logger import setup_logger
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph
import google.generativeai as genai
from load_cfg import GEMINI_API_KEY, LANGCHAIN_API_KEY, WORKING_DIRECTORY
from configs import generation_config_dictllm, generation_config_dict_power_llm, generation_config_dict_json_llm
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from tools.internet import google_search, scrape_webpages_with_fallback
from tools.FileEdit import collect_data
from langchain_community.tools import Tool
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_experimental.tools import PythonREPLTool
from router import QualityReview_router,hypothesis_router,process_router
from google_gemini_agent import create_google_genai_functions_agent
from dotenv import load_dotenv
from state import State
from typing import Any
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage,ToolMessage
import json
import re
from pathlib import Path
from langchain.agents import AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.output_parsers import StructuredOutputParser
from typing import List
from langchain.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from IPython.display import Image, display
from typing import Dict, Any

#加载 .env 文件
load_dotenv()

# 从环境变量中获取 SERPAPI_KEY
SERPAPI_KEY = os.getenv('SERPAPI_KEY')

# 如果 SERPAPI_KEY 为 None，给它一个默认值
if SERPAPI_KEY is None:
    SERPAPI_KEY = "默认值或空字符串"

# 设置环境变量
os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
os.environ["LANGCHAIN_TRACING_V2"] = "true" 
os.environ["LANGCHAIN_PROJECT"] = "Multi-Agent Data Analysis System"
os.environ["SERPAPI_KEY"] = SERPAPI_KEY

# 设置日志记录
logger = setup_logger()

# 确保工作目录存在
if not os.path.exists(WORKING_DIRECTORY):
    os.makedirs(WORKING_DIRECTORY)
    logger.info(f"Created working directory: {WORKING_DIRECTORY}")

logger.info("Initialization complete.")


# 设置代理（如果需要）
os.environ['https_proxy'] = 'http://127.0.0.1:7890'
os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['all_proxy'] = 'socks5://127.0.0.1:7890'

#我本地读不了node.py 所这里直接导入 为了方便管理 还是放在node.py里比较好
#node从这里开始
def agent_node(state: State, agent: AgentExecutor, name: str) -> State:
    logger.info(f"Entering agent_node for {name}")
    logger.debug(f"Input state: {state}")
    try:
        result = agent.invoke(state)
        logger.debug(f"Agent {name} result: {result}")
        
        output = result["output"] if isinstance(result, dict) and "output" in result else str(result)
        
        ai_message = AIMessage(content=output, name=name)
        state["messages"].append(ai_message)
        state["sender"] = name
        
        # 确保至少更新一个状态字段
        state[f"{name.lower()}_state"] = output
        state["hypothesis"] = output  # 确保更新 hypothesis 字段
        
        logger.info(f"Exiting agent_node for {name}")
        logger.debug(f"Output state: {state}")
        return state
    except Exception as e:
        logger.error(f"Error in agent_node for {name}: {str(e)}", exc_info=True)
        error_message = AIMessage(content=f"Error: {str(e)}", name=name)
        state["messages"].append(error_message)
        state[f"{name.lower()}_error"] = str(e)
        return state

def human_choice_node(state: State) -> State:
    logger.info("Prompting for human choice")
    print("Please choose the next step:")
    print("1. Regenerate hypothesis")
    print("2. Continue the research process")
    
    while True:
        choice = input("Please enter your choice (1 or 2): ")
        if choice in ["1", "2"]:
            break
        logger.warning(f"Invalid input received: {choice}")
        print("Invalid input, please try again.")
    
    if choice == "1":
        modification_areas = input("Please specify which parts of the hypothesis you want to modify: ")
        content = f"Regenerate hypothesis. Areas to modify: {modification_areas}"
        state["hypothesis"] = ""
        state["modification_areas"] = modification_areas
        logger.info("Hypothesis cleared for regeneration")
        logger.info(f"Areas to modify: {modification_areas}")
    else:
        content = "Continue the research process"
        state["process"] = "Continue the research process"
        logger.info("Continuing research process")
    
    human_message = HumanMessage(content=content)
    
    state["messages"].append(human_message)
    state["sender"] = 'human'
    
    logger.info("Human choice processed")
    return state

def create_message(message: dict[str], name: str) -> BaseMessage:
    """
    Create a BaseMessage object based on the message type.
    """
    content = message.get("content", "")
    message_type = message.get("type", "").lower()
    
    logger.debug(f"Creating message of type {message_type} for {name}")
    return HumanMessage(content=content) if message_type == "human" else AIMessage(content=content, name=name)

def create_error_state(state: State, error_message: AIMessage, name: str, error_type: str) -> State:
    """
    Create an error state when an exception occurs.
    """
    logger.info(f"Creating error state for {name}: {error_type}")
    error_state:State = {
            "messages": state.get("messages", []) + [error_message],
            "hypothesis": str(state.get("hypothesis", "")),
            "process": str(state.get("process", "")),
            "process_decision": str(state.get("process_decision", "")),
            "visualization_state": str(state.get("visualization_state", "")),
            "searcher_state": str(state.get("searcher_state", "")),
            "code_state": str(state.get("code_state", "")),
            "report_section": str(state.get("report_section", "")),
            "quality_review": str(state.get("quality_review", "")),
            "needs_revision": bool(state.get("needs_revision", False)),
            "sender": 'note_agent'
        }
    return error_state
def note_agent_node(state: State, agent: AgentExecutor, name: str) -> State:
    """
    Process the note agent's action and update the entire state.
    """
    logger.info(f"Processing note agent: {name}")
    try:
        current_messages = state.get("messages", [])
        
        head_messages, tail_messages = [], []
        
        if len(current_messages) > 6:
            head_messages = current_messages[:2] 
            tail_messages = current_messages[-2:]
            state = {**state, "messages": current_messages[2:-2]}
            logger.debug("Trimmed messages for processing")
        
        result = agent.invoke(state)
        logger.debug(f"Note agent {name} result: {result}")
        output = result["output"] if isinstance(result, dict) and "output" in result else str(result)

        cleaned_output = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', output)
        parsed_output = json.loads(cleaned_output)
        logger.debug(f"Parsed output: {parsed_output}")

        new_messages = [create_message(msg, name) for msg in parsed_output.get("messages", [])]
        
        messages = new_messages if new_messages else current_messages
        
        combined_messages = head_messages + messages + tail_messages
        
        updated_state: State = {
            "messages": combined_messages,
            "hypothesis": str(parsed_output.get("hypothesis", state.get("hypothesis", ""))),
            "process": str(parsed_output.get("process", state.get("process", ""))),
            "process_decision": str(parsed_output.get("process_decision", state.get("process_decision", ""))),
            "visualization_state": str(parsed_output.get("visualization_state", state.get("visualization_state", ""))),
            "searcher_state": str(parsed_output.get("searcher_state", state.get("searcher_state", ""))),
            "code_state": str(parsed_output.get("code_state", state.get("code_state", ""))),
            "report_section": str(parsed_output.get("report_section", state.get("report_section", ""))),
            "quality_review": str(parsed_output.get("quality_review", state.get("quality_review", ""))),
            "needs_revision": bool(parsed_output.get("needs_revision", state.get("needs_revision", False))),
            "sender": 'note_agent'
        }
        
        logger.info("Updated state successfully")
        return updated_state

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}", exc_info=True)
        return create_error_state(state, AIMessage(content=f"Error parsing output: {output}", name=name), name, "JSON decode error")
#这里删了openai的异常处理函数 感觉无伤大雅
    except Exception as e:
        logger.error(f"Unexpected error in note_agent_node: {e}", exc_info=True)
        return create_error_state(state, AIMessage(content=f"Unexpected error: {str(e)}", name=name), name, "Unexpected error")


def human_review_node(state: State) -> State:
    """
    Display current state to the user and update the state based on user input.
    Includes error handling for robustness.
    """
    try:
        print("Current research progress:")
        print(state)
        print("\nDo you need additional analysis or modifications?")
        
        while True:
            user_input = input("Enter 'yes' to continue analysis, or 'no' to end the research: ").lower()
            if user_input in ['yes', 'no']:
                break
            print("Invalid input. Please enter 'yes' or 'no'.")
        
        if user_input == 'yes':
            while True:
                additional_request = input("Please enter your additional analysis request: ").strip()
                if additional_request:
                    state["messages"].append(HumanMessage(content=additional_request))
                    state["needs_revision"] = True
                    break
                print("Request cannot be empty. Please try again.")
        else:
            state["needs_revision"] = False
        
        state["sender"] = "human"
        logger.info("Human review completed successfully.")
        return state
    
    except KeyboardInterrupt:
        logger.warning("Human review interrupted by user.")
        return None
    
    except Exception as e:
        logger.error(f"An error occurred during human review: {str(e)}", exc_info=True)
        return None
    
def refiner_node(state: State, agent: AgentExecutor, name: str) -> State:
    """
    Read MD file contents and PNG file names from the specified storage path,
    add them as report materials to a new message,
    then process with the agent and update the original state.
    If token limit is exceeded, use only MD file names instead of full content.
    """
    try:
        # Get storage path
        storage_path = Path(os.getenv('STORAGE_PATH', './data_storage/'))
        
        # Collect materials
        materials = []
        md_files = list(storage_path.glob("*.md"))
        png_files = list(storage_path.glob("*.png"))
        
        # Process MD files
        for md_file in md_files:
            with open(md_file, "r", encoding="utf-8") as f:
                materials.append(f"MD file '{md_file.name}':\n{f.read()}")
        
        # Process PNG files
        materials.extend(f"PNG file: '{png_file.name}'" for png_file in png_files)
        
        # Combine materials
        combined_materials = "\n\n".join(materials)
        report_content = f"Report materials:\n{combined_materials}"
        
        # Create refiner state
        refiner_state = state.copy()
        refiner_state["messages"] = [BaseMessage(content=report_content)]
        
        try:
            # Attempt to invoke agent with full content
            result = agent.invoke(refiner_state)
        except Exception as token_error:
            # If token limit is exceeded, retry with only MD file names
            logger.warning("Token limit exceeded. Retrying with MD file names only.")
            md_file_names = [f"MD file: '{md_file.name}'" for md_file in md_files]
            png_file_names = [f"PNG file: '{png_file.name}'" for png_file in png_files]
            
            simplified_materials = "\n".join(md_file_names + png_file_names)
            simplified_report_content = f"Report materials (file names only):\n{simplified_materials}"
            
            refiner_state["messages"] = [BaseMessage(content=simplified_report_content)]
            result = agent.invoke(refiner_state)
        
        # Update original state
        state["messages"].append(AIMessage(content=result))
        state["sender"] = name
        
        logger.info("Refiner node processing completed")
        return state
    except Exception as e:
        logger.error(f"Error occurred while processing refiner node: {str(e)}", exc_info=True)
        state["messages"].append(AIMessage(content=f"Error: {str(e)}", name=name))
        return state
    
logger.info("Agent processing module initialized")
#node到这里

#create_agent的内容在这里
@tool
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
        return f"Directory contents :\n" + "\n".join(contents)
    except Exception as e:
        logger.error(f"Error listing directory contents: {str(e)}")
        return f"Error listing directory contents: {str(e)}"

def create_agent(
    llm: genai.GenerativeModel,
    tools: list[tool],
    system_message: str,
    team_members: list[str],
    working_directory: str = './data_storage/'
) -> AgentExecutor:
    """
    Create an agent with the given language model, tools, system message, and team members.
    
    Parameters:
        llm (genai.ChatModel): The language model to use for the agent.
        tools (list[tool]): A list of tools the agent can use.
        system_message (str): A message defining the agent's role and tasks.
        team_members (list[str]): A list of team member roles for collaboration.
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
    initial_directory_contents = list_directory_contents.invoke(working_directory)

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
        f"You are chosen for a reason! You are one of the following team members: {team_members_str}.\n"
        f"The initial contents of your working directory are:\n{initial_directory_contents}\n"
        "Use the ListDirectoryContents tool to check for updates in the directory contents when needed."
    )

    # Define the prompt structure with placeholders for dynamic content
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        ("ai", "hypothesis: {hypothesis}"),
        ("ai", "process: {process}"),
        ("ai", "process_decision: {process_decision}"),
        ("ai", "visualization_state: {visualization_state}"),
        ("ai", "searcher_state: {searcher_state}"),
        ("ai", "code_state: {code_state}"),
        ("ai", "report_section: {report_section}"),
        ("ai", "quality_review: {quality_review}"),
        ("ai", "needs_revision: {needs_revision}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Create the agent using the defined prompt and tools
    agent = create_google_genai_functions_agent(llm=llm, tools=tools, prompt=prompt)
    
    logger.info("Agent created successfully")
    
    # Return an executor to manage the agent's task execution
    return AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=False)



def structured_output_parser(output: str) -> Dict[str, Any]:
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        # 如果不是有效的 JSON，尝试解析为键值对
        result = {}
        for line in output.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                result[key.strip()] = value.strip()
        return result

def create_supervisor(llm: genai.GenerativeModel, system_prompt: str, members: list[str]):
    logger.info("Creating supervisor")
    options = ["FINISH"] + members
    
    prompt_template = f"""
    {system_prompt}

    Given the conversation above, who should act next? Or should we FINISH? 
    Select one of: {options}. 
    Additionally, specify the task that the selected role should perform.

    Please format your response as a JSON object with the following structure:
    {{
        "next": "The next role to act",
        "task": "The task to be performed"
    }}

    Current conversation:
    {{messages}}
    """

    def supervisor_chain(state: Dict[str, Any]) -> Dict[str, Any]:
        messages = state.get("messages", [])
        formatted_messages = "\n".join([f"{m.type}: {m.content}" for m in messages])
        
        prompt = prompt_template.format(messages=formatted_messages)
        
        response = llm.generate_content(prompt)
        
        try:
            result = json.loads(response.text)
            return {
                "next": result["next"],
                "task": result["task"]
            }
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from model output: {response.text}")
            return {
                "next": "ERROR",
                "task": "Error occurred in supervisor. Please check the logs."
            }

    logger.info("Supervisor created successfully")
    return supervisor_chain


#state读不到notestate 所以创了一个功能类似的py文件
#已经放在create_agent.py里 可以删
from state_1 import NoteState 
from langchain.output_parsers import PydanticOutputParser

def create_note_agent(
    llm: ChatGoogleGenerativeAI,
    tools: list,
    system_prompt: str,
) -> AgentExecutor:
    """
    Create a Note Agent that updates the entire state.
    """
    logger.info("Creating note agent")
    parser = PydanticOutputParser(pydantic_object=NoteState)
    output_format = parser.get_format_instructions()
    escaped_output_format = output_format.replace("{", "{{").replace("}", "}}")
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt + "\n\nPlease format your response as a JSON object with the following structure:\n" + escaped_output_format),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    logger.debug(f"Note agent prompt: {prompt}")
    agent = create_google_genai_functions_agent(llm=llm, tools=tools, prompt=prompt)
    logger.info("Note agent created successfully")
    return AgentExecutor.from_agent_and_tools(
        agent=agent, 
        tools=tools, 
        verbose=False,
    )

logger.info("Agent creation module initialized")
#到这里

#router.py读不了 直接搞进来
import urllib
from urllib.parse import urlparse
import re

#: Regex for URL definitions.
_ROUTE_REGEX = re.compile(r'''
    \<            # The exact character "<"
    (\w*)         # The optional variable name (restricted to a-z, 0-9, _)
    (?::([^>]*))? # The optional :regex part
    \>            # The exact character ">"
    ''', re.VERBOSE)


class BaseRoute(object):
    """Interface for URL routes. Custom routes must implement some or all
    methods and attributes from this class.
    """
    #: Route name, used to build URLs.
    name = None
    #: True if this route is only used for URL generation and never matches.
    build_only = False

    def match(self, request):
        """Matches this route against the current request.

        :param request:
            A ``webob.Request`` instance.
        :returns:
            A tuple ``(handler, args, kwargs)`` if the route matches, or None.
        """
        raise NotImplementedError()

    def build(self, request, args, kwargs):
        """Builds and returns a URL for this route.

        :param request:
            The current ``Request`` object.
        :param args:
            Tuple of positional arguments to build the URL.
        :param kwargs:
            Dictionary of keyword arguments to build the URL.
        :returns:
            An absolute or relative URL.
        """
        raise NotImplementedError()

    def get_routes(self):
        """Generator to get all routes from a route.

        :yields:
            This route or all nested routes that it contains.
        """
        yield self

    def get_match_routes(self):
        """Generator to get all routes that can be matched from a route.

        :yields:
            This route or all nested routes that can be matched.
        """
        if not self.build_only:
            yield self
        elif not self.name:
            raise ValueError("Route %r is build_only but doesn't have a "
                "name" % self)

    def get_build_routes(self):
        """Generator to get all routes that can be built from a route.

        :yields:
            This route or all nested routes that can be built.
        """
        if self.name is not None:
            yield self


class Route(BaseRoute):
    """A URL route definition. A route template contains parts enclosed by
    ``<>`` and is used to match requested URLs. Here are some examples::

        route = Route(r'/article/<id:[\d]+>', ArticleHandler)
        route = Route(r'/wiki/<page_name:\w+>', WikiPageHandler)
        route = Route(r'/blog/<year:\d{4}>/<month:\d{2}>/<day:\d{2}>/<slug:\w+>', BlogItemHandler)

    Based on `Another Do-It-Yourself Framework`_, by Ian Bicking. We added
    URL building, non-keyword variables and other improvements.
    """
    def __init__(self, template, handler=None, name=None, defaults=None,
        build_only=False):
        """Initializes a URL route.

        :param template:
            A route template to be matched, containing parts enclosed by ``<>``
            that can have only a name, only a regular expression or both:

              =============================  ==================================
              Format                         Example
              =============================  ==================================
              ``<name>``                     ``r'/<year>/<month>'``
              ``<:regular expression>``      ``r'/<:\d{4}>/<:\d{2}>'``
              ``<name:regular expression>``  ``r'/<year:\d{4}>/<month:\d{2}>'``
              =============================  ==================================

            If the name is set, the value of the matched regular expression
            is passed as keyword argument to the :class:`RequestHandler`.
            Otherwise it is passed as positional argument.

            The same template can mix parts with name, regular expression or
            both.
        :param handler:
            A :class:`RequestHandler` class or dotted name for a class to be
            lazily imported, e.g., ``my.module.MyHandler``.
        :param name:
            The name of this route, used to build URLs based on it.
        :param defaults:
            Default or extra keywords to be returned by this route. Values
            also present in the route variables are used to build the URL
            when they are missing.
        :param build_only:
            If True, this route never matches and is used only to build URLs.
        """
        self.template = template
        self.handler = handler
        self.name = name
        self.defaults = defaults or {}
        self.build_only = build_only
        # Lazy properties.
        self.regex = None
        self.variables = None
        self.reverse_template = None

    def _parse_template(self):
        self.variables = {}
        last = count = 0
        regex = template = ''
        for match in _ROUTE_REGEX.finditer(self.template):
            part = self.template[last:match.start()]
            name = match.group(1)
            expr = match.group(2) or '[^/]+'
            last = match.end()

            if not name:
                name = '__%d__' % count
                count += 1

            template += '%s%%(%s)s' % (part, name)
            regex += '%s(?P<%s>%s)' % (re.escape(part), name, expr)
            self.variables[name] = re.compile('^%s$' % expr)

        regex = '^%s%s$' % (regex, re.escape(self.template[last:]))
        self.regex = re.compile(regex)
        self.reverse_template = template + self.template[last:]
        self.has_positional_variables = count > 0

    def _regex(self):
        if self.regex is None:
            self._parse_template()

        return self.regex

    def _variables(self):
        if self.variables is None:
            self._parse_template()

        return self.variables

    def _reverse_template(self):
        if self.reverse_template is None:
            self._parse_template()

        return self.reverse_template

    def match(self, request):
        """Matches this route against the current request.

        .. seealso:: :meth:`BaseRoute.match`.
        """
        regex = self.regex or self._regex()
        match = regex.match(request.path)
        if match:
            kwargs = self.defaults.copy()
            kwargs.update(match.groupdict())
            if kwargs and self.has_positional_variables:
                args = tuple(value[1] for value in sorted((int(key[2:-2]), \
                    kwargs.pop(key)) for key in \
                    kwargs.keys() if key.startswith('__')))
            else:
                args = ()

            return self.handler, args, kwargs

    def build(self, request, args, kwargs):
        """Builds a URL for this route.

        .. seealso:: :meth:`Router.build`.
        """
        return self._build(request, args, kwargs)[0]

    def _build(self, request, args, kwargs):
        """Builds the path for this route.

        :returns:
            A tuple ``(path, query)`` with the built URL path and extra
            keywords to be used as URL query arguments.
        """
        variables = self.variables or self._variables()
        if self.has_positional_variables:
            for index, value in enumerate(args):
                key = '__%d__' % index
                if key in variables:
                    kwargs[key] = value

        values = {}
        for name, regex in variables.iteritems():
            value = kwargs.pop(name, self.defaults.get(name))
            if not value:
                raise KeyError('Missing argument "%s" to build URL.' % \
                    name.strip('_'))

            if not isinstance(value, str):
                value = str(value)

            if not regex.match(value):
                raise ValueError('URL buiding error: Value "%s" is not '
                    'supported for argument "%s".' % (value, name.strip('_')))

            values[name] = value

        return (self.reverse_template % values, kwargs)


class Router(object):
    """A simple URL router used to match the current URL, dispatch the handler
    and build URLs for other resources.
    """
    #: Class used when the route is a tuple.
    route_class = Route

    def __init__(self, routes=None):
        """Initializes the router.

        :param routes:
            A list of :class:`Route` instances to initialize the router.
        """
        # All routes that can be matched.
        self.match_routes = []
        # All routes that can be built.
        self.build_routes = {}
        if routes:
            for route in routes:
                self.add(route)

    def add(self, route):
        """Adds a route to this router.

        :param route:
            A :class:`Route` instance.
        """
        if isinstance(route, tuple):
            # Default route.
            route = self.route_class(*route)

        for r in route.get_match_routes():
            self.match_routes.append(r)

        for r in route.get_build_routes():
            self.build_routes.setdefault(r.name, []).append(r)

    def match(self, request):
        """Matches all routes against the current request. The first one that
        matches is returned.

        :param request:
            A ``webob.Request`` instance.
        :returns:
            A tuple ``(route, args, kwargs)`` if a route matched, or None.
        """
        for route in self.match_routes:
            match = route.match(request)
            if match:
                return match

    def build(self, name, request, args, kwargs):
        """Builds and returns a URL for a named :class:`Route`.

        :param name:
            The route name.
        :param request:
            The current ``Request`` object.
        :param args:
            Tuple of positional arguments to build the URL.
        :param kwargs:
            Dictionary of keyword arguments to build the URL.
        :returns:
            An absolute or relative URL.
        """
        routes = self.build_routes.get(name)
        if not routes:
            raise KeyError('Route %r is not defined.' % name)

        best_match = None
        for route in routes:
            try:
                url, query = route._build(request, args, kwargs)
                query_count = len(query)
                if query_count == 0:
                    return url

                if best_match is None or query_count < best_match[0]:
                    best_match = (query_count, url)
            except (KeyError, ValueError) as e: 
                 print(f"An error occurred: {e}")

def to_utf8(value):
    """Returns a string encoded using UTF-8.

    This function comes from `Tornado`_.

    :param value:
    A unicode or string to be encoded.
    :returns:
    The encoded string.
    """
    # 在 Python 3 中，所有字符串都是 unicode，因此不需要单独处理 unicode
    if isinstance(value, str):
        return value.encode('utf-8')  # 将 str 编码为 UTF-8

    raise TypeError("Value must be a string")  # 如果不是字符串，抛出错误


def to_unicode(value):
    """Returns a unicode string from a string, using UTF-8 to decode if needed.

    This function comes from `Tornado`_.

    :param value:
        A unicode or string to be decoded.
    :returns:
        The decoded string.
    """
    if isinstance(value, str):
        return value.decode('utf-8')

    assert isinstance(value, str)
    return value


def urlunsplit(scheme=None, netloc=None, path=None, query=None, fragment=None):
    """Similar to ``urlparse.urlunsplit``, but will escape values and
    urlencode and sort query arguments.

    :param scheme:
        URL scheme, e.g., `http` or `https`.
    :param netloc:
        Network location, e.g., `localhost:8080` or `www.google.com`.
    :param path:
        URL path.
    :param query:
        URL query as an escaped string, or a dictionary or list of key-values
        tuples to build a query.
    :param fragment:
        Fragment identifier, also known as "anchor".
    :returns:
        An assembled absolute or relative URL.
    """
    if not scheme or not netloc:
        scheme = None
        netloc = None

    if path:
        path = urllib.quote_plus(to_utf8(path), '/')

    if query and not isinstance(query, str):
        if isinstance(query, dict):
            query = query.items()

        query_args = []
        for key, values in query:
            if isinstance(values, str):
                values = (values,)

            for value in values:
                query_args.append((to_utf8(key), to_utf8(value)))

        # Sorting should be optional? Sorted args are commonly needed to build
        # URL signatures for services.
        query_args.sort()
        query = urllib.urlencode(query_args)

    if fragment:
        fragment = urllib.quote_plus(to_utf8(fragment))

    return urlparse.urlunsplit((scheme, netloc, path, query, fragment))


# Create state graph for the workflow
workflow = StateGraph(State)


members = ["Hypothesis","Process","Visualization", "Search", "Coder", "Report", "QualityReview","Refiner"]

# 在第 28 行左右添加以下代码
try:
    # 模型设置
    llm = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config={
            **generation_config_dictllm,
            "temperature": 0.0,
            "max_output_tokens": 4096  # 相当于 max_tokens
        }
    )

    power_llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0.5,
        max_output_tokens=4096
    )

    json_llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0.0,
        max_output_tokens=4096
    )

    logger.info("Language models initialized successfully.")
except Exception as e:
    logger.error(f"Error initializing language models: {str(e)}")
    raise


from tools.internet import google_search,scrape_webpages_with_fallback
from tools.basetool import execute_code,execute_command
from tools.FileEdit import create_document,read_document,edit_document,collect_data

wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())


hypothesis_agent = create_agent(
    llm, 
    [collect_data, wikipedia, google_search, scrape_webpages_with_fallback] + load_tools(["arxiv"]),
    '''
    ��为数据分析领域的专家，您的任务是根据提供的信息表制定一系列研究假设，并概述基于这些假设的步骤。利用统计学、机器学习、深度学习和人工智能来制定这些假设。您的假设应当准确、可实现、专业且具有创新性。为了确保假设的可行性和独特性，请彻底调查相关信息。对于每个假设，请提供充分的参考资料以支持您的主张。

    在分析信息表后，您需要：

    1. 制定利用统计学、机器学习、深度学习和人工智能技术的研究假设。
    2. 概述测试这些假设所需的步骤。
    3. 通过全面的文献回顾验证每个假设的可行性和独特性。

    在分析结束时，呈现完整的研究假设，详细说明其独特性和可行性，并提供相关的参考资料以支持您的主张。请以结构化的方式回答，以增强可读性。
    仅回答研究假设。
    ''',
    members, WORKING_DIRECTORY
)


process_agent = create_supervisor(
    llm,  
    """
    您是负责监督和协调全面数据分析项目的研究主管，最终目标是生成完整且连贯���研究报告。您的主要任务包括：

    1. 验证和完善研究假设，以确保其清晰、具体且可测试。
    2. 组织全面的数据分析过程，确保所有代码都有良好的文档记录且可重复。
    3. 编写和完善研究报告，包括：
        - 引言
        - 假设
        - 方法论
        - 结果，附带相关的可视化
        - 讨论
        - 结论
        - 参考文献

    **逐步流程：**
    1. **规划：** 为项目的每个阶段定义明确的目标和预期结果。
    2. **任务分配：** 将具体任务分配给适当的代理（“可视化”、“搜索”、“编码”、“报告”）。
    3. **审查与整合：** 对每个代理的输出进行批判性审查和整合，确保一致性、质量和相关性。
    4. **反馈：** 根据需要提供反馈和进一步的指示，以完善输出。
    5. **最终汇编：** 确保所有组件逻辑上相互连接，并符合高标准的学术要求。

    **代理指南：**
    - **可视化代理：** 开发并解释有效传达关键发现的数据可视化。
    - **搜索代理：** 收集和总结相关信息，并编制全面的参考文献列表。
    - **编码代理：** 编写并记录用于数据分析的高效Python代码，确保代码清晰且可重复。
    - **报告代理：** 起草、完善并最终确定研究报告，整合所有代理的输入，确保叙述清晰且连贯。

    **工作流程：**
    1. 规划整体分析和报告过程。
    2. 将任务分配给适当的代理并监督其进展。
    3. 持续审查和整合每个代理的输出，确保每个代理有效地贡献于最终报告。
    4. 根据新出现的结果和见解调整分析和报告过程。
    5. 汇编最终报告，确保所有部分完整且良好整合。

    **完成标准：**
    仅在以下情况下响应“完成”：
    1. 假设已被彻底测试和验证。
    2. 数据分析已完成，所有代码都有文档记录且可重复。
    3. 所有所需的可视化已创建，标注正确并得到解释。
    4. 研究报告全面、结构合理，并包含所有必要部分。
    5. 参考文献列表完整且准确引用。
    6. 所有组件在最终报告中紧密整合。

    确保最终报告提供清晰、深刻的分析，涵盖假设的所有方面，并达到最高的学术标准。
    """,
    ["可视化", "搜索", "编码", "报告"]
)


visualization_agent = create_agent(
    llm, 
    [read_document, execute_code, execute_command],
    """
    您是一位数据可视化专家，负责创建数据的深刻可视化表现。您的主要职责包括：

    1. 设计适当的可视化，以清晰传达数据趋势和模式。
    2. 为不同的数据类型和分析目的选择最合适的图表类型（例如，条形图、散点图、热图）。
    3. 提供可执行的Python代码（使用matplotlib、seaborn或plotly等库）来生成这些可视化。
    4. 包括明确的标题、坐标轴标签、图例，并将可视化保存为文件。
    5. 提供对可视化结果的简要但清晰的解释。

    **文件保存指南：**
    - 将所有可视化保存为具有描述性和有意义的文件名的文件。
    - 确保文件名结构化，以便轻松识别内容（例如，'sales_trends_2024.png'用于销售趋势图）。
    - 确保保存的文件在工作目录中组织良好，便于其他代理查找和使用。

    **约束：**
    - 仅专注于可视化任务；不进行数据分析或处理。
    - 确保所有可视化元素适合目标受众，注意色彩方案和设计原则。
    - 避免过于复杂的可视化；追求清晰和简洁。
    """,
    members, WORKING_DIRECTORY
)

code_agent = create_agent(
    power_llm,
    [read_document, execute_code, execute_command],
    """
    您是一位专注于数据处理和分析的专家Python程序员。您的主要职责包括：

    1. 编写清晰、高效的Python代码，用于数据操作、清理和转换。
    2. 根据需要实现统计方法和机器学习算法。
    3. 调试和优化现有代码以提高性能。
    4. 遵循PEP 8标准，确保代码可读性，使用有意义的变量和函数名称。

    约束：
    - 仅专注于数据处理任务；不生成可视化或编写非Python代码。
    - 仅提供有效、可执行的Python代码，包括复杂逻辑的必要注释。
    - 避免不必要的复杂性；优先考虑可读性和效率。
    """,
    members, WORKING_DIRECTORY
)

searcher_agent = create_agent(
    llm,
    [create_document, read_document, collect_data, wikipedia, google_search, scrape_webpages_with_fallback] + load_tools(["arxiv"]),
    """
    您是一位熟练的研究助理，负责收集和总结相关信息。您的主要任务包括：

    1. 使用学术数据库和可靠的在线资源进行全面的文献回顾。
    2. 清晰、简洁地总结关键发现。
    3. 为所有来源提供引用，优先考虑经过同行评审和学术信誉良好的材料。

    约束：
    - 仅专注于信息检索和总结；不参与数据分析或处理。
    - 以有组织的格式呈现信息，清晰标注来源。
    - 评估来源的可信度，优先考虑高质量、可靠的信息。
    """,
    members, WORKING_DIRECTORY
)

report_agent = create_agent(
    power_llm, 
    [create_document, read_document, edit_document], 
    """
    您是一位经验丰富的科学作家，负责撰写全面的研究报告。您的主要职责包括：

    1. 在引言中清晰陈述研究假设和目标。
    2. 详细说明所用的方法，包括数据收集和分析技术。
    3. 将报告结构化为连贯的部分（例如，引言、方法论、结果、讨论、结论）。
    4. 将来自各种来源的信息综合成统一的叙述。
    5. 整合相关的数据可视化，并确保它们得到适当的引用和解释。

    约束：
    - 仅专注于报告写作；不进行数据分析或创建可视化。
    - 在整个报告中保持客观、学术的语气。
    - 使用APA格式引用所有来源，并确保所有发现都有证据支持。
    """,
    members, WORKING_DIRECTORY
)

quality_review_agent = create_agent(
    llm, 
    [create_document, read_document, edit_document], 
    '''
    您是一位细致的质量控制专家，负责审查和确保所有研究输出的高标准。您的任务包括：

    1. 批判性地评估研究报告的内容、方法和结论。
    2. 检查所有文档的一致性、准确性和清晰度。
    3. 确定需要改进或进一步阐述的部分。
    4. 确保遵循科学写作标准和伦理指南。

    在您的审查后，如果需要修订，请以“修订”为前缀响应，设置needs_revision=True，并提供需要改进的部分的具体反馈。如果不需要修订，请以“继续”为前缀响应，并设置needs_revision=False。
    ''',
    members, WORKING_DIRECTORY
)

note_agent = create_note_agent(
    json_llm, 
    [read_document], 
    '''
    您是一位细致的研究过程记录员。您的主要职责是观察、总结并记录研究团队的行动和发的任务包括：

    1. 观察并记录团队成员之间的关键活动、决策和讨论。
    2. 将复杂信息总结为清晰、简洁和准确的笔记。
    3. 以结构化格式组织笔记，确保易于检索和参考。
    4. 突出显示重要的见解、突破、挑战或任何偏离研究计划的情况。
    5. 仅以 JSON 格式响应，以确保结构化文档。

    您的输出应该组织良好，易于与其他项目文档集成。
    '''
)

refiner_agent = create_agent(
    power_llm,  
    [read_document, edit_document, create_document, collect_data, wikipedia, google_search, scrape_webpages_with_fallback] + load_tools(["arxiv"]),
    '''
    您是一位专家AI报告优化师，负责优化和增强研究报告。您的职责包括：

    1. 彻底审查整个研究报告，关注内容、结构和可读性。
    2. 确定并强调关键发现、见解和结论。
    3. 重新结构化报告，以改善清晰度、连贯性和逻辑流。
    4. 确保所有部分良好整合，并支持主要研究假设。
    5. 精简冗余或重复的内容，同时保留重要细节。
    6. 提高整体可读性，确保报告引人入胜且具有影响力。

    优化指南：
    - 保持原始内容的科学准确性和完整性。
    - 确保保留并清晰表达原始报告中的所有关键点。
    - 改善思想和论点的逻辑进展。
    - 突出最重要的结果及其对研究假设的影响。
    - 确保优化后的报告与最初的研究目标和假设一致。

    在优化报告后，提交给最终的人类审查，确保其准备好发布或展示。
    ''',
    members,  
    WORKING_DIRECTORY
)


def hypothesis_router(state: State):
    if state["hypothesis"]:
        return "HumanChoice"
    return "Hypothesis"


def process_router(state: State):
    logger.info(f"Routing from Process. Current process: {state['process']}")
    if "visualization" in state['process'].lower():
        return "Visualization"
    elif "search" in state['process'].lower():
        return "Search"
    elif "code" in state['process'].lower():
        return "Coder"
    elif "report" in state['process'].lower():
        return "Report"
    elif "refine" in state['process'].lower():
        return "Refiner"
    else:
        return "Process"


def QualityReview_router(state: State):
    if state.get("needs_revision", False):
        return "Process"
    elif state.get("quality_review", "") == "approved":
        return "HumanReview"
    else:
        return "Report"


workflow.add_node("Hypothesis", lambda state: agent_node(state, hypothesis_agent, "hypothesis_agent"))
workflow.add_node("Process", lambda state: agent_node(state, process_agent, "process_agent"))
workflow.add_node("Visualization", lambda state: agent_node(state, visualization_agent, "visualization_agent"))
workflow.add_node("Search", lambda state: agent_node(state, searcher_agent, "searcher_agent"))
workflow.add_node("Coder", lambda state: agent_node(state, code_agent, "code_agent"))
workflow.add_node("Report", lambda state: agent_node(state, report_agent, "report_agent"))
workflow.add_node("QualityReview", lambda state: agent_node(state, quality_review_agent, "quality_review_agent"))
workflow.add_node("NoteTaker", lambda state: note_agent_node(state, note_agent, "note_agent"))
workflow.add_node("HumanChoice", human_choice_node)
workflow.add_node("HumanReview", human_review_node)
workflow.add_node("Refiner", lambda state: refiner_node(state, refiner_agent, "refiner_agent"))


from langgraph.graph import END, START

# 起始边
workflow.add_edge(START, "Hypothesis")

# Hypothesis 相关边
workflow.add_conditional_edges(
    "Hypothesis",
    hypothesis_router,
    {
        "HumanChoice": "HumanChoice",
        "Hypothesis": "Hypothesis"
    }
)

# HumanChoice 相关边
workflow.add_conditional_edges(
    "HumanChoice",
    lambda state: "Process" if state["process"] else "Hypothesis",
    {
        "Process": "Process",
        "Hypothesis": "Hypothesis"
    }
)

# Process 相关边
workflow.add_conditional_edges(
    "Process",
    process_router,
    {
        "Visualization": "Visualization",
        "Search": "Search",
        "Coder": "Coder",
        "Report": "Report",
        "Process": "Process",
        "Refiner": "Refiner",
    }
)

# Visualization, Search, Coder, Refiner 返回到 Process
for node in ["Visualization", "Search", "Coder", "Refiner"]:
    workflow.add_edge(node, "Process")

# Report 到 QualityReview
workflow.add_edge("Report", "QualityReview")

# QualityReview 相关边
workflow.add_conditional_edges(
    "QualityReview",
    QualityReview_router,
    {
        "Process": "Process",
        "Report": "Report",
        "HumanReview": "HumanReview"
    }
)

# HumanReview 到结束或返回 Process
workflow.add_conditional_edges(
    "HumanReview",
    lambda state: "Process" if state.get("needs_revision", False) else END,
    {
        "Process": "Process",
        END: END
    }
)

# NoteTaker 可能需要在每个步骤后调用，所以可以添加到每个节点
for node in workflow.nodes:
    if node != "NoteTaker" and node != END:
        workflow.add_edge(node, "NoteTaker")
        workflow.add_edge("NoteTaker", node)

memory = MemorySaver()

print("Graph structure before compilation:")
for node in workflow.nodes:
    print(f"  {node}:")
    node_obj = workflow.nodes[node]
    if hasattr(node_obj, 'next'):
        print(f"    Next nodes: {node_obj.next}")
    if hasattr(node_obj, 'branch'):
        print(f"    Branch: {node_obj.branch}")

graph = workflow.compile()

print("Compiled graph structure:")
for node, node_obj in graph.nodes.items():
    print(f"  {node}:")
    if hasattr(node_obj, 'next'):
        print(f"    Next nodes: {node_obj.next}")
    if hasattr(node_obj, 'branch'):
        print(f"    Branch: {node_obj.branch}")

#display(Image(graph.get_graph().draw_mermaid_png()))


#OnlineSalesData.csv is my data set for demo
#在这里输入你的数据集路径及描述
userInput = '''
   datapath:BTC-USD_stock_data.csv
   使用机器学习对比特币价格数据进行分析,探索价格趋势和影响因素,并生成包含可视化的完整报告
   '''
#Here you can describe how you want your data to be processed


initial_state = {
    "messages": [HumanMessage(content=userInput)],
    "hypothesis": "",
    "process_decision": "",
    "process": "",
    "visualization_state": "",
    "searcher_state": "",
    "code_state": "",
    "report_section": "",
    "quality_review": "",
    "needs_revision": False,
    "sender": "",
}

events = graph.stream(
    initial_state,
    {"configurable": {"thread_id": "1"}, "recursion_limit": 3000},
    stream_mode="values",
    debug=True
)

try:
    for event in events:
        print(f"Event: {event}")
        for key, value in event.items():
            print(f"{key}: {value}")
        print("---")
except Exception as e:
    logger.error(f"Error during graph execution: {str(e)}", exc_info=True)