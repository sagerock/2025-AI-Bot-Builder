"""
Webhook Schemas
Pydantic models for webhook API requests and responses
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any
from datetime import datetime


class WebhookBase(BaseModel):
    url: str = Field(..., description="Webhook URL to call")
    events: List[str] = Field(..., description="List of events to trigger webhook")
    secret: Optional[str] = Field(None, description="Optional secret for signature verification")
    description: Optional[str] = Field(None, description="Description of webhook purpose")
    is_active: bool = Field(default=True, description="Whether webhook is active")


class WebhookCreate(WebhookBase):
    bot_id: str = Field(..., description="ID of bot this webhook belongs to")


class WebhookUpdate(BaseModel):
    url: Optional[str] = Field(None, description="Webhook URL to call")
    events: Optional[List[str]] = Field(None, description="List of events to trigger webhook")
    secret: Optional[str] = Field(None, description="Optional secret for signature verification")
    description: Optional[str] = Field(None, description="Description of webhook purpose")
    is_active: Optional[bool] = Field(None, description="Whether webhook is active")


class WebhookResponse(WebhookBase):
    id: str
    bot_id: str
    events: List[str]  # Converted from comma-separated string
    created_at: datetime
    updated_at: Optional[datetime] = None
    total_calls: int = 0
    last_called_at: Optional[datetime] = None
    last_status_code: Optional[int] = None
    last_error: Optional[str] = None

    model_config = {"from_attributes": True}

    @field_validator('events', mode='before')
    @classmethod
    def parse_events(cls, v: Any) -> List[str]:
        """Convert comma-separated string to list"""
        if isinstance(v, str):
            return [e.strip() for e in v.split(',') if e.strip()]
        return v

    @field_validator('total_calls', mode='before')
    @classmethod
    def parse_total_calls(cls, v: Any) -> int:
        """Convert string to int"""
        if isinstance(v, str):
            return int(v) if v.isdigit() else 0
        return v or 0

    @field_validator('last_status_code', mode='before')
    @classmethod
    def parse_status_code(cls, v: Any) -> Optional[int]:
        """Convert string to int"""
        if isinstance(v, str):
            return int(v) if v.isdigit() else None
        return v


class WebhookPayload(BaseModel):
    """Payload sent to webhook endpoints"""
    event: str = Field(..., description="Event type that triggered the webhook")
    bot_id: str = Field(..., description="ID of the bot")
    bot_name: str = Field(..., description="Name of the bot")
    session_id: str = Field(..., description="Conversation session ID")
    timestamp: datetime = Field(..., description="Event timestamp")
    user_id: Optional[str] = Field(None, description="User ID if authenticated")
    user_email: Optional[str] = Field(None, description="User email if authenticated")
    data: dict = Field(..., description="Event-specific data")


# Available event types
WEBHOOK_EVENTS = [
    "conversation_started",
    "message_sent",
    "message_received",
    "conversation_ended"
]
