from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class KnowledgeType(str, Enum):
    qa_pair = "qa_pair"
    solution_pattern = "solution_pattern"
    user_correction = "user_correction"
    context_pattern = "context_pattern"


class ReviewStatus(str, Enum):
    pending_review = "pending_review"
    approved = "approved"
    rejected = "rejected"


class LearnedKnowledgeCreate(BaseModel):
    agent_type: str
    knowledge_type: KnowledgeType
    source_thread_id: Optional[str] = None
    source_conversation_id: Optional[int] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    confidence_score: float = 0.0


class LearnedKnowledgeUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    status: Optional[ReviewStatus] = None


class LearnedKnowledgeReview(BaseModel):
    status: ReviewStatus  # approved or rejected
    reviewed_by: str  # User Name or ID who reviewed


class LearnedKnowledgeResponse(BaseModel):
    id: int
    agent_type: str
    knowledge_type: KnowledgeType
    source_thread_id: Optional[str]
    source_conversation_id: Optional[int]
    question: Optional[str]
    answer: Optional[str]
    context: Optional[Dict[str, Any]]
    confidence_score: float
    status: ReviewStatus
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
