from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.agents.requirement_agent import get_llm
from app.tools.rag_tool import search_knowledge_base
from app.tools.memory_tool import save_solution

def get_developer_agent():
    llm = get_llm()
    tools = [search_knowledge_base, save_solution]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert Laravel Developer Agent. Your goal is to propose technical solutions based on the requirements provided. "
                   "You should plan the database schema, decide on packages, and outline the architecture. "
                   "You do NOT write code, but you propose feasible solutions. "
                   "Use the 'search_knowledge_base' tool to find relevant information about Laravel packages and best practices if needed. "
                   "Once you have a solid plan, use the 'save_solution' tool to save it."),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    agent = prompt | llm.bind_tools(tools)
    return agent
