"""
Document Service
Handles document CRUD operations
"""
from app.database import get_db_connection, execute_query
from app.models.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    SourceType,
    DocumentStatus
)
from typing import Optional, List, Dict
import logging
import json

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document operations"""

    @staticmethod
    def create_document(doc_data: DocumentCreate) -> Optional[DocumentResponse]:
        """
        Create a new document

        Args:
            doc_data: Document creation data

        Returns:
            Created document or None if failed
        """
        try:
            metadata_json = json.dumps(doc_data.metadata) if doc_data.metadata else None

            query = """
                INSERT INTO kb_documents (
                    kb_id, title, content, source_type, source_reference,
                    metadata, status, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """

            doc_id = execute_query(
                query,
                (
                    doc_data.kb_id,
                    doc_data.title,
                    doc_data.content,
                    doc_data.source_type.value,
                    doc_data.source_reference,
                    metadata_json,
                    DocumentStatus.PENDING.value
                )
            )

            logger.info(f"Created document {doc_id} in KB {doc_data.kb_id}")

            return DocumentService.get_document_by_id(doc_id)

        except Exception as e:
            logger.error(f"Failed to create document: {e}")
            raise

    @staticmethod
    def get_document_by_id(doc_id: int) -> Optional[DocumentResponse]:
        """
        Get document by ID

        Args:
            doc_id: Document ID

        Returns:
            Document data or None if not found
        """
        query = "SELECT * FROM kb_documents WHERE id = %s"
        result = execute_query(query, (doc_id,), fetch_one=True)

        if not result:
            return None

        return DocumentService._row_to_response(result)

    @staticmethod
    def list_documents(
        kb_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[DocumentResponse]:
        """
        List documents with filtering

        Args:
            kb_id: Filter by KB ID
            status: Filter by status
            limit: Max results
            offset: Offset for pagination

        Returns:
            List of documents
        """
        conditions = []
        params = []

        if kb_id is not None:
            conditions.append("kb_id = %s")
            params.append(kb_id)

        if status:
            conditions.append("status = %s")
            params.append(status)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        query = f"""
            SELECT * FROM kb_documents
            {where_clause}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])

        results = execute_query(query, tuple(params), fetch_all=True)

        return [DocumentService._row_to_response(row) for row in results] if results else []

    @staticmethod
    def update_document(doc_id: int, updates: DocumentUpdate) -> Optional[DocumentResponse]:
        """
        Update document

        Args:
            doc_id: Document ID
            updates: Update data

        Returns:
            Updated document or None if not found
        """
        set_clauses = []
        params = []

        if updates.title is not None:
            set_clauses.append("title = %s")
            params.append(updates.title)

        if updates.content is not None:
            set_clauses.append("content = %s")
            params.append(updates.content)

        if updates.metadata is not None:
            set_clauses.append("metadata = %s")
            params.append(json.dumps(updates.metadata))

        if not set_clauses:
            logger.warning("No fields to update")
            return DocumentService.get_document_by_id(doc_id)

        set_clauses.append("updated_at = NOW()")

        query = f"""
            UPDATE kb_documents
            SET {', '.join(set_clauses)}
            WHERE id = %s
        """
        params.append(doc_id)

        execute_query(query, tuple(params))

        logger.info(f"Updated document {doc_id}")

        return DocumentService.get_document_by_id(doc_id)

    @staticmethod
    def update_document_status(
        doc_id: int,
        status: DocumentStatus,
        chunk_count: Optional[int] = None
    ) -> Optional[DocumentResponse]:
        """
        Update document status and chunk count

        Args:
            doc_id: Document ID
            status: New status
            chunk_count: Number of chunks (optional)

        Returns:
            Updated document
        """
        if chunk_count is not None:
            query = """
                UPDATE kb_documents
                SET status = %s, chunk_count = %s, updated_at = NOW()
                WHERE id = %s
            """
            execute_query(query, (status.value, chunk_count, doc_id))
        else:
            query = """
                UPDATE kb_documents
                SET status = %s, updated_at = NOW()
                WHERE id = %s
            """
            execute_query(query, (status.value, doc_id))

        logger.info(f"Updated document {doc_id} status to {status.value}")

        return DocumentService.get_document_by_id(doc_id)

    @staticmethod
    def delete_document(doc_id: int) -> bool:
        """
        Delete a document

        Args:
            doc_id: Document ID

        Returns:
            True if deleted successfully
        """
        query = "DELETE FROM kb_documents WHERE id = %s"
        execute_query(query, (doc_id,))

        logger.info(f"Deleted document {doc_id}")

        return True

    @staticmethod
    def get_pending_documents(kb_id: int) -> List[DocumentResponse]:
        """
        Get all pending and failed documents for a KB
        (Documents that need to be vectorized or re-vectorized)

        Args:
            kb_id: KB ID

        Returns:
            List of documents needing vectorization
        """
        # Get both pending AND failed documents
        # Failed documents should be retried when "Re-Vectorize" is clicked
        from app.database import execute_query
        
        query = """
            SELECT * FROM kb_documents
            WHERE kb_id = %s AND (status = 'pending' OR status = 'failed')
            ORDER BY created_at DESC
        """
        
        results = execute_query(query, (kb_id,), fetch_all=True)
        
        if not results:
            return []
        
        return [DocumentService._row_to_response(row) for row in results]

    @staticmethod
    def count_documents(kb_id: int, status: Optional[str] = None) -> int:
        """
        Count documents in a KB

        Args:
            kb_id: KB ID
            status: Filter by status (optional)

        Returns:
            Document count
        """
        if status:
            query = "SELECT COUNT(*) as count FROM kb_documents WHERE kb_id = %s AND status = %s"
            result = execute_query(query, (kb_id, status), fetch_one=True)
        else:
            query = "SELECT COUNT(*) as count FROM kb_documents WHERE kb_id = %s"
            result = execute_query(query, (kb_id,), fetch_one=True)

        return result['count'] if result else 0

    @staticmethod
    def _row_to_response(row: Dict) -> DocumentResponse:
        """Convert database row to response model"""
        metadata = json.loads(row['metadata']) if row['metadata'] else None

        return DocumentResponse(
            id=row['id'],
            kb_id=row['kb_id'],
            title=row['title'],
            content=row['content'],
            source_type=SourceType(row['source_type']),
            source_reference=row['source_reference'],
            metadata=metadata,
            chunk_count=row['chunk_count'],
            status=DocumentStatus(row['status']),
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
