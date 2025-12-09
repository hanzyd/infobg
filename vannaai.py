#!/usr/bin/env python3

# All imports at the top
from vanna import Agent, AgentConfig
from vanna.core.registry import ToolRegistry
from vanna.core.user import UserResolver, User, RequestContext
from vanna.tools import RunSqlTool, VisualizeDataTool
from vanna.tools.agent_memory import SaveQuestionToolArgsTool, SearchSavedCorrectToolUsesTool, SaveTextMemoryTool
from vanna.servers.fastapi import VannaFastAPIServer
from vanna.integrations.ollama import OllamaLlmService
from vanna.integrations.postgres import PostgresRunner
from vanna.integrations.local.agent_memory import DemoAgentMemory

# Configure your LLM
llm = OllamaLlmService(
    model="gpt-oss:20b",
    host="http://localhost:11434"
)

# Configure your database
db_tool = RunSqlTool(
    sql_runner=PostgresRunner(connection_string="postgresql://localhost/infobg")
)

# Configure your agent memory
agent_memory = DemoAgentMemory(max_items=1000)

# Configure user authentication
class SimpleUserResolver(UserResolver):
    async def resolve_user(self, request_context: RequestContext) -> User:
        user_email = request_context.get_cookie('vanna_email') or 'guest@example.com'
        group = 'admin' if user_email == 'admin@example.com' else 'user'
        return User(id=user_email, email=user_email, group_memberships=[group])

user_resolver = SimpleUserResolver()

# Create your agent
tools = ToolRegistry()
tools.register_local_tool(db_tool, access_groups=['admin', 'user'])
tools.register_local_tool(SaveQuestionToolArgsTool(), access_groups=['admin'])
tools.register_local_tool(SearchSavedCorrectToolUsesTool(), access_groups=['admin', 'user'])
tools.register_local_tool(SaveTextMemoryTool(), access_groups=['admin', 'user'])
tools.register_local_tool(VisualizeDataTool(), access_groups=['admin', 'user'])

config = AgentConfig(
    max_tokens=2000,
    # Default is likely a low number (e.g., 2 or 3).
    # THIS IS THE LINE TO CHANGE:
    max_tool_iterations=100,
    temperature=0.6,
)

agent = Agent(
    llm_service=llm,
    tool_registry=tools,
    user_resolver=user_resolver,
    agent_memory=agent_memory,
    config=config
)

# Run the server
server = VannaFastAPIServer(agent)
server.run()  # Access at http://localhost:8000