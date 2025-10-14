from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base
import uuid


class APIKey(Base):
    """API Key model for storing reusable API keys"""
    __tablename__ = "api_keys"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)  # e.g., "My Anthropic Key", "Client A OpenAI"
    provider = Column(String(50), nullable=False)  # anthropic, openai
    api_key = Column(String(500), nullable=False)  # The actual API key
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
