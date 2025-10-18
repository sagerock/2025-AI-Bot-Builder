from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import base64
from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.bot_service import BotService
from app.services.chat_service import ChatService
from app.services.memory_service import MemoryService
from app.services.document_service import document_service
from app.services.webhook_service import WebhookService
from app.utils.jwt_auth import get_current_user_from_token

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Supported image formats
IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

def is_image_file(filename: str) -> bool:
    """Check if file is an image"""
    import os
    ext = os.path.splitext(filename.lower())[1]
    return ext in IMAGE_FORMATS

def get_image_mime_type(filename: str) -> str:
    """Get MIME type for image"""
    import os
    ext = os.path.splitext(filename.lower())[1]
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    return mime_types.get(ext, 'image/jpeg')


@router.post("/{bot_id}", response_model=ChatResponse)
async def chat(
    bot_id: str,
    message: str = Form(...),
    session_id: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    full_document: Optional[str] = None,
    authorization: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Send a message to a bot and get a response, with optional file upload

    Args:
        bot_id: ID of the bot to chat with
        message: User message text
        session_id: Optional session ID for conversation continuity
        file: Optional file upload (image or document)
        full_document: Optional filename to retrieve ALL chunks from Qdrant (instead of RAG search)
        authorization: Optional JWT token for authentication
        db: Database session

    Example full_document usage:
        POST /api/chat/{bot_id}?full_document=chapter-3.pdf
        Body: { "message": "Create an outline of this chapter" }

        This will retrieve ALL chunks from "chapter-3.pdf" instead of using RAG search.
    """
    # Extract user info from token if provided
    user_info = None
    if authorization:
        try:
            user_info = await get_current_user_from_token(authorization)
        except:
            pass  # Token auth is optional for chat

    user_id = user_info.get("sub") if user_info else None
    user_email = user_info.get("email") if user_info else None

    # Get bot
    bot = BotService.get_bot(db, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    # Refresh bot from database to get latest data
    db.refresh(bot)

    # Get or create conversation
    conversation, session_id = MemoryService.get_or_create_conversation(
        db, bot_id, session_id
    )

    # Fire webhook for conversation_started if this is a new conversation
    is_new_conversation = not session_id or conversation.id == session_id
    if is_new_conversation:
        WebhookService.trigger_event(
            db=db,
            event="conversation_started",
            bot_id=bot_id,
            bot_name=bot.name,
            session_id=session_id,
            user_id=user_id,
            user_email=user_email,
            data={"initial_message": message[:100]}
        )

    # Get conversation history if memory is enabled
    history = []
    if bot.enable_memory:
        history = MemoryService.get_conversation_history(
            db, conversation.id, bot.memory_max_messages
        )

    # Process uploaded file if present
    file_context = None
    image_data = None

    if file and file.filename:
        try:
            # Read file content
            file_content = await file.read()

            # Validate file size (10MB limit)
            max_size = 10 * 1024 * 1024
            if len(file_content) > max_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Maximum size is 10MB"
                )

            # Check if it's an image
            if is_image_file(file.filename):
                # Encode image as base64
                base64_image = base64.b64encode(file_content).decode('utf-8')
                mime_type = get_image_mime_type(file.filename)
                image_data = {
                    'base64': base64_image,
                    'mime_type': mime_type,
                    'filename': file.filename
                }
            else:
                # Extract text from document
                extracted_text = document_service.extract_text(file.filename, file_content)

                if extracted_text.strip():
                    file_context = f"\n\n[Uploaded file: {file.filename}]\n{extracted_text[:100000]}"  # Limit to 100,000 chars
                else:
                    file_context = f"\n\n[Uploaded file: {file.filename}] (No text could be extracted)"
        except Exception as e:
            print(f"File processing error: {e}")
            file_context = f"\n\n[Uploaded file: {file.filename}] (Error processing file: {str(e)})"

    # Append file context to message if present (for documents)
    enhanced_message = message
    if file_context:
        enhanced_message = message + file_context

    # Get RAG contexts if enabled
    rag_contexts = None
    if bot.use_qdrant and bot.qdrant_collection:
        if full_document:
            # Retrieve ALL chunks from the specified document
            from app.services.qdrant_service import qdrant_service
            full_text = qdrant_service.get_all_chunks_for_document(
                collection_name=bot.qdrant_collection,
                filename=full_document
            )
            if full_text:
                rag_contexts = [full_text]
            else:
                # Document not found, fall back to normal RAG search
                rag_contexts = ChatService.get_rag_contexts(bot, message)
        else:
            # Normal RAG search with top_k chunks
            rag_contexts = ChatService.get_rag_contexts(bot, message)

    # Save user message (with file indicator if present)
    user_message_display = message
    if file and file.filename:
        user_message_display = f"{message}\n[Attached: {file.filename}]"

    MemoryService.add_message(
        db, conversation.id, "user", user_message_display
    )

    # Fire webhook for message_sent
    WebhookService.trigger_event(
        db=db,
        event="message_sent",
        bot_id=bot_id,
        bot_name=bot.name,
        session_id=session_id,
        user_id=user_id,
        user_email=user_email,
        data={
            "message": message,
            "has_file": bool(file and file.filename),
            "file_name": file.filename if file else None
        }
    )

    # Generate response
    try:
        response_text = ChatService.chat(
            bot, enhanced_message, history, rag_contexts, image_data
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

    # Fire webhook for message_received
    WebhookService.trigger_event(
        db=db,
        event="message_received",
        bot_id=bot_id,
        bot_name=bot.name,
        session_id=session_id,
        user_id=user_id,
        user_email=user_email,
        data={
            "user_message": message,
            "bot_response": response_text,
            "has_rag_context": bool(rag_contexts)
        }
    )

    return ChatResponse(
        response=response_text,
        session_id=session_id,
        rag_context=rag_contexts if rag_contexts else None
    )


@router.delete("/{bot_id}/session/{session_id}", status_code=204)
def clear_session(bot_id: str, session_id: str, db: Session = Depends(get_db)):
    """Clear conversation history for a session"""
    # Get bot info for webhook
    bot = BotService.get_bot(db, bot_id)

    success = MemoryService.clear_conversation(db, session_id, bot_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")

    # Fire webhook for conversation_ended
    if bot:
        WebhookService.trigger_event(
            db=db,
            event="conversation_ended",
            bot_id=bot_id,
            bot_name=bot.name,
            session_id=session_id,
            user_id=None,
            user_email=None,
            data={"reason": "session_cleared"}
        )

    return None
