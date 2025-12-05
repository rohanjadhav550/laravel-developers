from langchain_community.vectorstores import Redis
from langchain_openai import OpenAIEmbeddings
from langchain.tools import tool
import os

# Initialize Embeddings
# Note: We might need to make this dynamic based on the provider, but for now assuming OpenAI embeddings are fine or we can switch to HuggingFace if needed.
# Since the user has OpenAI/Anthropic keys, we'll try to use OpenAI embeddings if available, or fallback.
# For simplicity in this step, I'll assume OpenAI embeddings.

def get_vector_store(agent_type: str = "default"):
    """
    Get vector store with agent-specific index.

    Args:
        agent_type: Agent type (requirement_agent, developer_agent, generic)
                   Defaults to "default" for backward compatibility

    Returns:
        Redis vector store instance
    """
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
    embeddings = OpenAIEmbeddings() # Requires OPENAI_API_KEY to be set in env or passed

    # Dynamic index name based on agent type
    # Pattern: kb_{agent_type} (e.g., kb_requirement_agent, kb_developer_agent)
    # Falls back to "laravel_docs" for backward compatibility
    if agent_type and agent_type != "default":
        index_name = f"kb_{agent_type}"
    else:
        index_name = "laravel_docs"

    vector_store = Redis(
        redis_url=redis_url,
        embedding=embeddings,
        index_name=index_name,
    )
    return vector_store

@tool
def search_knowledge_base(query: str, agent_type: str = "default"):
    """
    Searches the agent-specific knowledge base for relevant information.

    Args:
        query: Search query
        agent_type: Agent type (automatically injected from context)

    Returns:
        Relevant knowledge base content or error message
    """
    try:
        vector_store = get_vector_store(agent_type)
        results = vector_store.similarity_search(query, k=3)
        return "\n\n".join([doc.page_content for doc in results])
    except Exception as e:
        return f"Error searching knowledge base: {e}"
