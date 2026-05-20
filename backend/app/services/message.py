from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.message import Message, ChatSession
from app.schemas.message import MessageCreate
from typing import Optional, List


def get_session(db: Session, session_id: str):
    return db.query(ChatSession).filter(ChatSession.id == session_id).first()


def get_or_create_session(db: Session, student_id: str, session_id: Optional[str] = None):
    """获取或创建会话。"""
    if session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.student_id == student_id
        ).first()
        if session:
            return session
    
    # 创建新会话
    session = ChatSession(student_id=student_id, title="新对话")
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session_messages(db: Session, session_id: str, limit: int = 50):
    """获取会话消息历史。"""
    return db.query(Message).filter(
        Message.session_id == session_id
    ).order_by(Message.created_at.asc()).limit(limit).all()


def create_message(db: Session, student_id: str, data: MessageCreate, 
                   role: str = "user", intent: Optional[str] = None,
                   intent_confidence: Optional[int] = None,
                   meta: Optional[dict] = None):
    """创建消息。"""
    session = get_or_create_session(db, student_id, data.session_id)
    
    msg = Message(
        student_id=student_id,
        session_id=session.id,
        role=role,
        content=data.content,
        content_type=data.content_type or "text",
        image_url=data.image_url,
        intent=intent,
        intent_confidence=intent_confidence,
        meta=meta or {},
    )
    db.add(msg)
    
    # 更新会话计数
    session.message_count = db.query(func.count(Message.id)).filter(
        Message.session_id == session.id
    ).scalar() + 1
    session.updated_at = func.now()
    
    db.commit()
    db.refresh(msg)
    return msg


def get_recent_sessions(db: Session, student_id: str, limit: int = 10):
    """获取最近的会话列表。"""
    return db.query(ChatSession).filter(
        ChatSession.student_id == student_id
    ).order_by(ChatSession.updated_at.desc()).limit(limit).all()
