from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Bot(Base):
    __tablename__ = "bots"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # AI Provider Configuration
    provider = Column(String(50), nullable=False)  # "anthropic" or "openai"
    model = Column(String(100), nullable=False)  # e.g., "claude-3-5-sonnet-20241022", "gpt-4"
    api_key_id = Column(String(36), ForeignKey('api_keys.id'), nullable=True)  # Reference to APIKey
    api_key = Column(String(255), nullable=True)  # Legacy field, kept for backward compatibility

    # Relationship to APIKey
    api_key_ref = relationship("APIKey", foreign_keys=[api_key_id])

    # Bot Behavior
    system_prompt = Column(Text, nullable=False)
    temperature = Column(Integer, default=70)  # 0-100 (will be converted to 0.0-1.0)
    max_tokens = Column(Integer, default=1024)

    # GPT-5 specific settings (for OpenAI Responses API)
    reasoning_effort = Column(String(20), default="medium")  # minimal, low, medium, high
    text_verbosity = Column(String(20), default="medium")  # low, medium, high

    # RAG Configuration
    use_qdrant = Column(Boolean, default=False)
    qdrant_collection = Column(String(255), nullable=True)
    qdrant_top_k = Column(Integer, default=5)

    # Session Configuration
    enable_memory = Column(Boolean, default=True)
    memory_max_messages = Column(Integer, default=10)  # Last N messages to remember

    # Widget Customization
    widget_title = Column(String(255), nullable=True)
    widget_color = Column(String(7), default="#0066CC")  # Hex color
    widget_greeting = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
