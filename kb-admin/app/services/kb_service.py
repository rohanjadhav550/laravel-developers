"""
Knowledge Base Service
Handles CRUD operations for Knowledge Bases
"""
from app.database import get_db_connection, execute_query
from app.services.redis_index_service import RedisIndexService
from app.models.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
    AgentType,
    KBStatus
)
from typing import Optional, List, Dict
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class KBService:
    """Service for Knowledge Base operations"""

    @staticmethod
    def create_kb(kb_data: KnowledgeBaseCreate) -> Optional[KnowledgeBaseResponse]:
        """
        Create a new Knowledge Base

        Args:
            kb_data: KB creation data

        Returns:
            Created KB or None if failed
        """
        try:
            # Generate index name
            index_name = f"kb_{kb_data.agent_type.value}"

            # Check if KB already exists for this agent
            existing = KBService.get_kb_by_agent_type(kb_data.agent_type.value)
            if existing:
                logger.warning(f"KB already exists for {kb_data.agent_type.value}")
                raise ValueError(f"Knowledge Base already exists for agent type {kb_data.agent_type.value}")

            # Create Redis index
            logger.info(f"Creating Redis index: {index_name}")
            RedisIndexService.create_index_for_agent(
                agent_type=kb_data.agent_type.value,
                embedding_provider=kb_data.embedding_provider.value
            )

            # Insert into database
            query = """
                INSERT INTO knowledge_bases (
                    agent_type, name, description, status, index_name,
                    embedding_provider, embedding_model, chunk_size, chunk_overlap,
                    created_by, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """

            kb_id = execute_query(
                query,
                (
                    kb_data.agent_type.value,
                    kb_data.name,
                    kb_data.description,
                    KBStatus.DRAFT.value,
                    index_name,
                    kb_data.embedding_provider.value,
                    kb_data.embedding_model,
                    kb_data.chunk_size,
                    kb_data.chunk_overlap,
                    kb_data.created_by
                )
            )

            # Log audit
            KBService._log_audit(kb_id, "created", kb_data.created_by, {"name": kb_data.name})

            logger.info(f"Created KB {kb_id} for agent {kb_data.agent_type.value}")

            # Return created KB
            return KBService.get_kb_by_id(kb_id)

        except Exception as e:
            logger.error(f"Failed to create KB: {e}")
            raise

    @staticmethod
    def get_kb_by_id(kb_id: int) -> Optional[KnowledgeBaseResponse]:
        """
        Get Knowledge Base by ID

        Args:
            kb_id: KB ID

        Returns:
            KB data or None if not found
        """
        query = "SELECT * FROM knowledge_bases WHERE id = %s"
        result = execute_query(query, (kb_id,), fetch_one=True)

        if not result:
            return None

        return KBService._row_to_response(result)

    @staticmethod
    def get_kb_by_agent_type(agent_type: str) -> Optional[KnowledgeBaseResponse]:
        """
        Get active Knowledge Base for an agent type

        Args:
            agent_type: Agent type (requirement_agent, developer_agent, generic)

        Returns:
            KB data or None if not found
        """
        query = "SELECT * FROM knowledge_bases WHERE agent_type = %s ORDER BY created_at DESC LIMIT 1"
        result = execute_query(query, (agent_type,), fetch_one=True)

        if not result:
            return None

        return KBService._row_to_response(result)

    @staticmethod
    def get_active_kb_by_agent(agent_type: str) -> KnowledgeBaseResponse:
        """
        Get active Knowledge Base for an agent type (raises error if not found or not active)

        Args:
            agent_type: Agent type (requirement_agent, developer_agent, generic)

        Returns:
            Active KB data

        Raises:
            ValueError: If no active KB found for the agent type
        """
        query = "SELECT * FROM knowledge_bases WHERE agent_type = %s AND status = 'active' ORDER BY created_at DESC LIMIT 1"
        result = execute_query(query, (agent_type,), fetch_one=True)

        if not result:
            raise ValueError(f"No active Knowledge Base found for agent type: {agent_type}")

        return KBService._row_to_response(result)

    @staticmethod
    def list_kbs(
        agent_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[KnowledgeBaseResponse]:
        """
        List Knowledge Bases with filtering

        Args:
            agent_type: Filter by agent type
            status: Filter by status
            limit: Max results
            offset: Offset for pagination

        Returns:
            List of KBs
        """
        conditions = []
        params = []

        if agent_type:
            conditions.append("agent_type = %s")
            params.append(agent_type)

        if status:
            conditions.append("status = %s")
            params.append(status)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        query = f"""
            SELECT * FROM knowledge_bases
            {where_clause}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])

        results = execute_query(query, tuple(params), fetch_all=True)

        return [KBService._row_to_response(row) for row in results] if results else []

    @staticmethod
    def update_kb(kb_id: int, updates: KnowledgeBaseUpdate, user_id: Optional[int] = None) -> Optional[KnowledgeBaseResponse]:
        """
        Update Knowledge Base

        Args:
            kb_id: KB ID
            updates: Update data
            user_id: User performing update

        Returns:
            Updated KB or None if not found
        """
        # Build update query dynamically
        set_clauses = []
        params = []

        if updates.name is not None:
            set_clauses.append("name = %s")
            params.append(updates.name)

        if updates.description is not None:
            set_clauses.append("description = %s")
            params.append(updates.description)

        if updates.status is not None:
            set_clauses.append("status = %s")
            params.append(updates.status.value)

        if updates.chunk_size is not None:
            set_clauses.append("chunk_size = %s")
            params.append(updates.chunk_size)

        if updates.chunk_overlap is not None:
            set_clauses.append("chunk_overlap = %s")
            params.append(updates.chunk_overlap)

        if not set_clauses:
            logger.warning("No fields to update")
            return KBService.get_kb_by_id(kb_id)

        set_clauses.append("updated_at = NOW()")

        query = f"""
            UPDATE knowledge_bases
            SET {', '.join(set_clauses)}
            WHERE id = %s
        """
        params.append(kb_id)

        execute_query(query, tuple(params))

        # Log audit
        KBService._log_audit(kb_id, "updated", user_id, updates.dict(exclude_none=True))

        logger.info(f"Updated KB {kb_id}")

        return KBService.get_kb_by_id(kb_id)

    @staticmethod
    def activate_kb(kb_id: int, user_id: Optional[int] = None) -> Optional[KnowledgeBaseResponse]:
        """
        Activate a Knowledge Base

        Args:
            kb_id: KB ID
            user_id: User performing activation

        Returns:
            Activated KB or None if not found
        """
        kb = KBService.get_kb_by_id(kb_id)
        if not kb:
            raise ValueError(f"KB {kb_id} not found")

        # Update status
        update_data = KnowledgeBaseUpdate(status=KBStatus.ACTIVE)
        updated_kb = KBService.update_kb(kb_id, update_data, user_id)

        # Log audit
        KBService._log_audit(kb_id, "activated", user_id, {"status": "active"})

        logger.info(f"Activated KB {kb_id} for agent {kb.agent_type}")

        return updated_kb

    @staticmethod
    def delete_kb(kb_id: int, user_id: Optional[int] = None) -> bool:
        """
        Delete a Knowledge Base (and its Redis index)

        Args:
            kb_id: KB ID
            user_id: User performing deletion

        Returns:
            True if deleted successfully
        """
        kb = KBService.get_kb_by_id(kb_id)
        if not kb:
            logger.warning(f"KB {kb_id} not found")
            return False

        try:
            # Delete Redis index
            logger.info(f"Deleting Redis index: {kb.index_name}")
            RedisIndexService.delete_index_for_agent(kb.agent_type.value)

            # Delete from database (cascade will delete documents)
            query = "DELETE FROM knowledge_bases WHERE id = %s"
            execute_query(query, (kb_id,))

            logger.info(f"Deleted KB {kb_id}")

            return True

        except Exception as e:
            logger.error(f"Failed to delete KB {kb_id}: {e}")
            raise

    @staticmethod
    def update_document_count(kb_id: int) -> None:
        """
        Update document and vector counts for a KB

        Args:
            kb_id: KB ID
        """
        kb = KBService.get_kb_by_id(kb_id)
        if not kb:
            return

        # Count documents
        doc_query = "SELECT COUNT(*) as count FROM kb_documents WHERE kb_id = %s AND status = 'vectorized'"
        doc_result = execute_query(doc_query, (kb_id,), fetch_one=True)
        doc_count = doc_result['count'] if doc_result else 0

        # Count vectors from Redis
        vector_count = RedisIndexService.get_document_count(kb.agent_type.value)

        # Update KB
        update_query = """
            UPDATE knowledge_bases
            SET document_count = %s, vector_count = %s, updated_at = NOW()
            WHERE id = %s
        """
        execute_query(update_query, (doc_count, vector_count, kb_id))

        logger.debug(f"Updated counts for KB {kb_id}: docs={doc_count}, vectors={vector_count}")

    @staticmethod
    def update_last_vectorized(kb_id: int) -> None:
        """
        Update last_vectorized_at timestamp

        Args:
            kb_id: KB ID
        """
        query = "UPDATE knowledge_bases SET last_vectorized_at = NOW(), updated_at = NOW() WHERE id = %s"
        execute_query(query, (kb_id,))

    @staticmethod
    def _row_to_response(row: Dict) -> KnowledgeBaseResponse:
        """Convert database row to response model"""
        return KnowledgeBaseResponse(
            id=row['id'],
            agent_type=AgentType(row['agent_type']),
            name=row['name'],
            description=row['description'],
            status=KBStatus(row['status']),
            index_name=row['index_name'],
            embedding_provider=row['embedding_provider'],
            embedding_model=row['embedding_model'],
            chunk_size=row['chunk_size'],
            chunk_overlap=row['chunk_overlap'],
            created_by=row['created_by'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            last_vectorized_at=row['last_vectorized_at'],
            document_count=row['document_count'],
            vector_count=row['vector_count']
        )

    @staticmethod
    def _log_audit(kb_id: int, action: str, user_id: Optional[int], details: Dict) -> None:
        """
        Log audit entry

        Args:
            kb_id: KB ID
            action: Action performed
            user_id: User ID
            details: Action details
        """
        try:
            query = """
                INSERT INTO kb_audit_log (kb_id, action, user_id, details, created_at)
                VALUES (%s, %s, %s, %s, NOW())
            """
            execute_query(query, (kb_id, action, user_id, json.dumps(details)))
        except Exception as e:
            logger.warning(f"Failed to log audit: {e}")
