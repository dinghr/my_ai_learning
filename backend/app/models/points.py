from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from app.database import Base
import uuid
from datetime import datetime


class PointsRecord(Base):
    """积分记录表"""
    __tablename__ = "points_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id"), nullable=False)
    
    # 积分变动
    points = Column(Integer, nullable=False)  # 正数获得，负数消耗
    balance = Column(Integer, nullable=False)  # 变动后余额
    
    # 来源
    source_type = Column(String(50), nullable=False)  # task / reward / wish / manual
    source_id = Column(String(36), nullable=True)     # 关联记录ID
    description = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
