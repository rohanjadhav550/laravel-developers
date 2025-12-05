from app.database import get_db_connection
from app.models.learned_knowledge import (
    LearnedKnowledgeCreate,
    LearnedKnowledgeUpdate,
    LearnedKnowledgeReview,
    LearnedKnowledgeResponse,
    ReviewStatus
)
from typing import List, Optional
import json
from datetime import datetime


class LearnedKnowledgeService:
    """Service for managing learned knowledge"""

    @staticmethod
    def capture_knowledge(data: LearnedKnowledgeCreate) -> LearnedKnowledgeResponse:
        """
        Capture new learned knowledge from conversations or solutions.
        Status defaults to 'pending_review'.
        """
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)

            try:
                # Serialize context to JSON
                context_json = json.dumps(data.context) if data.context else None

                query = """
                    INSERT INTO learned_knowledge (
                        agent_type, knowledge_type, source_thread_id,
                        source_conversation_id, question, answer,
                        context, confidence_score, status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                cursor.execute(query, (
                    data.agent_type,
                    data.knowledge_type.value,
                    data.source_thread_id,
                    data.source_conversation_id,
                    data.question,
                    data.answer,
                    context_json,
                    data.confidence_score,
                    'pending_review'
                ))

                knowledge_id = cursor.lastrowid
                # Commit is handled by context manager on exit
            finally:
                cursor.close()

        # Fetch the created record
        return LearnedKnowledgeService.get_by_id(knowledge_id)

    @staticmethod
    def get_by_id(knowledge_id: int) -> LearnedKnowledgeResponse:
        """Get learned knowledge by ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)

            try:
                query = "SELECT * FROM learned_knowledge WHERE id = %s"
                cursor.execute(query, (knowledge_id,))
                row = cursor.fetchone()

                if not row:
                    raise ValueError(f"Learned knowledge with ID {knowledge_id} not found")

                # Parse JSON context
                if row['context']:
                    row['context'] = json.loads(row['context'])

                return LearnedKnowledgeResponse(**row)
            finally:
                cursor.close()

    @staticmethod
    def list_pending_review(
        agent_type: Optional[str] = None,
        knowledge_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[LearnedKnowledgeResponse]:
        """List all knowledge pending review with optional filters"""
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)

            try:
                query = "SELECT * FROM learned_knowledge WHERE status = 'pending_review'"
                params = []

                if agent_type:
                    query += " AND agent_type = %s"
                    params.append(agent_type)

                if knowledge_type:
                    query += " AND knowledge_type = %s"
                    params.append(knowledge_type)

                query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])

                cursor.execute(query, params)
                rows = cursor.fetchall()

                results = []
                for row in rows:
                    if row['context']:
                        row['context'] = json.loads(row['context'])
                    results.append(LearnedKnowledgeResponse(**row))

                return results
            finally:
                cursor.close()

    @staticmethod
    def review_knowledge(
        knowledge_id: int,
        review: LearnedKnowledgeReview
    ) -> LearnedKnowledgeResponse:
        """
        Review learned knowledge - approve or reject.
        If approved, it will be vectorized and added to the KB.
        """
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)

            try:
                query = """
                    UPDATE learned_knowledge
                    SET status = %s, reviewed_by = %s, reviewed_at = %s
                    WHERE id = %s
                """

                cursor.execute(query, (
                    review.status.value,
                    review.reviewed_by,
                    datetime.utcnow(),
                    knowledge_id
                ))
                
                if cursor.rowcount == 0:
                    raise ValueError(f"Learned knowledge with ID {knowledge_id} not found")
                
                # Commit is handled by context manager
            finally:
                cursor.close()

        # If approved, trigger vectorization
        if review.status == ReviewStatus.approved:
            LearnedKnowledgeService._vectorize_approved_knowledge(knowledge_id)

        return LearnedKnowledgeService.get_by_id(knowledge_id)

    @staticmethod
    def _vectorize_approved_knowledge(knowledge_id: int):
        """
        Vectorize approved knowledge and add to agent's KB.
        This creates a document in the KB and triggers vectorization.
        """
        from app.services.kb_service import KBService
        from app.services.document_service import DocumentService
        from app.services.vectorization_service import VectorizationService

        knowledge = LearnedKnowledgeService.get_by_id(knowledge_id)

        # Get or create KB for this agent type
        try:
            kb = KBService.get_active_kb_by_agent(knowledge.agent_type)
        except ValueError:
            # No active KB for this agent, skip vectorization
            print(f"No active KB found for agent type: {knowledge.agent_type}")
            return

        # Format the knowledge as markdown document
        if knowledge.knowledge_type == "qa_pair":
            content = f"# Q&A\n\n**Question:** {knowledge.question}\n\n**Answer:** {knowledge.answer}"
            title = f"QA: {knowledge.question[:50]}..."
        elif knowledge.knowledge_type == "solution_pattern":
            content = knowledge.answer or ""
            title = f"Solution Pattern: {knowledge.question[:50] if knowledge.question else 'Learned Pattern'}"
        elif knowledge.knowledge_type == "user_correction":
            content = f"# User Correction\n\n**Original:** {knowledge.question}\n\n**Corrected:** {knowledge.answer}"
            title = f"Correction: {knowledge.question[:50]}..."
        else:  # context_pattern
            content = knowledge.answer or ""
            title = f"Context Pattern: {knowledge.question[:50] if knowledge.question else 'Pattern'}"

        # Create document in KB
        doc = DocumentService.create_document(
            kb_id=kb.id,
            title=title,
            content=content,
            metadata={
                "source": "learned_knowledge",
                "learned_id": knowledge_id,
                "knowledge_type": knowledge.knowledge_type,
                "thread_id": knowledge.source_thread_id
            }
        )

        # Vectorize the document
        VectorizationService.vectorize_document(doc.id)

        print(f"✅ Learned knowledge {knowledge_id} vectorized and added to KB {kb.id}")

    @staticmethod
    def update_knowledge(
        knowledge_id: int,
        data: LearnedKnowledgeUpdate
    ) -> LearnedKnowledgeResponse:
        """Update learned knowledge before review"""
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)

            try:
                # Build dynamic update query
                update_fields = []
                params = []

                if data.question is not None:
                    update_fields.append("question = %s")
                    params.append(data.question)

                if data.answer is not None:
                    update_fields.append("answer = %s")
                    params.append(data.answer)

                if data.context is not None:
                    update_fields.append("context = %s")
                    params.append(json.dumps(data.context))

                if data.confidence_score is not None:
                    update_fields.append("confidence_score = %s")
                    params.append(data.confidence_score)

                if data.status is not None:
                    update_fields.append("status = %s")
                    params.append(data.status.value)

                if not update_fields:
                    # No fields to update
                    # Close cursor first
                    cursor.close()
                    return LearnedKnowledgeService.get_by_id(knowledge_id)

                update_fields.append("updated_at = %s")
                params.append(datetime.utcnow())
                params.append(knowledge_id)

                query = f"""
                    UPDATE learned_knowledge
                    SET {', '.join(update_fields)}
                    WHERE id = %s
                """

                cursor.execute(query, params)
                
                if cursor.rowcount == 0:
                    raise ValueError(f"Learned knowledge with ID {knowledge_id} not found")
                
                # Commit handled by context manager
            finally:
                cursor.close()

        return LearnedKnowledgeService.get_by_id(knowledge_id)

    @staticmethod
    def delete_knowledge(knowledge_id: int) -> bool:
        """Delete learned knowledge (only if pending review)"""
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)

            try:
                query = """
                    DELETE FROM learned_knowledge
                    WHERE id = %s AND status = 'pending_review'
                """

                cursor.execute(query, (knowledge_id,))
                # Commit handled by context manager

                return cursor.rowcount > 0
            finally:
                cursor.close()

    @staticmethod
    def get_stats(agent_type: Optional[str] = None) -> dict:
        """Get statistics about learned knowledge"""
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)

            try:
                where_clause = f"WHERE agent_type = '{agent_type}'" if agent_type else ""

                query = f"""
                    SELECT
                        status,
                        knowledge_type,
                        COUNT(*) as count
                    FROM learned_knowledge
                    {where_clause}
                    GROUP BY status, knowledge_type
                """

                cursor.execute(query)
                rows = cursor.fetchall()

                stats = {
                    "total": 0,
                    "pending_review": 0,
                    "approved": 0,
                    "rejected": 0,
                    "by_type": {}
                }

                for row in rows:
                    count = row['count']
                    status = row['status']
                    k_type = row['knowledge_type']

                    stats['total'] += count
                    stats[status] = stats.get(status, 0) + count

                    if k_type not in stats['by_type']:
                        stats['by_type'][k_type] = {
                            "pending_review": 0,
                            "approved": 0,
                            "rejected": 0
                        }
                    stats['by_type'][k_type][status] = count

                return stats
            finally:
                cursor.close()
