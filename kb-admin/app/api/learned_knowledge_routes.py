from fastapi import APIRouter, HTTPException, Query
from app.models.learned_knowledge import (
    LearnedKnowledgeCreate,
    LearnedKnowledgeUpdate,
    LearnedKnowledgeReview,
    LearnedKnowledgeResponse
)
from app.services.learned_knowledge_service import LearnedKnowledgeService
from typing import List, Optional

router = APIRouter()


@router.post("/capture", response_model=LearnedKnowledgeResponse, status_code=201)
def capture_knowledge(data: LearnedKnowledgeCreate):
    """
    Capture new learned knowledge from conversations or solutions.

    This endpoint is called by:
    - idea-agent after Q&A exchanges
    - Laravel app when solutions are approved
    - Manual corrections by users

    Knowledge is captured with status='pending_review' and waits for admin approval.
    """
    try:
        return LearnedKnowledgeService.capture_knowledge(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending", response_model=List[LearnedKnowledgeResponse])
def list_pending_review(
    agent_type: Optional[str] = Query(None, description="Filter by agent type"),
    knowledge_type: Optional[str] = Query(None, description="Filter by knowledge type"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    List all learned knowledge pending review.

    Use this endpoint to build a review queue in the admin portal.
    Supports filtering by agent_type and knowledge_type.
    """
    try:
        return LearnedKnowledgeService.list_pending_review(
            agent_type=agent_type,
            knowledge_type=knowledge_type,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{knowledge_id}", response_model=LearnedKnowledgeResponse)
def get_knowledge(knowledge_id: int):
    """Get learned knowledge by ID"""
    try:
        return LearnedKnowledgeService.get_by_id(knowledge_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{knowledge_id}", response_model=LearnedKnowledgeResponse)
def update_knowledge(knowledge_id: int, data: LearnedKnowledgeUpdate):
    """
    Update learned knowledge before review.

    Allows admins to edit question/answer before approving.
    Only works for knowledge with status='pending_review'.
    """
    try:
        return LearnedKnowledgeService.update_knowledge(knowledge_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{knowledge_id}/review", response_model=LearnedKnowledgeResponse)
def review_knowledge(knowledge_id: int, review: LearnedKnowledgeReview):
    """
    Review learned knowledge - approve or reject.

    When approved:
    1. Status changes to 'approved'
    2. Knowledge is formatted as a document
    3. Document is added to the agent's KB
    4. Document is vectorized automatically
    5. Future agent queries can use this knowledge

    When rejected:
    1. Status changes to 'rejected'
    2. Knowledge is not added to KB
    3. Can be deleted or kept for audit trail
    """
    try:
        return LearnedKnowledgeService.review_knowledge(knowledge_id, review)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{knowledge_id}")
def delete_knowledge(knowledge_id: int):
    """
    Delete learned knowledge (only if pending review).

    Approved/rejected knowledge cannot be deleted to maintain audit trail.
    """
    try:
        success = LearnedKnowledgeService.delete_knowledge(knowledge_id)
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete - knowledge is not pending review or doesn't exist"
            )
        return {"success": True, "message": "Learned knowledge deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
def get_stats(agent_type: Optional[str] = Query(None, description="Filter by agent type")):
    """
    Get statistics about learned knowledge.

    Returns counts by status and knowledge type.
    Useful for dashboard widgets.
    """
    try:
        return LearnedKnowledgeService.get_stats(agent_type=agent_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
