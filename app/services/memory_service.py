from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.conversation import Conversation, Message
from app.schemas.chat import ChatMessage
import uuid


class MemoryService:
    @staticmethod
    def get_or_create_conversation(
        db: Session, bot_id: str, session_id: Optional[str] = None
    ) -> tuple[Conversation, str]:
        """
        Get existing conversation or create new one
        Returns: (conversation, session_id)
        """
        if not session_id:
            session_id = str(uuid.uuid4())

        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.bot_id == bot_id,
                Conversation.session_id == session_id
            )
            .first()
        )

        if not conversation:
            conversation = Conversation(
                bot_id=bot_id,
                session_id=session_id
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

        return conversation, session_id

    @staticmethod
    def add_message(
        db: Session,
        conversation_id: str,
        role: str,
        content: str,
        rag_context: Optional[str] = None
    ) -> Message:
        """Add a message to conversation"""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            rag_context=rag_context
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def get_conversation_history(
        db: Session,
        conversation_id: str,
        max_messages: int = 10
    ) -> List[ChatMessage]:
        """Get recent conversation history"""
        messages = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(max_messages)
            .all()
        )

        # Reverse to get chronological order
        messages.reverse()

        return [
            ChatMessage(role=msg.role, content=msg.content)
            for msg in messages
        ]

    @staticmethod
    def clear_conversation(db: Session, session_id: str, bot_id: str) -> bool:
        """Clear conversation history for a session"""
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.bot_id == bot_id,
                Conversation.session_id == session_id
            )
            .first()
        )

        if conversation:
            db.query(Message).filter(
                Message.conversation_id == conversation.id
            ).delete()
            db.commit()
            return True

        return False
