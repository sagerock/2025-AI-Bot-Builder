"""
Webhook Schemas
Pydantic models for webhook API requests and responses
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
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

    class Config:
        from_attributes = True

    def __init__(self, **data):
        # Convert events string to list if needed
        if 'events' in data and isinstance(data['events'], str):
            data['events'] = [e.strip() for e in data['events'].split(',') if e.strip()]

        # Convert string fields to int if needed
        if 'total_calls' in data and isinstance(data['total_calls'], str):
            data['total_calls'] = int(data['total_calls']) if data['total_calls'].isdigit() else 0

        if 'last_status_code' in data and isinstance(data['last_status_code'], str):
            data['last_status_code'] = int(data['last_status_code']) if data['last_status_code'] else None

        super().__init__(**data)


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
