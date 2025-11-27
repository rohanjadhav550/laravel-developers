from langchain_community.vectorstores import Redis
from langchain_openai import OpenAIEmbeddings
from langchain.tools import tool
import os

# Initialize Embeddings
# Note: We might need to make this dynamic based on the provider, but for now assuming OpenAI embeddings are fine or we can switch to HuggingFace if needed.
# Since the user has OpenAI/Anthropic keys, we'll try to use OpenAI embeddings if available, or fallback.
# For simplicity in this step, I'll assume OpenAI embeddings.

def get_vector_store():
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
    embeddings = OpenAIEmbeddings() # Requires OPENAI_API_KEY to be set in env or passed
    
    # We need to ensure the index exists. 
    # In a real app, we'd have an ingestion pipeline. 
    # For now, we'll just connect to an existing one or create a dummy one if needed.
    
    vector_store = Redis(
        redis_url=redis_url,
        embedding=embeddings,
        index_name="laravel_docs",
    )
    return vector_store

@tool
def search_knowledge_base(query: str):
    """Searches the knowledge base for relevant information about Laravel development, packages, and best practices."""
    try:
        vector_store = get_vector_store()
        results = vector_store.similarity_search(query, k=3)
        return "\n\n".join([doc.page_content for doc in results])
    except Exception as e:
        return f"Error searching knowledge base: {e}"
