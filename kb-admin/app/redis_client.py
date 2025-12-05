"""
Redis client and utilities for vector store operations
"""
import redis
from redis.commands.search.field import TextField, NumericField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from typing import Optional, Dict, List
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Global Redis client
_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    """
    Get or create Redis client

    Returns:
        Redis client instance
    """
    global _redis_client

    if _redis_client is None:
        try:
            _redis_client = redis.from_url(
                settings.REDIS_URL,
                db=settings.REDIS_DB,
                decode_responses=False,  # Binary mode for vectors
            )
            # Test connection
            _redis_client.ping()
            logger.info(f"Redis client connected: {settings.REDIS_URL}")
        except redis.RedisError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    return _redis_client


def test_redis_connection() -> bool:
    """
    Test Redis connection

    Returns:
        True if connection successful
    """
    try:
        client = get_redis_client()
        return client.ping()
    except Exception as e:
        logger.error(f"Redis connection test failed: {e}")
        return False


def create_vector_index(
    index_name: str,
    vector_dims: int = 1536,
    distance_metric: str = "COSINE"
) -> bool:
    """
    Create Redis Search index for vector similarity search

    Args:
        index_name: Name of the index (e.g., kb_requirement_agent)
        vector_dims: Vector dimensions (1536 for OpenAI, 1024 for Anthropic)
        distance_metric: COSINE, L2, or IP

    Returns:
        True if index created successfully
    """
    client = get_redis_client()

    try:
        # Check if index already exists
        try:
            client.ft(index_name).info()
            logger.info(f"Index {index_name} already exists")
            return True
        except redis.ResponseError:
            # Index doesn't exist, create it
            pass

        # Define schema
        schema = (
            TextField("content", weight=1.0),
            TextField("title", weight=1.5),
            NumericField("document_id"),
            NumericField("kb_id"),
            NumericField("chunk_index"),
            TextField("metadata"),
            VectorField(
                "embedding",
                "HNSW",
                {
                    "TYPE": "FLOAT32",
                    "DIM": vector_dims,
                    "DISTANCE_METRIC": distance_metric,
                    "INITIAL_CAP": 1000,
                }
            ),
        )

        # Create index
        client.ft(index_name).create_index(
            fields=schema,
            definition=IndexDefinition(
                prefix=[f"{index_name}:doc:"],
                index_type=IndexType.HASH
            )
        )

        logger.info(f"Created vector index: {index_name} (dims={vector_dims})")
        return True

    except Exception as e:
        logger.error(f"Failed to create index {index_name}: {e}")
        raise


def delete_vector_index(index_name: str) -> bool:
    """
    Delete Redis Search index and all its documents

    Args:
        index_name: Name of the index to delete

    Returns:
        True if deletion successful
    """
    client = get_redis_client()

    try:
        # Delete index and documents
        client.ft(index_name).dropindex(delete_documents=True)
        logger.info(f"Deleted vector index: {index_name}")
        return True
    except redis.ResponseError as e:
        logger.warning(f"Index {index_name} does not exist or already deleted: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to delete index {index_name}: {e}")
        raise


def get_index_info(index_name: str) -> Optional[Dict]:
    """
    Get information about a vector index

    Args:
        index_name: Name of the index

    Returns:
        Index info dictionary or None if index doesn't exist
    """
    client = get_redis_client()

    try:
        info = client.ft(index_name).info()
        return {
            "index_name": info.get("index_name"),
            "num_docs": info.get("num_docs", 0),
            "num_terms": info.get("num_terms", 0),
            "num_records": info.get("num_records", 0),
            "indexing": info.get("indexing", False),
        }
    except redis.ResponseError:
        logger.warning(f"Index {index_name} does not exist")
        return None
    except Exception as e:
        logger.error(f"Failed to get index info for {index_name}: {e}")
        raise


def list_all_indexes() -> List[str]:
    """
    List all Redis Search indexes

    Returns:
        List of index names
    """
    client = get_redis_client()

    try:
        indexes = client.execute_command("FT._LIST")
        # Filter to only kb_ indexes
        kb_indexes = [idx.decode() if isinstance(idx, bytes) else idx
                      for idx in indexes if (isinstance(idx, bytes) and idx.startswith(b"kb_"))
                      or (isinstance(idx, str) and idx.startswith("kb_"))]
        return kb_indexes
    except Exception as e:
        logger.error(f"Failed to list indexes: {e}")
        return []


def count_documents_in_index(index_name: str) -> int:
    """
    Count total documents in an index

    Args:
        index_name: Name of the index

    Returns:
        Number of documents
    """
    info = get_index_info(index_name)
    return info.get("num_docs", 0) if info else 0
