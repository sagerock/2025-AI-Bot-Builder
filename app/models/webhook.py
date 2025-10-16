"""
Webhook Model
Stores webhook configurations for bots
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.database import Base


class Webhook(Base):
    """Webhook configuration for a bot"""
    __tablename__ = "webhooks"

    id = Column(String, primary_key=True, index=True)
    bot_id = Column(String, ForeignKey("bots.id", ondelete="CASCADE"), nullable=False, index=True)

    # Webhook configuration
    url = Column(String, nullable=False)  # Webhook URL to call
    events = Column(Text, nullable=False)  # Comma-separated list of events (e.g., "conversation_started,message_sent")
    secret = Column(String, nullable=True)  # Optional secret for webhook signature verification

    # Status
    is_active = Column(Boolean, default=True)

    # Metadata
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Stats
    total_calls = Column(String, default="0")  # Total webhook calls
    last_called_at = Column(DateTime(timezone=True), nullable=True)
    last_status_code = Column(String, nullable=True)  # Last HTTP status code
    last_error = Column(Text, nullable=True)  # Last error message if failed


# Supported webhook events
WEBHOOK_EVENTS = {
    "conversation_started": "Triggered when a new conversation begins",
    "message_sent": "Triggered when a user sends a message",
    "message_received": "Triggered when bot sends a response",
    "conversation_ended": "Triggered when a conversation is cleared/deleted",
}
