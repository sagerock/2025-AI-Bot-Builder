from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.bot import BotCreate, BotUpdate, BotResponse
from app.services.bot_service import BotService
from app.models.bot import Bot
from app import auth

router = APIRouter(prefix="/api/bots", tags=["bots"])


def require_auth_dependency(request: Request) -> str:
    """Dependency to require authentication"""
    return auth.require_auth(request)


def enrich_bot_response(bot: Bot) -> BotResponse:
    """Convert Bot model to BotResponse with api_key_name populated"""
    response = BotResponse.model_validate(bot)
    # Populate api_key_name if using new system
    if bot.api_key_id and bot.api_key_ref:
        response.api_key_name = bot.api_key_ref.name
    return response


@router.post("", response_model=BotResponse, status_code=201)
def create_bot(bot_data: BotCreate, db: Session = Depends(get_db), username: str = Depends(require_auth_dependency)):
    """Create a new bot"""
    bot = BotService.create_bot(db, bot_data)
    return enrich_bot_response(bot)


@router.get("", response_model=List[BotResponse])
def list_bots(include_inactive: bool = False, db: Session = Depends(get_db), username: str = Depends(require_auth_dependency)):
    """List all bots"""
    bots = BotService.get_all_bots(db, include_inactive)
    return [enrich_bot_response(bot) for bot in bots]


@router.get("/{bot_id}/public")
def get_bot_public(bot_id: str, db: Session = Depends(get_db)):
    """Get public bot information (no auth required)"""
    bot = BotService.get_bot(db, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    # Return only public fields (exclude API keys and sensitive data)
    return {
        "id": bot.id,
        "name": bot.name,
        "widget_title": bot.widget_title,
        "widget_greeting": bot.widget_greeting,
        "widget_color": bot.widget_color,
        "enable_suggestions": bot.enable_suggestions,
        "use_qdrant": bot.use_qdrant,
        "qdrant_collection": bot.qdrant_collection
    }


@router.get("/{bot_id}", response_model=BotResponse)
def get_bot(bot_id: str, db: Session = Depends(get_db), username: str = Depends(require_auth_dependency)):
    """Get a specific bot (requires authentication)"""
    bot = BotService.get_bot(db, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    return enrich_bot_response(bot)


@router.put("/{bot_id}", response_model=BotResponse)
def update_bot(bot_id: str, bot_data: BotUpdate, db: Session = Depends(get_db), username: str = Depends(require_auth_dependency)):
    """Update a bot"""
    bot = BotService.update_bot(db, bot_id, bot_data)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    return enrich_bot_response(bot)


@router.delete("/{bot_id}", status_code=204)
def delete_bot(bot_id: str, hard_delete: bool = False, db: Session = Depends(get_db), username: str = Depends(require_auth_dependency)):
    """Delete a bot (soft delete by default)"""
    if hard_delete:
        success = BotService.hard_delete_bot(db, bot_id)
    else:
        success = BotService.delete_bot(db, bot_id)

    if not success:
        raise HTTPException(status_code=404, detail="Bot not found")

    return None
