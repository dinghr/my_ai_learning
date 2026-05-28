import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.message import ChatRequest, ChatResponse, MessageOut, SessionOut, QuickReply
from app.services.message import get_or_create_session, get_session_messages, create_message, get_recent_sessions
from app.services.ai import detect_intent, chat_with_ai, get_quick_replies
from typing import Optional, List

router = APIRouter(prefix="/api/students/{student_id}/ai-chat", tags=["ai-chat"])
logger = logging.getLogger(__name__)


@router.post("/chat", response_model=ChatResponse)
def chat(student_id: str, request: ChatRequest, db: Session = Depends(get_db)):
    """
    发送消息并获取AI回复。
    流程：保存用户消息 → 识别意图 → 调用AI → 保存AI回复 → 返回结果
    """
    logger.info(f"[CHAT_REQ] student={student_id} | msg={request.message[:50]}... | session={request.session_id}")
    
    # 1. 保存用户消息
    from app.schemas.message import MessageCreate
    user_msg = create_message(
        db, student_id,
        MessageCreate(content=request.message, session_id=request.session_id, image_url=request.image_url),
        role="user"
    )
    logger.info(f"[CHAT_REQ] user_msg saved | id={user_msg.id}")
    
    # 2. 识别意图
    intent_result = detect_intent(request.message)
    intent = intent_result.get("intent", "chat")
    confidence = intent_result.get("confidence", 50)
    logger.info(f"[CHAT_REQ] intent={intent} | confidence={confidence}")
    
    # 3. 获取对话历史（用于上下文）
    history = []
    if user_msg.session_id:
        past_messages = get_session_messages(db, user_msg.session_id, limit=10)
        for msg in past_messages:
            if msg.id != user_msg.id:  # 排除刚保存的消息
                history.append({"role": msg.role, "content": msg.content})
        logger.info(f"[CHAT_REQ] history loaded | len={len(history)}")
    
    # 4. 调用AI
    ai_result = chat_with_ai(request.message, history=history, intent=intent)
    ai_text = ai_result.get("text_response", "")
    ai_poem = ai_result.get("poem")
    logger.info(f"[CHAT_REQ] ai_result | success={ai_result.get('success')} | text_len={len(ai_text)}")
    
    # 5. 保存AI回复
    meta = {"intent_explanation": intent_result.get("explanation", "")}
    if ai_poem:
        meta["poem"] = ai_poem
    
    ai_msg = create_message(
        db, student_id,
        MessageCreate(content=ai_text, session_id=user_msg.session_id),
        role="assistant",
        intent=intent,
        intent_confidence=confidence,
        meta=meta
    )
    logger.info(f"[CHAT_REQ] ai_msg saved | id={ai_msg.id}")
    
    # 6. 获取快捷回复建议
    suggestions = get_quick_replies(intent)
    
    return ChatResponse(
        message=MessageOut.model_validate(ai_msg),
        intent=intent,
        suggestions=[s["prompt"] for s in suggestions[:3]]
    )


@router.get("/sessions", response_model=list[SessionOut])
def list_sessions(student_id: str, db: Session = Depends(get_db)):
    """获取会话列表。"""
    return get_recent_sessions(db, student_id)


@router.get("/sessions/{session_id}/messages", response_model=list[MessageOut])
def get_messages(student_id: str, session_id: str, db: Session = Depends(get_db)):
    """获取会话消息。"""
    return get_session_messages(db, session_id)


@router.get("/quick-replies", response_model=list[QuickReply])
def quick_replies(student_id: str, intent: Optional[str] = None):
    """获取快捷回复建议。"""
    replies = get_quick_replies(intent)
    return [QuickReply(**r) for r in replies]
