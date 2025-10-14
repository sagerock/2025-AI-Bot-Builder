from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.bot_service import BotService
from app.services.chat_service import ChatService
from app.services.memory_service import MemoryService

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/{bot_id}", response_model=ChatResponse)
def chat(bot_id: str, request: ChatRequest, db: Session = Depends(get_db)):
    """
    Send a message to a bot and get a response
    """
    # Get bot
    bot = BotService.get_bot(db, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    # Refresh bot from database to get latest data
    db.refresh(bot)

    # Get or create conversation
    conversation, session_id = MemoryService.get_or_create_conversation(
        db, bot_id, request.session_id
    )

    # Get conversation history if memory is enabled
    history = []
    if bot.enable_memory:
        history = MemoryService.get_conversation_history(
            db, conversation.id, bot.memory_max_messages
        )

    # Get RAG contexts if enabled
    rag_contexts = None
    if bot.use_qdrant and bot.qdrant_collection:
        rag_contexts = ChatService.get_rag_contexts(bot, request.message)

    # Save user message
    MemoryService.add_message(
        db, conversation.id, "user", request.message
    )

    # Generate response
    try:
        response_text = ChatService.chat(
            bot, request.message, history, rag_contexts
        )
    except Exception as e:
        import traceback
        error_detail = f"AI provider error: {str(e)}\n{traceback.format_exc()}"
        print(f"ERROR in chat: {error_detail}")  # Log to console
        raise HTTPException(status_code=500, detail=f"AI provider error: {str(e)}")

    # Save assistant response
    MemoryService.add_message(
        db,
        conversation.id,
        "assistant",
        response_text,
        rag_context="\n".join(rag_contexts) if rag_contexts else None
    )

    return ChatResponse(
        response=response_text,
        session_id=session_id,
        rag_context=rag_contexts if rag_contexts else None
    )


@router.delete("/{bot_id}/session/{session_id}", status_code=204)
def clear_session(bot_id: str, session_id: str, db: Session = Depends(get_db)):
    """Clear conversation history for a session"""
    success = MemoryService.clear_conversation(db, session_id, bot_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return None
