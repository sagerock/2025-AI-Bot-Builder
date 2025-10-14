from pydantic import BaseModel, Field
from typing import Optional, List


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: Optional[str] = None  # For maintaining conversation history


class ChatResponse(BaseModel):
    response: str
    session_id: str
    rag_context: Optional[List[str]] = None  # Context snippets used from RAG
