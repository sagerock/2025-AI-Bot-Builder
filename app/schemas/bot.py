from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


# Model-specific max token limits
MODEL_MAX_TOKENS = {
    # Claude 4.x
    'claude-sonnet-4-5': 64000,
    'claude-haiku-4-5': 64000,
    'claude-sonnet-4': 64000,
    'claude-opus-4-1': 32000,
    # Claude 3.x
    'claude-3-7': 128000,
    'claude-3-5-sonnet': 8000,
    'claude-3-5-haiku': 8000,
    'claude-3-opus': 4000,
    'claude-3-sonnet': 4000,
    'claude-3-haiku': 4000,
    # OpenAI GPT-5
    'gpt-5': 128000,
    'gpt-5-mini': 128000,
    'gpt-5-nano': 128000,
    # OpenAI GPT-4
    'gpt-4': 8000,
    'gpt-4o': 16000,
    'gpt-4-turbo': 4096,
}


def get_model_max_tokens(model: str) -> int:
    """Get max tokens for a model, checking partial matches"""
    for key, max_tokens in MODEL_MAX_TOKENS.items():
        if key in model.lower():
            return max_tokens
    # Default to 8000 for unknown models
    return 8000


class BotBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    provider: str = Field(..., pattern="^(anthropic|openai)$")
    model: str = Field(..., min_length=1)
    system_prompt: str = Field(..., min_length=1)
    temperature: int = Field(default=70, ge=0, le=100)
    max_tokens: int = Field(default=8192, ge=1, le=128000)  # Absolute max, validated per model

    @field_validator('max_tokens')
    @classmethod
    def validate_max_tokens_for_model(cls, v: int, info) -> int:
        """Validate max_tokens doesn't exceed model's capability"""
        # Get model from the data being validated
        model = info.data.get('model', '')
        if model:
            model_limit = get_model_max_tokens(model)
            if v > model_limit:
                raise ValueError(
                    f"max_tokens ({v}) exceeds limit for {model} (max: {model_limit})"
                )
        return v

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
    enable_suggestions: bool = False

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
    max_tokens: Optional[int] = Field(None, ge=1, le=128000)  # Supports GPT-5 (128k max output)
    reasoning_effort: Optional[str] = Field(None, pattern="^(minimal|low|medium|high)$")
    text_verbosity: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    use_qdrant: Optional[bool] = None
    qdrant_collection: Optional[str] = None
    qdrant_top_k: Optional[int] = Field(None, ge=1, le=20)
    enable_memory: Optional[bool] = None
    memory_max_messages: Optional[int] = Field(None, ge=1, le=50)
    enable_suggestions: Optional[bool] = None
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
