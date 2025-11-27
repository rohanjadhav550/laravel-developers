from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from app.database import get_llm_config
from app.tools.memory_tool import save_requirements
import os

def get_llm():
    config = get_llm_config()
    if not config:
        raise ValueError(
            "AI configuration not found. Please configure your AI settings at "
            "http://localhost:8000/settings/ai with your OpenAI or Anthropic API key."
        )

    if config['provider'] == 'OpenAI':
        return ChatOpenAI(api_key=config['api_key'], model="gpt-4o")
    elif config['provider'] == 'Anthropic':
        return ChatAnthropic(api_key=config['api_key'], model="claude-3-5-sonnet-20240620")

    raise ValueError(f"Unsupported AI provider: {config['provider']}")

def get_requirement_agent():
    llm = get_llm()
    tools = [save_requirements]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert Requirement Gathering Agent. Your goal is to have a conversation with the user to understand their needs for a Laravel project. "
                   "Ask clarifying questions to gather all necessary details. Once you have a clear understanding, use the 'save_requirements' tool to save them. "
                   "Do not propose technical solutions yet, just focus on the 'what' and 'why'."),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    agent = prompt | llm.bind_tools(tools)
    return agent
