"""
Knowledge Base API Routes
"""
from fastapi import APIRouter, HTTPException, status
from app.services.kb_service import KBService
from app.services.redis_index_service import RedisIndexService
from app.models.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
    KnowledgeBaseList,
    KnowledgeBaseStats
)
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/create", response_model=KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(kb_data: KnowledgeBaseCreate):
    """
    Create a new Knowledge Base for an agent

    - **agent_type**: requirement_agent, developer_agent, or generic
    - **name**: KB name
    - **description**: Optional description
    - **embedding_provider**: openai or anthropic
    - **chunk_size**: Text chunk size (default: 1000)
    - **chunk_overlap**: Chunk overlap (default: 200)
    """
    try:
        kb = KBService.create_kb(kb_data)
        return kb
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create KB: {e}")
        raise HTTPException(status_code=500, detail="Failed to create Knowledge Base")


@router.get("/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(kb_id: int):
    """
    Get Knowledge Base by ID
    """
    kb = KBService.get_kb_by_id(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail=f"Knowledge Base {kb_id} not found")
    return kb


@router.get("/agent/{agent_type}", response_model=KnowledgeBaseResponse)
async def get_kb_by_agent_type(agent_type: str):
    """
    Get active Knowledge Base for an agent type

    - **agent_type**: requirement_agent, developer_agent, or generic
    """
    kb = KBService.get_kb_by_agent_type(agent_type)
    if not kb:
        raise HTTPException(
            status_code=404,
            detail=f"No Knowledge Base found for agent type {agent_type}"
        )
    return kb


@router.get("/", response_model=KnowledgeBaseList)
async def list_knowledge_bases(
    agent_type: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 50
):
    """
    List Knowledge Bases with optional filtering

    - **agent_type**: Filter by agent type
    - **status**: Filter by status (draft, active, archived)
    - **page**: Page number (starts at 1)
    - **page_size**: Results per page
    """
    offset = (page - 1) * page_size
    kbs = KBService.list_kbs(
        agent_type=agent_type,
        status=status,
        limit=page_size,
        offset=offset
    )

    return KnowledgeBaseList(
        items=kbs,
        total=len(kbs),  # TODO: Implement total count query
        page=page,
        page_size=page_size
    )


@router.put("/{kb_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_base(kb_id: int, updates: KnowledgeBaseUpdate):
    """
    Update Knowledge Base properties

    - **name**: Update name
    - **description**: Update description
    - **status**: Update status
    - **chunk_size**: Update chunk size
    - **chunk_overlap**: Update chunk overlap
    """
    try:
        kb = KBService.update_kb(kb_id, updates)
        if not kb:
            raise HTTPException(status_code=404, detail=f"Knowledge Base {kb_id} not found")
        return kb
    except Exception as e:
        logger.error(f"Failed to update KB {kb_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update Knowledge Base")


@router.put("/{kb_id}/activate", response_model=KnowledgeBaseResponse)
async def activate_knowledge_base(kb_id: int):
    """
    Activate a Knowledge Base

    Sets status to 'active' - the KB will now be used by its assigned agent
    """
    try:
        kb = KBService.activate_kb(kb_id)
        return kb
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to activate KB {kb_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to activate Knowledge Base")


@router.delete("/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_base(kb_id: int):
    """
    Delete a Knowledge Base

    **Warning**: This will delete all documents and vectors associated with this KB!
    """
    try:
        success = KBService.delete_kb(kb_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Knowledge Base {kb_id} not found")
    except Exception as e:
        logger.error(f"Failed to delete KB {kb_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete Knowledge Base")


@router.get("/{kb_id}/status")
async def get_kb_status(kb_id: int):
    """
    Get Knowledge Base vectorization status

    Returns current status, document counts, and vector counts
    """
    kb = KBService.get_kb_by_id(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail=f"Knowledge Base {kb_id} not found")

    # Get Redis index stats
    index_stats = RedisIndexService.get_index_statistics(kb.agent_type.value)

    return {
        "kb_id": kb.id,
        "status": kb.status.value,
        "document_count": kb.document_count,
        "vector_count": kb.vector_count,
        "last_vectorized_at": kb.last_vectorized_at,
        "index_stats": index_stats
    }


@router.get("/{kb_id}/stats", response_model=KnowledgeBaseStats)
async def get_kb_statistics(kb_id: int):
    """
    Get detailed statistics for a Knowledge Base

    Includes document counts, vector counts, and usage metrics
    """
    kb = KBService.get_kb_by_id(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail=f"Knowledge Base {kb_id} not found")

    # TODO: Implement actual query metrics
    return KnowledgeBaseStats(
        kb_id=kb.id,
        agent_type=kb.agent_type,
        total_documents=kb.document_count,
        total_vectors=kb.vector_count,
        avg_chunk_size=kb.chunk_size,
        learned_knowledge_count=0,  # TODO: Query learned_knowledge table
        last_query_at=None,
        query_count_24h=0
    )
