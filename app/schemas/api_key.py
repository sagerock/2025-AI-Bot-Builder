from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class APIKeyCreate(BaseModel):
    """Schema for creating an API key"""
    name: str = Field(..., min_length=1, max_length=100, description="Friendly name for the API key")
    provider: str = Field(..., pattern="^(anthropic|openai)$", description="AI provider")
    api_key: str = Field(..., min_length=1, description="The actual API key")


class APIKeyUpdate(BaseModel):
    """Schema for updating an API key"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    provider: Optional[str] = Field(None, pattern="^(anthropic|openai)$")
    api_key: Optional[str] = Field(None, min_length=1)


class APIKeyResponse(BaseModel):
    """Schema for API key responses (with masked key)"""
    id: str
    name: str
    provider: str
    api_key: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    def model_post_init(self, __context):
        """Mask API key for security after initialization"""
        if self.api_key and len(self.api_key) > 12:
            self.api_key = f"{self.api_key[:8]}...{self.api_key[-4:]}"
        elif self.api_key:
            self.api_key = "***"
