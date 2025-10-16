from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import List, Optional
from app.database import get_db
from app.models.bot import Bot
from app.models.conversation import Conversation, Message
from app import auth

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


def require_auth_dependency(request: Request) -> str:
    """Dependency to require authentication"""
    return auth.require_auth(request)


@router.get("/bots")
async def get_bot_analytics(
    username: str = Depends(require_auth_dependency),
    db: Session = Depends(get_db)
):
    """Get analytics for all bots"""

    # Get all bots
    bots = db.query(Bot).filter(Bot.is_active == True).all()

    analytics = []

    for bot in bots:
        # Total conversations
        total_conversations = db.query(func.count(Conversation.id))\
            .filter(Conversation.bot_id == bot.id)\
            .scalar() or 0

        # Total messages
        total_messages = db.query(func.count(Message.id))\
            .join(Conversation)\
            .filter(Conversation.bot_id == bot.id)\
            .scalar() or 0

        # Messages today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        messages_today = db.query(func.count(Message.id))\
            .join(Conversation)\
            .filter(
                Conversation.bot_id == bot.id,
                Message.created_at >= today_start
            )\
            .scalar() or 0

        # Messages this week
        week_start = today_start - timedelta(days=today_start.weekday())
        messages_this_week = db.query(func.count(Message.id))\
            .join(Conversation)\
            .filter(
                Conversation.bot_id == bot.id,
                Message.created_at >= week_start
            )\
            .scalar() or 0

        # Average messages per conversation
        avg_messages = round(total_messages / total_conversations, 2) if total_conversations > 0 else 0

        # RAG usage count
        rag_usage_count = db.query(func.count(Message.id))\
            .join(Conversation)\
            .filter(
                Conversation.bot_id == bot.id,
                Message.rag_context.isnot(None),
                Message.rag_context != ''
            )\
            .scalar() or 0

        # RAG usage percentage
        rag_usage_percentage = round((rag_usage_count / total_messages * 100), 2) if total_messages > 0 else 0

        # First and last used dates
        first_message = db.query(Message.created_at)\
            .join(Conversation)\
            .filter(Conversation.bot_id == bot.id)\
            .order_by(Message.created_at.asc())\
            .first()

        last_message = db.query(Message.created_at)\
            .join(Conversation)\
            .filter(Conversation.bot_id == bot.id)\
            .order_by(Message.created_at.desc())\
            .first()

        analytics.append({
            "bot_id": bot.id,
            "bot_name": bot.name,
            "provider": bot.provider,
            "model": bot.model,
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "messages_today": messages_today,
            "messages_this_week": messages_this_week,
            "avg_messages_per_conversation": avg_messages,
            "rag_enabled": bot.use_qdrant,
            "rag_usage_count": rag_usage_count,
            "rag_usage_percentage": rag_usage_percentage,
            "first_used": first_message[0].isoformat() if first_message else None,
            "last_used": last_message[0].isoformat() if last_message else None
        })

    # Sort by total messages (most active first)
    analytics.sort(key=lambda x: x["total_messages"], reverse=True)

    return {"bots": analytics}


@router.get("/platform")
async def get_platform_analytics(
    username: str = Depends(require_auth_dependency),
    db: Session = Depends(get_db)
):
    """Get platform-wide analytics"""

    # Total conversations
    total_conversations = db.query(func.count(Conversation.id)).scalar() or 0

    # Total messages
    total_messages = db.query(func.count(Message.id)).scalar() or 0

    # Total bots
    total_bots = db.query(func.count(Bot.id)).filter(Bot.is_active == True).scalar() or 0

    # Active bots (have at least one conversation)
    active_bots = db.query(func.count(func.distinct(Conversation.bot_id))).scalar() or 0

    # Unique users (unique session_ids)
    unique_users = db.query(func.count(func.distinct(Conversation.session_id))).scalar() or 0

    # Today's stats
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    conversations_today = db.query(func.count(Conversation.id))\
        .filter(Conversation.created_at >= today_start)\
        .scalar() or 0

    messages_today = db.query(func.count(Message.id))\
        .filter(Message.created_at >= today_start)\
        .scalar() or 0

    # This week's stats
    week_start = today_start - timedelta(days=today_start.weekday())
    conversations_this_week = db.query(func.count(Conversation.id))\
        .filter(Conversation.created_at >= week_start)\
        .scalar() or 0

    messages_this_week = db.query(func.count(Message.id))\
        .filter(Message.created_at >= week_start)\
        .scalar() or 0

    # Average messages per conversation
    avg_messages_per_conversation = round(total_messages / total_conversations, 2) if total_conversations > 0 else 0

    return {
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "total_bots": total_bots,
        "active_bots": active_bots,
        "inactive_bots": total_bots - active_bots,
        "unique_users": unique_users,
        "conversations_today": conversations_today,
        "messages_today": messages_today,
        "conversations_this_week": conversations_this_week,
        "messages_this_week": messages_this_week,
        "avg_messages_per_conversation": avg_messages_per_conversation
    }


@router.get("/timeline")
async def get_timeline_analytics(
    days: int = 30,
    username: str = Depends(require_auth_dependency),
    db: Session = Depends(get_db)
):
    """Get daily activity timeline for the last N days"""

    # Calculate start date
    end_date = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)
    start_date = end_date - timedelta(days=days)

    # Get daily message counts
    daily_stats = []

    for i in range(days + 1):
        day_start = (start_date + timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        conversations = db.query(func.count(Conversation.id))\
            .filter(
                Conversation.created_at >= day_start,
                Conversation.created_at < day_end
            )\
            .scalar() or 0

        messages = db.query(func.count(Message.id))\
            .filter(
                Message.created_at >= day_start,
                Message.created_at < day_end
            )\
            .scalar() or 0

        daily_stats.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "conversations": conversations,
            "messages": messages
        })

    return {"timeline": daily_stats, "days": days}


@router.get("/bots/{bot_id}")
async def get_bot_detail_analytics(
    bot_id: str,
    username: str = Depends(require_auth_dependency),
    db: Session = Depends(get_db)
):
    """Get detailed analytics for a specific bot"""

    # Check if bot exists
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    # Get recent conversations (last 10)
    recent_conversations = db.query(
        Conversation.id,
        Conversation.session_id,
        Conversation.created_at,
        Conversation.updated_at,
        func.count(Message.id).label('message_count')
    ).join(Message)\
     .filter(Conversation.bot_id == bot_id)\
     .group_by(Conversation.id, Conversation.session_id, Conversation.created_at, Conversation.updated_at)\
     .order_by(Conversation.created_at.desc())\
     .limit(10)\
     .all()

    conversations_list = []
    for conv in recent_conversations:
        duration = None
        if conv.updated_at and conv.created_at:
            delta = conv.updated_at - conv.created_at
            duration = int(delta.total_seconds())

        conversations_list.append({
            "conversation_id": conv.id,
            "session_id": conv.session_id,
            "started_at": conv.created_at.isoformat(),
            "last_message_at": conv.updated_at.isoformat() if conv.updated_at else conv.created_at.isoformat(),
            "message_count": conv.message_count,
            "duration_seconds": duration
        })

    # Daily activity for last 7 days
    daily_activity = []
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    for i in range(7):
        day_start = today - timedelta(days=6-i)
        day_end = day_start + timedelta(days=1)

        messages = db.query(func.count(Message.id))\
            .join(Conversation)\
            .filter(
                Conversation.bot_id == bot_id,
                Message.created_at >= day_start,
                Message.created_at < day_end
            )\
            .scalar() or 0

        daily_activity.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "messages": messages
        })

    return {
        "bot_id": bot_id,
        "bot_name": bot.name,
        "recent_conversations": conversations_list,
        "daily_activity": daily_activity
    }
