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

    # Save to Laravel database
    if thread_id:
        # Save to conversation table (legacy)
        result = save_requirements_to_laravel(thread_id, requirements)

        # Also update the solution table
        try:
            laravel_url = os.getenv("LARAVEL_API_URL", "http://laravel-app-dev:8000")
            # Get conversation ID from thread_id
            response = requests.get(
                f"{laravel_url}/api/internal/conversations/{thread_id}",
                timeout=5
            )
            if response.status_code == 200:
                conversation = response.json().get('data')
                if conversation and conversation.get('id'):
                    # Update solution requirements
                    update_solution_requirements(conversation['id'], requirements)
        except Exception as e:
            print(f"Error updating solution requirements: {e}")

        if result:
            return "Requirements saved successfully to the database. The developer agent will now propose a technical solution based on these requirements."
        else:
            return "Requirements saved to session memory, but failed to persist to database. Please check the connection to Laravel."
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

    # Save to Laravel database
    if thread_id:
        # Save to conversation table (legacy)
        result = save_solution_to_laravel(thread_id, solution)

        # Also update the solution table
        try:
            laravel_url = os.getenv("LARAVEL_API_URL", "http://laravel-app-dev:8000")
            # Get conversation ID from thread_id
            response = requests.get(
                f"{laravel_url}/api/internal/conversations/{thread_id}",
                timeout=5
            )
            if response.status_code == 200:
                conversation = response.json().get('data')
                if conversation and conversation.get('id'):
                    # Update solution technical solution
                    update_solution_technical(conversation['id'], solution)
        except Exception as e:
            print(f"Error updating solution technical solution: {e}")

        if result:
            return "Solution saved successfully to the database. The conversation is now complete."
        else:
            return "Solution saved to session memory, but failed to persist to database. Please check the connection to Laravel."
    else:
        return "Solution saved to session memory only (no thread_id provided)."

def get_memory():
    return session_memory
