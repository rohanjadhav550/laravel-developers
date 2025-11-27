from langchain.tools import tool

# Simple in-memory storage for the session. 
# In a production app, this should be persisted to a database or Redis.
session_memory = {
    "requirements": [],
    "solutions": []
}

@tool
def save_requirements(requirements: str):
    """Saves the gathered requirements to memory."""
    session_memory["requirements"].append(requirements)
    return "Requirements saved successfully."

@tool
def save_solution(solution: str):
    """Saves the proposed solution to memory."""
    session_memory["solutions"].append(solution)
    return "Solution saved successfully."

def get_memory():
    return session_memory
