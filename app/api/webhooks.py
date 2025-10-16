"""
Webhooks API
Manage webhooks for bots
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.webhook import WebhookCreate, WebhookUpdate, WebhookResponse, WEBHOOK_EVENTS
from app.services.webhook_service import WebhookService
from app.auth import is_authenticated

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


@router.post("/", response_model=WebhookResponse)
def create_webhook(
    webhook: WebhookCreate,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(is_authenticated)
):
    """
    Create a new webhook for a bot

    Requires authentication.
    """
    # Validate events
    invalid_events = [e for e in webhook.events if e not in WEBHOOK_EVENTS]
    if invalid_events:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid events: {', '.join(invalid_events)}. "
                   f"Valid events: {', '.join(WEBHOOK_EVENTS)}"
        )

    # Create webhook
    webhook_obj = WebhookService.create_webhook(
        db,
        bot_id=webhook.bot_id,
        url=webhook.url,
        events=webhook.events,
        secret=webhook.secret,
        description=webhook.description
    )

    return WebhookResponse.model_validate(webhook_obj)


@router.get("/bot/{bot_id}", response_model=List[WebhookResponse])
def get_bot_webhooks(
    bot_id: str,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(is_authenticated)
):
    """
    Get all webhooks for a bot

    Requires authentication.
    """
    webhooks = WebhookService.get_webhooks_for_bot(db, bot_id, active_only=False)
    return [WebhookResponse.model_validate(w) for w in webhooks]


@router.get("/{webhook_id}", response_model=WebhookResponse)
def get_webhook(
    webhook_id: str,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(is_authenticated)
):
    """
    Get a specific webhook by ID

    Requires authentication.
    """
    from app.models.webhook import Webhook

    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    return WebhookResponse.model_validate(webhook)


@router.put("/{webhook_id}", response_model=WebhookResponse)
def update_webhook(
    webhook_id: str,
    updates: WebhookUpdate,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(is_authenticated)
):
    """
    Update a webhook

    Requires authentication.
    """
    from app.models.webhook import Webhook

    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    # Validate events if provided
    if updates.events:
        invalid_events = [e for e in updates.events if e not in WEBHOOK_EVENTS]
        if invalid_events:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid events: {', '.join(invalid_events)}"
            )
        webhook.events = ",".join(updates.events)

    # Update fields
    if updates.url is not None:
        webhook.url = updates.url
    if updates.secret is not None:
        webhook.secret = updates.secret
    if updates.description is not None:
        webhook.description = updates.description
    if updates.is_active is not None:
        webhook.is_active = updates.is_active

    db.commit()
    db.refresh(webhook)

    return WebhookResponse.model_validate(webhook)


@router.delete("/{webhook_id}", status_code=204)
def delete_webhook(
    webhook_id: str,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(is_authenticated)
):
    """
    Delete a webhook

    Requires authentication.
    """
    success = WebhookService.delete_webhook(db, webhook_id)
    if not success:
        raise HTTPException(status_code=404, detail="Webhook not found")

    return None


@router.get("/events/available")
def get_available_events():
    """
    Get list of available webhook events

    Does not require authentication.
    """
    from app.models.webhook import WEBHOOK_EVENTS as EVENT_DESCRIPTIONS

    return {
        "events": [
            {
                "name": event,
                "description": EVENT_DESCRIPTIONS.get(event, "")
            }
            for event in WEBHOOK_EVENTS
        ]
    }
