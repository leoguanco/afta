"""
Indexing Endpoints - Infrastructure Layer

API endpoints for RAG indexing operations.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from src.infrastructure.di.container import Container
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/index", tags=["indexing"])


class IndexRequest(BaseModel):
    """Request model for manual indexing."""
    match_events: Optional[list] = None
    match_metrics: Optional[Dict[str, Any]] = None
    match_summary: Optional[str] = None


@router.post("/{match_id}")
async def index_match(match_id: str, request: IndexRequest):
    """
    Manually trigger RAG indexing for a match.
    
    This is useful for re-indexing or indexing custom data.
    """
    try:
        indexer = Container.get_match_data_indexer()
        result = indexer.execute(
            match_id=match_id,
            match_events=request.match_events,
            match_metrics=request.match_metrics,
            match_summary=request.match_summary
        )
        
        logger.info(f"Manual indexing complete for {match_id}: {result.documents_indexed} docs")
        
        return {
            "status": result.status,
            "match_id": result.match_id,
            "documents_indexed": result.documents_indexed
        }
    except Exception as e:
        logger.error(f"Manual indexing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_index_stats():
    """
    Get vector store statistics.
    
    Returns document count, collection info, etc.
    """
    try:
        vector_store = Container.get_vector_store()
        stats = vector_store.get_collection_stats()
        
        return {
            "status": "ok",
            **stats
        }
    except Exception as e:
        logger.error(f"Failed to get index stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{match_id}")
async def delete_match_index(match_id: str):
    """
    Delete all indexed documents for a specific match.
    
    Useful for re-indexing or cleanup.
    """
    try:
        vector_store = Container.get_vector_store()
        deleted_count = vector_store.delete_by_metadata({"match_id": match_id})
        
        logger.info(f"Deleted {deleted_count} documents for match {match_id}")
        
        return {
            "status": "deleted",
            "match_id": match_id,
            "documents_deleted": deleted_count
        }
    except Exception as e:
        logger.error(f"Failed to delete index: {e}")
        raise HTTPException(status_code=500, detail=str(e))
