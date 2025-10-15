from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.api_key import APIKeyCreate, APIKeyUpdate, APIKeyResponse
from app.services.api_key_service import APIKeyService
from app import auth

router = APIRouter(prefix="/api/api-keys", tags=["api-keys"])


def require_auth_dependency(request: Request) -> str:
    """Dependency to require authentication"""
    return auth.require_auth(request)


@router.post("", response_model=APIKeyResponse, status_code=201)
def create_api_key(api_key_data: APIKeyCreate, db: Session = Depends(get_db), username: str = Depends(require_auth_dependency)):
    """Create a new API key"""
    api_key = APIKeyService.create_api_key(db, api_key_data)
    return api_key


@router.get("", response_model=List[APIKeyResponse])
def get_api_keys(provider: Optional[str] = None, db: Session = Depends(get_db), username: str = Depends(require_auth_dependency)):
    """Get all API keys, optionally filtered by provider"""
    return APIKeyService.get_all_api_keys(db, provider)


@router.get("/{key_id}", response_model=APIKeyResponse)
def get_api_key(key_id: str, db: Session = Depends(get_db), username: str = Depends(require_auth_dependency)):
    """Get a specific API key"""
    api_key = APIKeyService.get_api_key(db, key_id)
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    return api_key


@router.put("/{key_id}", response_model=APIKeyResponse)
def update_api_key(key_id: str, api_key_data: APIKeyUpdate, db: Session = Depends(get_db), username: str = Depends(require_auth_dependency)):
    """Update an API key"""
    api_key = APIKeyService.update_api_key(db, key_id, api_key_data)
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    return api_key


@router.delete("/{key_id}", status_code=204)
def delete_api_key(key_id: str, db: Session = Depends(get_db), username: str = Depends(require_auth_dependency)):
    """Delete an API key"""
    success = APIKeyService.delete_api_key(db, key_id)
    if not success:
        raise HTTPException(status_code=404, detail="API key not found")
    return None
