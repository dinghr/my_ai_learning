from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, ForeignKey, Text, JSON
from app.database import Base
import uuid
from datetime import datetime


class Task(Base):
    """任务表：每日任务 + 长期目标"""
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id"), nullable=False)
    
    # 任务信息
    name = Column(String(100), nullable=False)
    description = Column(Text)
    icon = Column(String(50), default="⭐")
    task_type = Column(String(20), default="daily")  # daily / long_term
    category = Column(String(20))  # sport / labor / writing / reading / custom
    
    # 积分
    points = Column(Integer, default=10)
    
    # 长期目标专用
    target_value = Column(Integer, nullable=True)  # 目标值（如阅读120页）
    current_value = Column(Integer, default=0)     # 当前进度
    unit = Column(String(20), nullable=True)       # 单位（页/天/次）
    
    # 配置
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TaskCompletion(Base):
    """任务完成记录"""
    __tablename__ = "task_completions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id"), nullable=False)
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False)
    
    # 完成信息
    completed_date = Column(Date, nullable=False)
    points_earned = Column(Integer, default=0)
    note = Column(Text, nullable=True)
    
    # 长期目标进度增量
    progress_increment = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
