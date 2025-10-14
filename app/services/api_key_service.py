from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.api_key import APIKey
from app.schemas.api_key import APIKeyCreate, APIKeyUpdate


class APIKeyService:
    @staticmethod
    def create_api_key(db: Session, key_data: APIKeyCreate) -> APIKey:
        """Create a new API key"""
        api_key = APIKey(**key_data.model_dump())
        db.add(api_key)
        db.commit()
        db.refresh(api_key)
        return api_key

    @staticmethod
    def get_api_key(db: Session, key_id: str) -> Optional[APIKey]:
        """Get an API key by ID"""
        return db.query(APIKey).filter(APIKey.id == key_id, APIKey.is_active == True).first()

    @staticmethod
    def get_all_api_keys(db: Session, provider: Optional[str] = None) -> List[APIKey]:
        """Get all API keys, optionally filtered by provider"""
        query = db.query(APIKey).filter(APIKey.is_active == True)
        if provider:
            query = query.filter(APIKey.provider == provider)
        return query.order_by(APIKey.created_at.desc()).all()

    @staticmethod
    def update_api_key(db: Session, key_id: str, key_data: APIKeyUpdate) -> Optional[APIKey]:
        """Update an API key"""
        api_key = db.query(APIKey).filter(APIKey.id == key_id).first()
        if not api_key:
            return None

        update_data = key_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(api_key, field, value)

        db.commit()
        db.refresh(api_key)
        return api_key

    @staticmethod
    def delete_api_key(db: Session, key_id: str) -> bool:
        """Soft delete an API key"""
        api_key = db.query(APIKey).filter(APIKey.id == key_id).first()
        if not api_key:
            return False

        api_key.is_active = False
        db.commit()
        return True
