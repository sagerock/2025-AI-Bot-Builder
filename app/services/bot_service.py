from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.bot import Bot
from app.schemas.bot import BotCreate, BotUpdate


class BotService:
    @staticmethod
    def create_bot(db: Session, bot_data: BotCreate) -> Bot:
        """Create a new bot"""
        bot = Bot(**bot_data.model_dump())
        db.add(bot)
        db.commit()
        db.refresh(bot)
        return bot

    @staticmethod
    def get_bot(db: Session, bot_id: str) -> Optional[Bot]:
        """Get a bot by ID"""
        from sqlalchemy.orm import joinedload
        return db.query(Bot).options(joinedload(Bot.api_key_ref)).filter(Bot.id == bot_id, Bot.is_active == True).first()

    @staticmethod
    def get_all_bots(db: Session, include_inactive: bool = False) -> List[Bot]:
        """Get all bots"""
        from sqlalchemy.orm import joinedload
        query = db.query(Bot).options(joinedload(Bot.api_key_ref))
        if not include_inactive:
            query = query.filter(Bot.is_active == True)
        return query.order_by(Bot.created_at.desc()).all()

    @staticmethod
    def update_bot(db: Session, bot_id: str, bot_data: BotUpdate) -> Optional[Bot]:
        """Update a bot"""
        bot = db.query(Bot).filter(Bot.id == bot_id).first()
        if not bot:
            return None

        update_data = bot_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(bot, field, value)

        db.commit()
        db.refresh(bot)
        return bot

    @staticmethod
    def delete_bot(db: Session, bot_id: str) -> bool:
        """Soft delete a bot"""
        bot = db.query(Bot).filter(Bot.id == bot_id).first()
        if not bot:
            return False

        bot.is_active = False
        db.commit()
        return True

    @staticmethod
    def hard_delete_bot(db: Session, bot_id: str) -> bool:
        """Permanently delete a bot"""
        bot = db.query(Bot).filter(Bot.id == bot_id).first()
        if not bot:
            return False

        db.delete(bot)
        db.commit()
        return True
