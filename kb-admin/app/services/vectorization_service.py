"""
Vectorization Service
Handles document chunking, embedding, and vector storage in Redis
"""
from app.services.kb_service import KBService
from app.services.document_service import DocumentService
from app.services.embedding_service import get_embedding_service
from app.utils.chunking import ChunkingService
from app.redis_client import get_redis_client
from app.models.document import DocumentStatus
from typing import List, Dict, Optional
import logging
import numpy as np
import uuid

logger = logging.getLogger(__name__)


class VectorizationService:
    """Service for vectorizing documents and storing in Redis"""

    @staticmethod
    def vectorize_document(doc_id: int) -> bool:
        """
        Vectorize a single document

        Args:
            doc_id: Document ID

        Returns:
            True if successful
        """
        try:
            # Get document
            doc = DocumentService.get_document_by_id(doc_id)
            if not doc:
                logger.error(f"Document {doc_id} not found")
                return False

            # Get KB
            kb = KBService.get_kb_by_id(doc.kb_id)
            if not kb:
                logger.error(f"KB {doc.kb_id} not found")
                return False

            logger.info(f"Vectorizing document {doc_id} in KB {kb.id}")

            # Chunk document
            is_markdown = doc.title.endswith('.md') or (doc.metadata and doc.metadata.get('format') == 'markdown')

            chunks = ChunkingService.chunk_document(
                title=doc.title,
                content=doc.content,
                chunk_size=kb.chunk_size,
                chunk_overlap=kb.chunk_overlap,
                is_markdown=is_markdown
            )

            if not chunks:
                logger.warning(f"No chunks generated for document {doc_id}")
                DocumentService.update_document_status(doc_id, DocumentStatus.FAILED, 0)
                return False

            logger.info(f"Generated {len(chunks)} chunks for document {doc_id}")

            # Generate embeddings
            embedding_service = get_embedding_service(
                provider=kb.embedding_provider.value,
                model=kb.embedding_model
            )

            chunk_texts = [chunk['content'] for chunk in chunks]
            embeddings = embedding_service.embed_documents(chunk_texts)

            if len(embeddings) != len(chunks):
                logger.error(f"Embedding count mismatch: {len(embeddings)} != {len(chunks)}")
                DocumentService.update_document_status(doc_id, DocumentStatus.FAILED, 0)
                return False

            # Store vectors in Redis
            VectorizationService._store_vectors_in_redis(
                index_name=kb.index_name,
                kb_id=kb.id,
                doc_id=doc_id,
                chunks=chunks,
                embeddings=embeddings
            )

            # Update document status
            DocumentService.update_document_status(doc_id, DocumentStatus.VECTORIZED, len(chunks))

            # Update KB stats
            KBService.update_document_count(kb.id)
            KBService.update_last_vectorized(kb.id)

            logger.info(f"Successfully vectorized document {doc_id} ({len(chunks)} chunks)")

            return True

        except Exception as e:
            logger.error(f"Failed to vectorize document {doc_id}: {e}")
            DocumentService.update_document_status(doc_id, DocumentStatus.FAILED)
            raise

    @staticmethod
    def vectorize_kb(kb_id: int, document_ids: Optional[List[int]] = None) -> Dict:
        """
        Vectorize all documents (or specific documents) in a KB

        Args:
            kb_id: KB ID
            document_ids: Specific document IDs (None = all pending documents)

        Returns:
            Vectorization results
        """
        try:
            # Get KB
            kb = KBService.get_kb_by_id(kb_id)
            if not kb:
                raise ValueError(f"KB {kb_id} not found")

            # Get documents to vectorize
            if document_ids:
                documents = [DocumentService.get_document_by_id(doc_id) for doc_id in document_ids]
                documents = [d for d in documents if d and d.kb_id == kb_id]
            else:
                documents = DocumentService.get_pending_documents(kb_id)

            if not documents:
                logger.warning(f"No documents to vectorize for KB {kb_id}")
                return {
                    "total_documents": 0,
                    "processed": 0,
                    "failed": 0,
                    "status": "completed"
                }

            logger.info(f"Vectorizing {len(documents)} documents for KB {kb_id}")

            # Vectorize each document
            processed = 0
            failed = 0

            for doc in documents:
                try:
                    success = VectorizationService.vectorize_document(doc.id)
                    if success:
                        processed += 1
                    else:
                        failed += 1
                except Exception as e:
                    logger.error(f"Error vectorizing document {doc.id}: {e}")
                    failed += 1

            logger.info(f"Vectorization complete: {processed} processed, {failed} failed")

            return {
                "total_documents": len(documents),
                "processed": processed,
                "failed": failed,
                "status": "completed"
            }

        except Exception as e:
            logger.error(f"Failed to vectorize KB {kb_id}: {e}")
            raise

    @staticmethod
    def _store_vectors_in_redis(
        index_name: str,
        kb_id: int,
        doc_id: int,
        chunks: List[Dict],
        embeddings: List[List[float]]
    ) -> None:
        """
        Store vectors in Redis

        Args:
            index_name: Redis index name
            kb_id: KB ID
            doc_id: Document ID
            chunks: List of chunk dictionaries
            embeddings: List of embedding vectors
        """
        redis_client = get_redis_client()

        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # Create unique key for this chunk
            chunk_key = f"{index_name}:doc:{doc_id}:{idx}"

            # Convert embedding to bytes
            embedding_bytes = np.array(embedding, dtype=np.float32).tobytes()

            # Prepare Redis hash
            redis_data = {
                "content": chunk['content'],
                "title": chunk['title'],
                "document_id": doc_id,
                "kb_id": kb_id,
                "chunk_index": idx,
                "metadata": f"chunk {idx + 1} of {chunk['total_chunks']}",
                "embedding": embedding_bytes
            }

            # Store in Redis
            redis_client.hset(chunk_key, mapping=redis_data)

            logger.debug(f"Stored vector {chunk_key}")

        logger.info(f"Stored {len(chunks)} vectors in Redis index {index_name}")

    @staticmethod
    def delete_document_vectors(kb_id: int, doc_id: int) -> bool:
        """
        Delete all vectors for a document from Redis

        Args:
            kb_id: KB ID
            doc_id: Document ID

        Returns:
            True if successful
        """
        try:
            # Get KB to get index name
            kb = KBService.get_kb_by_id(kb_id)
            if not kb:
                logger.error(f"KB {kb_id} not found")
                return False

            redis_client = get_redis_client()
            index_name = kb.index_name

            # Find all keys for this document
            pattern = f"{index_name}:doc:{doc_id}:*"
            keys = redis_client.keys(pattern)

            if keys:
                redis_client.delete(*keys)
                logger.info(f"Deleted {len(keys)} vectors for document {doc_id}")

            return True

        except Exception as e:
            logger.error(f"Failed to delete vectors for document {doc_id}: {e}")
            raise

    @staticmethod
    def get_vectorization_job_id() -> str:
        """
        Generate a unique job ID for vectorization

        Returns:
            Job ID
        """
        return str(uuid.uuid4())
