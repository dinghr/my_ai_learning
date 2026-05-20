from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, ForeignKey
from app.database import Base
import uuid
from datetime import datetime


class Message(Base):
    """AI对话消息表"""
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id"), nullable=False)
    
    # 消息内容
    role = Column(String(20), nullable=False)  # user / assistant / system
    content = Column(Text, nullable=False)
    content_type = Column(String(20), default="text")  # text / image / mixed
    
    # 意图识别结果（仅assistant消息）
    intent = Column(String(50), nullable=True)  # wrong_question / poem / math / general / chat
    intent_confidence = Column(Integer, nullable=True)  # 0-100
    
    # 多媒体
    image_url = Column(String(500), nullable=True)
    
    # 会话分组
    session_id = Column(String(36), nullable=False, default=lambda: str(uuid.uuid4()))
    
    # 元数据
    meta = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatSession(Base):
    """对话会话表"""
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id"), nullable=False)
    
    title = Column(String(100), nullable=True)
    summary = Column(Text, nullable=True)
    
    # 消息计数
    message_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
