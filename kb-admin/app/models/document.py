"""
Pydantic models for KB Document entities
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SourceType(str, Enum):
    """Document source types"""
    UPLOAD = "upload"
    LEARNED = "learned"
    MANUAL = "manual"
    IMPORTED = "imported"


class DocumentStatus(str, Enum):
    """Document processing status"""
    PENDING = "pending"
    VECTORIZED = "vectorized"
    FAILED = "failed"


class DocumentCreate(BaseModel):
    """Schema for creating a document"""
    kb_id: int
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    source_type: SourceType = SourceType.UPLOAD
    source_reference: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentUpdate(BaseModel):
    """Schema for updating a document"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    metadata: Optional[Dict[str, Any]] = None


class DocumentResponse(BaseModel):
    """Schema for document response"""
    id: int
    kb_id: int
    title: str
    content: str
    source_type: SourceType
    source_reference: Optional[str]
    metadata: Optional[Dict[str, Any]]
    chunk_count: int
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentList(BaseModel):
    """Schema for listing documents"""
    items: List[DocumentResponse]
    total: int
    page: int
    page_size: int


class DocumentUploadResponse(BaseModel):
    """Schema for document upload response"""
    document_id: int
    title: str
    status: DocumentStatus
    chunk_count: int
    message: str


class VectorizationRequest(BaseModel):
    """Schema for vectorization request"""
    document_ids: Optional[List[int]] = None  # None means all pending documents


class VectorizationResponse(BaseModel):
    """Schema for vectorization response"""
    job_id: str
    status: str
    total_documents: int
    message: str


class VectorizationStatus(BaseModel):
    """Schema for vectorization status"""
    job_id: str
    status: str  # processing, completed, failed
    total_documents: int
    processed_documents: int
    failed_documents: int
    progress_percentage: float
    error_message: Optional[str] = None
