from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Optional
from pydantic import BaseModel
from app.services.qdrant_service import qdrant_service
from app import auth

router = APIRouter(prefix="/api/qdrant", tags=["qdrant"])


def require_auth_dependency(request: Request) -> str:
    """Dependency to require authentication"""
    return auth.require_auth(request)


class CollectionResponse(BaseModel):
    name: str
    vectors_count: int
    points_count: int
    status: str
    error: Optional[str] = None


class CollectionDetailResponse(BaseModel):
    name: str
    vectors_count: int
    points_count: int
    status: str
    config: dict


class ConnectionTestResponse(BaseModel):
    connected: bool
    collections_count: Optional[int] = None
    url: Optional[str] = None
    error: Optional[str] = None


@router.get("/test", response_model=ConnectionTestResponse)
async def test_qdrant_connection(username: str = Depends(require_auth_dependency)):
    """Test connection to Qdrant"""
    result = qdrant_service.test_connection()
    return result


@router.get("/collections", response_model=List[CollectionResponse])
async def list_collections(username: str = Depends(require_auth_dependency)):
    """List all available Qdrant collections"""
    collections = qdrant_service.list_collections()
    return collections


@router.get("/collections/{collection_name}", response_model=CollectionDetailResponse)
async def get_collection_details(collection_name: str, username: str = Depends(require_auth_dependency)):
    """Get detailed information about a specific collection"""
    info = qdrant_service.get_collection_info(collection_name)

    if not info:
        raise HTTPException(
            status_code=404,
            detail=f"Collection '{collection_name}' not found or could not be accessed"
        )

    return info


@router.get("/collections/{collection_name}/exists")
async def check_collection_exists(collection_name: str, username: str = Depends(require_auth_dependency)):
    """Check if a collection exists"""
    exists = qdrant_service.collection_exists(collection_name)
    return {"exists": exists, "collection_name": collection_name}
