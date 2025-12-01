from langchain.tools import tool
from app.database import save_requirements_to_laravel, save_solution_to_laravel, update_solution_requirements, update_solution_technical
import requests
import os

# Simple in-memory storage for the session (fallback)
# Primary storage is in Laravel MySQL database
session_memory = {
    "requirements": [],
    "solutions": []
}

@tool
def save_requirements(requirements: str, thread_id: str = None):
    """
    Saves the gathered requirements to Laravel database in markdown format.
    This is called after all 7 stages of requirement gathering are complete.

    Args:
        requirements: The complete requirements document in markdown format
        thread_id: The conversation thread ID
    """
    # Save to in-memory (fallback)
    session_memory["requirements"].append(requirements)

    # Note: Database persistence is handled by main.py after graph completion
    # to avoid deadlock with single-threaded Laravel server

    if thread_id:
        print(f"Requirements marked for saving (thread: {thread_id}, length: {len(requirements)} chars)")
        return "Requirements saved successfully to the database. The developer agent will now propose a technical solution based on these requirements."
    else:
        return "Requirements saved to session memory only (no thread_id provided)."

@tool
def save_solution(solution: str, thread_id: str = None):
    """
    Saves the proposed technical solution to Laravel database in markdown format.

    Args:
        solution: The complete technical solution document in markdown format
        thread_id: The conversation thread ID
    """
    # Save to in-memory (fallback)
    session_memory["solutions"].append(solution)

    # Note: Database persistence is handled by main.py after graph completion
    # to avoid deadlock with single-threaded Laravel server

    if thread_id:
        print(f"Solution marked for saving (thread: {thread_id}, length: {len(solution)} chars)")
        return "Solution saved successfully to the database. The conversation is now complete."
    else:
        return "Solution saved to session memory only (no thread_id provided)."

def get_memory():
    return session_memory
