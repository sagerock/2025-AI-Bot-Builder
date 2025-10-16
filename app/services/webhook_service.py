"""
Webhook Service
Handles webhook firing and management
"""
import httpx
import hashlib
import hmac
import json
from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from app.models.webhook import Webhook
from app.schemas.webhook import WebhookPayload
import asyncio


class WebhookService:
    """Service for managing and firing webhooks"""

    @staticmethod
    def create_webhook(db: Session, bot_id: str, url: str, events: List[str],
                      secret: Optional[str] = None, description: Optional[str] = None) -> Webhook:
        """
        Create a new webhook for a bot

        Args:
            db: Database session
            bot_id: Bot ID
            url: Webhook URL
            events: List of events to trigger webhook
            secret: Optional secret for signature verification
            description: Optional description

        Returns:
            Created webhook
        """
        import uuid

        webhook = Webhook(
            id=str(uuid.uuid4()),
            bot_id=bot_id,
            url=url,
            events=",".join(events),  # Store as comma-separated string
            secret=secret,
            description=description,
            is_active=True,
            total_calls="0"
        )

        db.add(webhook)
        db.commit()
        db.refresh(webhook)

        return webhook

    @staticmethod
    def get_webhooks_for_bot(db: Session, bot_id: str, active_only: bool = True) -> List[Webhook]:
        """
        Get all webhooks for a bot

        Args:
            db: Database session
            bot_id: Bot ID
            active_only: Only return active webhooks

        Returns:
            List of webhooks
        """
        query = db.query(Webhook).filter(Webhook.bot_id == bot_id)

        if active_only:
            query = query.filter(Webhook.is_active == True)

        return query.all()

    @staticmethod
    def get_webhooks_for_event(db: Session, bot_id: str, event: str) -> List[Webhook]:
        """
        Get webhooks that should be triggered for a specific event

        Args:
            db: Database session
            bot_id: Bot ID
            event: Event name

        Returns:
            List of webhooks subscribed to this event
        """
        webhooks = WebhookService.get_webhooks_for_bot(db, bot_id, active_only=True)

        # Filter webhooks that have this event in their events list
        return [w for w in webhooks if event in w.events.split(',')]

    @staticmethod
    def update_webhook_stats(db: Session, webhook_id: str, status_code: int,
                            error: Optional[str] = None):
        """
        Update webhook statistics after firing

        Args:
            db: Database session
            webhook_id: Webhook ID
            status_code: HTTP status code received
            error: Error message if failed
        """
        webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()

        if webhook:
            # Increment total calls
            current_calls = int(webhook.total_calls) if webhook.total_calls.isdigit() else 0
            webhook.total_calls = str(current_calls + 1)

            # Update stats
            webhook.last_called_at = datetime.utcnow()
            webhook.last_status_code = str(status_code)
            webhook.last_error = error

            db.commit()

    @staticmethod
    def generate_signature(payload: str, secret: str) -> str:
        """
        Generate HMAC SHA256 signature for webhook payload

        Args:
            payload: JSON payload as string
            secret: Webhook secret

        Returns:
            Hex digest of signature
        """
        return hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    @staticmethod
    async def fire_webhook_async(webhook: Webhook, payload: WebhookPayload, db: Session):
        """
        Fire a webhook asynchronously

        Args:
            webhook: Webhook configuration
            payload: Payload to send
            db: Database session
        """
        try:
            # Convert payload to dict
            payload_dict = payload.model_dump(mode='json')

            # Convert datetime to ISO format string
            if 'timestamp' in payload_dict:
                payload_dict['timestamp'] = payload_dict['timestamp'].isoformat()

            payload_json = json.dumps(payload_dict)

            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "AI-Bot-Builder-Webhook/1.0",
                "X-Webhook-Event": payload.event,
                "X-Bot-ID": payload.bot_id,
                "X-Session-ID": payload.session_id,
            }

            # Add signature if secret is configured
            if webhook.secret:
                signature = WebhookService.generate_signature(payload_json, webhook.secret)
                headers["X-Webhook-Signature"] = f"sha256={signature}"

            # Fire webhook with timeout
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    webhook.url,
                    content=payload_json,
                    headers=headers
                )

                # Update stats
                WebhookService.update_webhook_stats(
                    db,
                    webhook.id,
                    response.status_code,
                    error=None if response.is_success else response.text[:500]
                )

                print(f"✅ Webhook fired successfully: {webhook.url} (status: {response.status_code})")

        except Exception as e:
            # Update stats with error
            WebhookService.update_webhook_stats(
                db,
                webhook.id,
                500,
                error=str(e)[:500]
            )
            print(f"❌ Webhook firing failed: {webhook.url} - {str(e)}")

    @staticmethod
    def fire_webhook(webhook: Webhook, payload: WebhookPayload, db: Session):
        """
        Fire a webhook synchronously (creates async task)

        Args:
            webhook: Webhook configuration
            payload: Payload to send
            db: Database session
        """
        try:
            # Create event loop if not exists
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # Run async webhook in background
            asyncio.create_task(WebhookService.fire_webhook_async(webhook, payload, db))

        except Exception as e:
            print(f"❌ Error creating webhook task: {str(e)}")

    @staticmethod
    def trigger_event(db: Session, event: str, bot_id: str, bot_name: str,
                     session_id: str, user_id: Optional[str], user_email: Optional[str],
                     data: Dict):
        """
        Trigger webhook event for all subscribed webhooks

        Args:
            db: Database session
            event: Event name
            bot_id: Bot ID
            bot_name: Bot name
            session_id: Session ID
            user_id: User ID if authenticated
            user_email: User email if authenticated
            data: Event-specific data
        """
        # Get webhooks for this event
        webhooks = WebhookService.get_webhooks_for_event(db, bot_id, event)

        if not webhooks:
            return  # No webhooks to fire

        # Create payload
        payload = WebhookPayload(
            event=event,
            bot_id=bot_id,
            bot_name=bot_name,
            session_id=session_id,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            user_email=user_email,
            data=data
        )

        # Fire all webhooks
        for webhook in webhooks:
            try:
                WebhookService.fire_webhook(webhook, payload, db)
            except Exception as e:
                print(f"❌ Error firing webhook {webhook.id}: {str(e)}")


    @staticmethod
    def delete_webhook(db: Session, webhook_id: str) -> bool:
        """
        Delete a webhook

        Args:
            db: Database session
            webhook_id: Webhook ID

        Returns:
            True if deleted, False if not found
        """
        webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()

        if not webhook:
            return False

        db.delete(webhook)
        db.commit()
        return True
