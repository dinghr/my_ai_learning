from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


class MessageBase(BaseModel):
    content: str
    content_type: Optional[str] = "text"
    image_url: Optional[str] = None


class MessageCreate(MessageBase):
    session_id: Optional[str] = None


class MessageOut(BaseModel):
    id: str
    student_id: str
    role: str
    content: str
    content_type: str
    intent: Optional[str] = None
    intent_confidence: Optional[int] = None
    image_url: Optional[str] = None
    session_id: str
    meta: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    image_url: Optional[str] = None


class ChatResponse(BaseModel):
    message: MessageOut
    intent: Optional[str] = None
    suggestions: Optional[list[str]] = None


class IntentResult(BaseModel):
    intent: str
    confidence: int
    explanation: Optional[str] = None


class SessionOut(BaseModel):
    id: str
    student_id: str
    title: Optional[str] = None
    summary: Optional[str] = None
    message_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuickReply(BaseModel):
    label: str
    icon: str
    prompt: str
