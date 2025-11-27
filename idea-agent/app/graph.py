from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from app.agents.requirement_agent import get_requirement_agent
from app.agents.developer_agent import get_developer_agent
from app.tools.rag_tool import search_knowledge_base
from app.tools.memory_tool import save_requirements, save_solution
from langchain_core.tools import Tool
from langgraph.checkpoint.memory import MemorySaver
import operator
import os

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    next_step: str

def requirement_node(state: AgentState):
    agent = get_requirement_agent()
    messages = state['messages']
    response = agent.invoke(messages)
    return {"messages": [response]}

def developer_node(state: AgentState):
    agent = get_developer_agent()
    messages = state['messages']
    response = agent.invoke(messages)
    return {"messages": [response]}

def router(state: AgentState):
    messages = state['messages']
    last_message = messages[-1]
    
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        tool_name = last_message.tool_calls[0]['name']
        if tool_name == 'save_requirements':
            return "developer"
        elif tool_name == 'save_solution':
            return END
        # Handle other tools if any, or continue conversation
        return "continue"
    
    # If no tool call, it's a conversation turn. 
    # We need to decide if we stay in the current agent or switch.
    # For simplicity, let's assume we stay in requirement gathering until requirements are saved.
    # But wait, the router needs to know which agent generated the message.
    # We can infer this from the graph structure or state.
    # A better approach might be to have explicit edges.
    
    return "continue"

# Tools execution node
def tool_node(state: AgentState):
    messages = state['messages']
    last_message = messages[-1]
    
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        tool_call = last_message.tool_calls[0]
        tool_name = tool_call['name']
        tool_args = tool_call['args']
        
        if tool_name == 'save_requirements':
            result = save_requirements.invoke(tool_args)
            return {"messages": [HumanMessage(content=str(result), name=tool_name)], "next_step": "developer"}
        elif tool_name == 'save_solution':
            result = save_solution.invoke(tool_args)
            return {"messages": [HumanMessage(content=str(result), name=tool_name)], "next_step": "end"}
        elif tool_name == 'search_knowledge_base':
            result = search_knowledge_base.invoke(tool_args)
            return {"messages": [HumanMessage(content=str(result), name=tool_name)], "next_step": "developer"}
            
    return {"messages": []}

workflow = StateGraph(AgentState)

workflow.add_node("requirement_agent", requirement_node)
workflow.add_node("developer_agent", developer_node)
workflow.add_node("tools", tool_node)

workflow.set_entry_point("requirement_agent")

def requirement_conditional(state: AgentState):
    last_message = state['messages'][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return END # Wait for user input

def developer_conditional(state: AgentState):
    last_message = state['messages'][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return END # Wait for user input

def tool_conditional(state: AgentState):
    if state.get("next_step") == "developer":
        return "developer_agent"
    elif state.get("next_step") == "end":
        return END
    # If it was a search tool, go back to developer
    return "developer_agent" 

# This logic is a bit simplified. 
# We need to handle the loop: User -> Agent -> (Tool -> Agent)* -> User
# LangGraph's prebuilt `create_react_agent` handles this well, but we are building custom.

# Let's refine the flow:
# 1. Start with Requirement Agent.
# 2. It converses with User until it calls `save_requirements`.
# 3. `save_requirements` triggers switch to Developer Agent.
# 4. Developer Agent converses/thinks (using RAG) until it calls `save_solution`.
# 5. `save_solution` ends the flow.

workflow.add_conditional_edges(
    "requirement_agent",
    requirement_conditional,
    {
        "tools": "tools",
        END: END
    }
)

workflow.add_conditional_edges(
    "developer_agent",
    developer_conditional,
    {
        "tools": "tools",
        END: END
    }
)

workflow.add_conditional_edges(
    "tools",
    tool_conditional,
    {
        "developer_agent": "developer_agent",
        END: END
    }
)

# Use MemorySaver for conversation persistence within the session
# Messages are stored in memory (will persist while container is running)
# Conversation metadata is still saved to MySQL database
checkpointer = MemorySaver()
app_graph = workflow.compile(checkpointer=checkpointer)
