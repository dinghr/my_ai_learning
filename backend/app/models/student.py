from sqlalchemy import Column, String, Integer, DateTime, JSON
from app.database import Base
import uuid
from datetime import datetime


class Student(Base):
    """小朋友表"""
    __tablename__ = "students"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(64), nullable=False)
    nickname = Column(String(64))
    age = Column(Integer)
    gender = Column(String(10))  # boy / girl
    grade = Column(String(20))
    
    # 积分
    points_balance = Column(Integer, default=0)
    
    # 扩展
    openid = Column(String(128), unique=True, nullable=True, index=True)
    avatar = Column(String(255))
    settings = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
