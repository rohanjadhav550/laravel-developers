"""
Document API Routes
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from app.services.kb_service import KBService
from app.services.document_service import DocumentService
from app.services.vectorization_service import VectorizationService
from app.models.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentList,
    DocumentUploadResponse,
    VectorizationRequest,
    VectorizationResponse,
    SourceType,
    DocumentStatus
)
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/{kb_id}/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    kb_id: int,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None)
):
    """
    Upload a document to a Knowledge Base

    - **kb_id**: Knowledge Base ID
    - **file**: Document file (markdown, text, or PDF)
    - **title**: Optional custom title (uses filename if not provided)
    """
    # Verify KB exists
    kb = KBService.get_kb_by_id(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail=f"Knowledge Base {kb_id} not found")

    try:
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8')

        # Use provided title or filename
        doc_title = title or file.filename

        # Create document
        doc_data = DocumentCreate(
            kb_id=kb_id,
            title=doc_title,
            content=content_str,
            source_type=SourceType.UPLOAD,
            source_reference=file.filename,
            metadata={
                "filename": file.filename,
                "content_type": file.content_type,
                "size": len(content)
            }
        )

        doc = DocumentService.create_document(doc_data)

        return DocumentUploadResponse(
            document_id=doc.id,
            title=doc.title,
            status=doc.status,
            chunk_count=0,
            message=f"Document uploaded successfully. Use /vectorize to process."
        )

    except Exception as e:
        logger.error(f"Failed to upload document: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload document")


@router.post("/{kb_id}/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(kb_id: int, doc_data: DocumentCreate):
    """
    Create a document from raw text

    - **kb_id**: Knowledge Base ID
    - **title**: Document title
    - **content**: Document content
    - **source_type**: upload, learned, manual, or imported
    """
    # Verify KB exists
    kb = KBService.get_kb_by_id(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail=f"Knowledge Base {kb_id} not found")

    # Ensure kb_id matches
    doc_data.kb_id = kb_id

    try:
        doc = DocumentService.create_document(doc_data)
        return doc
    except Exception as e:
        logger.error(f"Failed to create document: {e}")
        raise HTTPException(status_code=500, detail="Failed to create document")


@router.get("/{kb_id}/documents/{doc_id}", response_model=DocumentResponse)
async def get_document(kb_id: int, doc_id: int):
    """
    Get a document by ID
    """
    doc = DocumentService.get_document_by_id(doc_id)
    if not doc or doc.kb_id != kb_id:
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found in KB {kb_id}")
    return doc


@router.get("/{kb_id}/documents", response_model=DocumentList)
async def list_documents(
    kb_id: int,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 50
):
    """
    List documents in a Knowledge Base

    - **kb_id**: Knowledge Base ID
    - **status**: Filter by status (pending, vectorized, failed)
    - **page**: Page number
    - **page_size**: Results per page
    """
    # Verify KB exists
    kb = KBService.get_kb_by_id(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail=f"Knowledge Base {kb_id} not found")

    offset = (page - 1) * page_size
    docs = DocumentService.list_documents(
        kb_id=kb_id,
        status=status,
        limit=page_size,
        offset=offset
    )

    total = DocumentService.count_documents(kb_id, status)

    return DocumentList(
        items=docs,
        total=total,
        page=page,
        page_size=page_size
    )


@router.put("/{kb_id}/documents/{doc_id}", response_model=DocumentResponse)
async def update_document(kb_id: int, doc_id: int, updates: DocumentUpdate):
    """
    Update a document

    - **title**: Update title
    - **content**: Update content
    - **metadata**: Update metadata
    """
    doc = DocumentService.get_document_by_id(doc_id)
    if not doc or doc.kb_id != kb_id:
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found in KB {kb_id}")

    try:
        updated_doc = DocumentService.update_document(doc_id, updates)
        return updated_doc
    except Exception as e:
        logger.error(f"Failed to update document {doc_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update document")


@router.delete("/{kb_id}/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(kb_id: int, doc_id: int):
    """
    Delete a document

    Also deletes associated vectors from Redis
    """
    doc = DocumentService.get_document_by_id(doc_id)
    if not doc or doc.kb_id != kb_id:
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found in KB {kb_id}")

    try:
        # Delete vectors from Redis
        VectorizationService.delete_document_vectors(kb_id, doc_id)

        # Delete document from database
        DocumentService.delete_document(doc_id)

        # Update KB stats
        KBService.update_document_count(kb_id)

    except Exception as e:
        logger.error(f"Failed to delete document {doc_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete document")


@router.post("/{kb_id}/vectorize", response_model=VectorizationResponse)
async def vectorize_documents(kb_id: int, request: Optional[VectorizationRequest] = None):
    """
    Trigger vectorization for documents

    - **kb_id**: Knowledge Base ID
    - **document_ids**: Specific document IDs (optional, defaults to all pending documents)

    This will:
    1. Chunk documents into smaller pieces
    2. Generate embeddings for each chunk
    3. Store vectors in Redis for similarity search
    """
    # Verify KB exists
    kb = KBService.get_kb_by_id(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail=f"Knowledge Base {kb_id} not found")

    try:
        document_ids = request.document_ids if request else None

        # Start vectorization (synchronous for now, TODO: make async with background jobs)
        result = VectorizationService.vectorize_kb(kb_id, document_ids)

        job_id = VectorizationService.get_vectorization_job_id()

        return VectorizationResponse(
            job_id=job_id,
            status="completed",  # Since we're doing it synchronously
            total_documents=result['total_documents'],
            message=f"Processed {result['processed']} documents, {result['failed']} failed"
        )

    except Exception as e:
        logger.error(f"Failed to vectorize KB {kb_id}: {e}")
        raise HTTPException(status_code=500, detail="Vectorization failed")
