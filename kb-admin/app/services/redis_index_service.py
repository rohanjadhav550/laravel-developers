"""
Redis Index Management Service
Handles creation, deletion, and management of Redis vector indexes
"""
from app.redis_client import (
    create_vector_index,
    delete_vector_index,
    get_index_info,
    list_all_indexes,
    count_documents_in_index
)
from app.config import settings
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class RedisIndexService:
    """Service for managing Redis vector indexes"""

    @staticmethod
    def create_index_for_agent(agent_type: str, embedding_provider: str = "openai") -> bool:
        """
        Create a Redis vector index for an agent

        Args:
            agent_type: Agent type (requirement_agent, developer_agent, generic)
            embedding_provider: openai or anthropic

        Returns:
            True if index created successfully
        """
        index_name = f"kb_{agent_type}"

        # Determine vector dimensions based on provider
        vector_dims = 1536 if embedding_provider == "openai" else 1024

        logger.info(f"Creating index {index_name} with {vector_dims} dimensions")

        try:
            return create_vector_index(
                index_name=index_name,
                vector_dims=vector_dims,
                distance_metric="COSINE"
            )
        except Exception as e:
            logger.error(f"Failed to create index {index_name}: {e}")
            raise

    @staticmethod
    def delete_index_for_agent(agent_type: str) -> bool:
        """
        Delete a Redis vector index for an agent

        Args:
            agent_type: Agent type

        Returns:
            True if deletion successful
        """
        index_name = f"kb_{agent_type}"
        logger.info(f"Deleting index {index_name}")

        try:
            return delete_vector_index(index_name)
        except Exception as e:
            logger.error(f"Failed to delete index {index_name}: {e}")
            raise

    @staticmethod
    def get_index_statistics(agent_type: str) -> Optional[Dict]:
        """
        Get statistics for an agent's index

        Args:
            agent_type: Agent type

        Returns:
            Dictionary with index statistics or None if index doesn't exist
        """
        index_name = f"kb_{agent_type}"

        try:
            info = get_index_info(index_name)
            if not info:
                return None

            return {
                "index_name": index_name,
                "agent_type": agent_type,
                "num_docs": info.get("num_docs", 0),
                "num_terms": info.get("num_terms", 0),
                "indexing": info.get("indexing", False),
            }
        except Exception as e:
            logger.error(f"Failed to get index stats for {index_name}: {e}")
            return None

    @staticmethod
    def index_exists(agent_type: str) -> bool:
        """
        Check if an index exists for an agent

        Args:
            agent_type: Agent type

        Returns:
            True if index exists
        """
        index_name = f"kb_{agent_type}"
        info = get_index_info(index_name)
        return info is not None

    @staticmethod
    def list_all_kb_indexes() -> List[Dict]:
        """
        List all knowledge base indexes

        Returns:
            List of index information dictionaries
        """
        try:
            index_names = list_all_indexes()

            indexes = []
            for index_name in index_names:
                info = get_index_info(index_name)
                if info:
                    agent_type = index_name.replace("kb_", "") if index_name.startswith("kb_") else "unknown"
                    indexes.append({
                        "index_name": index_name,
                        "agent_type": agent_type,
                        "num_docs": info.get("num_docs", 0),
                    })

            return indexes
        except Exception as e:
            logger.error(f"Failed to list indexes: {e}")
            return []

    @staticmethod
    def get_document_count(agent_type: str) -> int:
        """
        Get count of documents in an agent's index

        Args:
            agent_type: Agent type

        Returns:
            Number of documents
        """
        index_name = f"kb_{agent_type}"

        try:
            return count_documents_in_index(index_name)
        except Exception as e:
            logger.error(f"Failed to count documents in {index_name}: {e}")
            return 0

    @staticmethod
    def ensure_index_exists(agent_type: str, embedding_provider: str = "openai") -> bool:
        """
        Ensure an index exists, create if it doesn't

        Args:
            agent_type: Agent type
            embedding_provider: openai or anthropic

        Returns:
            True if index exists or was created
        """
        if RedisIndexService.index_exists(agent_type):
            logger.debug(f"Index kb_{agent_type} already exists")
            return True

        logger.info(f"Index kb_{agent_type} doesn't exist, creating...")
        return RedisIndexService.create_index_for_agent(agent_type, embedding_provider)
