from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from app.agents.requirement_agent import get_requirement_agent
from app.tools.memory_tool import save_requirements
from langchain_core.tools import Tool
import operator
import os

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    next_step: str
    current_agent: str  # Track which agent is currently active

def requirement_node(state: AgentState, config: RunnableConfig):
    # Extract AI configuration from config
    user_id = config.get("configurable", {}).get("user_id", 2)
    ai_provider = config.get("configurable", {}).get("ai_provider")
    ai_api_key = config.get("configurable", {}).get("ai_api_key")

    agent = get_requirement_agent(user_id=user_id, ai_provider=ai_provider, ai_api_key=ai_api_key)
    messages = state['messages']
    response = agent.invoke(messages)
    return {"messages": [response], "current_agent": "requirement_agent"}

# Tools execution node - simplified for requirements gathering only
def tool_node(state: AgentState, config: RunnableConfig):
    messages = state['messages']
    last_message = messages[-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        # Get thread_id from config
        thread_id = config.get("configurable", {}).get("thread_id")

        # Process ALL tool calls
        tool_messages = []
        next_step = "end"  # End conversation after saving requirements

        for tool_call in last_message.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            tool_call_id = tool_call['id']

            if tool_name == 'save_requirements':
                # Add thread_id to tool args
                tool_args['thread_id'] = thread_id
                result = save_requirements.invoke(tool_args)
                tool_messages.append(ToolMessage(content=str(result), tool_call_id=tool_call_id))
                # Note: Developer agent will be triggered manually via separate endpoint
            else:
                # Handle unknown tools with an error message
                tool_messages.append(
                    ToolMessage(
                        content=f"Error: Unknown tool '{tool_name}'",
                        tool_call_id=tool_call_id
                    )
                )

        return {"messages": tool_messages, "next_step": next_step}

    return {"messages": []}

workflow = StateGraph(AgentState)

# Add only requirement agent and tools nodes
workflow.add_node("requirement_agent", requirement_node)
workflow.add_node("tools", tool_node)

# Set entry point - always start with requirement agent
workflow.set_entry_point("requirement_agent")

# Define conditional routing for requirement agent
def requirement_conditional(state: AgentState):
    last_message = state['messages'][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"  # Go to tools if agent wants to call a tool
    return END  # End conversation and wait for user input

# Define conditional routing for tools
def tool_conditional(state: AgentState):
    if state.get("next_step") == "end":
        return END  # End conversation after saving requirements
    return "requirement_agent"  # Continue with requirement agent if needed

# Simplified workflow:
# 1. Start with Requirement Agent
# 2. User converses through 7 stages
# 3. Requirement Agent calls save_requirements tool
# 4. Conversation ends
# 5. Developer Agent is triggered MANUALLY via separate /publish endpoint

workflow.add_conditional_edges(
    "requirement_agent",
    requirement_conditional,
    {
        "tools": "tools",
        END: END
    }
)

workflow.add_conditional_edges(
    "tools",
    tool_conditional,
    {
        "requirement_agent": "requirement_agent",
        END: END
    }
)

# Use RedisSaver for persistent conversation storage across restarts
from langgraph.checkpoint.redis import RedisSaver

# Initialize RedisSaver with Redis connection string
redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
checkpointer = RedisSaver(redis_url)

# Ensure Redis Search indices are created
checkpointer.setup()

app_graph = workflow.compile(checkpointer=checkpointer)
