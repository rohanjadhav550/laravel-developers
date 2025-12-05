"""
Pydantic models for Knowledge Base entities
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AgentType(str, Enum):
    """Agent types for KB assignment"""
    REQUIREMENT_AGENT = "requirement_agent"
    DEVELOPER_AGENT = "developer_agent"
    GENERIC = "generic"


class KBStatus(str, Enum):
    """Knowledge Base status"""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class EmbeddingProvider(str, Enum):
    """Supported embedding providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class KnowledgeBaseCreate(BaseModel):
    """Schema for creating a new Knowledge Base"""
    agent_type: AgentType
    name: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    embedding_provider: EmbeddingProvider = EmbeddingProvider.OPENAI
    embedding_model: Optional[str] = "text-embedding-3-small"
    chunk_size: int = Field(default=1000, ge=100, le=2000)
    chunk_overlap: int = Field(default=200, ge=0, le=500)
    created_by: Optional[int] = None


class KnowledgeBaseUpdate(BaseModel):
    """Schema for updating a Knowledge Base"""
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    status: Optional[KBStatus] = None
    chunk_size: Optional[int] = Field(None, ge=100, le=2000)
    chunk_overlap: Optional[int] = Field(None, ge=0, le=500)


class KnowledgeBaseResponse(BaseModel):
    """Schema for Knowledge Base response"""
    id: int
    agent_type: AgentType
    name: str
    description: Optional[str]
    status: KBStatus
    index_name: str
    embedding_provider: EmbeddingProvider
    embedding_model: Optional[str]
    chunk_size: int
    chunk_overlap: int
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    last_vectorized_at: Optional[datetime]
    document_count: int
    vector_count: int

    class Config:
        from_attributes = True


class KnowledgeBaseList(BaseModel):
    """Schema for listing Knowledge Bases"""
    items: List[KnowledgeBaseResponse]
    total: int
    page: int
    page_size: int


class KnowledgeBaseStats(BaseModel):
    """Schema for KB statistics"""
    kb_id: int
    agent_type: AgentType
    total_documents: int
    total_vectors: int
    avg_chunk_size: float
    learned_knowledge_count: int
    last_query_at: Optional[datetime]
    query_count_24h: int
