from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BotBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    provider: str = Field(..., pattern="^(anthropic|openai)$")
    model: str = Field(..., min_length=1)
    system_prompt: str = Field(..., min_length=1)
    temperature: int = Field(default=70, ge=0, le=100)
    max_tokens: int = Field(default=1024, ge=1, le=4096)

    # GPT-5 specific settings
    reasoning_effort: str = Field(default="medium", pattern="^(minimal|low|medium|high)$")
    text_verbosity: str = Field(default="medium", pattern="^(low|medium|high)$")

    # RAG
    use_qdrant: bool = False
    qdrant_collection: Optional[str] = None
    qdrant_top_k: int = Field(default=5, ge=1, le=20)

    # Memory
    enable_memory: bool = True
    memory_max_messages: int = Field(default=10, ge=1, le=50)

    # Widget
    widget_title: Optional[str] = None
    widget_color: str = Field(default="#0066CC", pattern="^#[0-9A-Fa-f]{6}$")
    widget_greeting: Optional[str] = None


class BotCreate(BotBase):
    api_key: Optional[str] = Field(None, min_length=1)  # Legacy support
    api_key_id: Optional[str] = None  # New system - reference to APIKey


class BotUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    provider: Optional[str] = Field(None, pattern="^(anthropic|openai)$")
    model: Optional[str] = None
    api_key: Optional[str] = None  # Legacy support
    api_key_id: Optional[str] = None  # New system
    system_prompt: Optional[str] = None
    temperature: Optional[int] = Field(None, ge=0, le=100)
    max_tokens: Optional[int] = Field(None, ge=1, le=4096)
    reasoning_effort: Optional[str] = Field(None, pattern="^(minimal|low|medium|high)$")
    text_verbosity: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    use_qdrant: Optional[bool] = None
    qdrant_collection: Optional[str] = None
    qdrant_top_k: Optional[int] = Field(None, ge=1, le=20)
    enable_memory: Optional[bool] = None
    memory_max_messages: Optional[int] = Field(None, ge=1, le=50)
    widget_title: Optional[str] = None
    widget_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    widget_greeting: Optional[str] = None
    is_active: Optional[bool] = None


class BotResponse(BotBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool
    api_key: Optional[str] = Field(default="***hidden***")  # Legacy - never expose full API key
    api_key_id: Optional[str] = None  # New system - reference to APIKey
    api_key_name: Optional[str] = None  # For display in UI
    reasoning_effort: str = "medium"
    text_verbosity: str = "medium"

    class Config:
        from_attributes = True

    def model_post_init(self, __context):
        """Hide API key in response and populate api_key_name"""
        # Hide legacy API key
        if hasattr(self, 'api_key') and self.api_key and self.api_key != "***hidden***":
            self.api_key = f"{self.api_key[:8]}...{self.api_key[-4:]}" if len(self.api_key) > 12 else "***hidden***"
