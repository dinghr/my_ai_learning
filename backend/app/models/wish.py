from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from app.database import Base
import uuid
from datetime import datetime


class Wish(Base):
    """愿望表"""
    __tablename__ = "wishes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id"), nullable=False)
    
    # 愿望信息
    name = Column(String(100), nullable=False)
    icon = Column(String(50), default="🎁")
    description = Column(Text)
    
    # 积分
    points_required = Column(Integer, nullable=False)
    points_progress = Column(Integer, default=0)
    
    # 状态
    status = Column(String(20), default="active")  # active / completed / cancelled
    is_featured = Column(Boolean, default=False)   # 是否在底部进度条展示
    
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Reward(Base):
    """奖励商城表"""
    __tablename__ = "rewards"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    name = Column(String(100), nullable=False)
    icon = Column(String(50), default="🎁")
    description = Column(Text)
    points_cost = Column(Integer, nullable=False)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
