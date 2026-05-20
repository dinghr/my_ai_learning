from sqlalchemy import Column, String, Integer, DateTime, JSON, Enum, Index
from app.database import Base
import uuid
from datetime import datetime


class Character(Base):
    """识字表 - 记录小朋友认识的生字"""
    __tablename__ = "characters"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), nullable=False, index=True)

    # 生字信息
    character = Column(String(10), nullable=False)  # 单个汉字
    pinyin = Column(String(50))                     # 拼音
    radical = Column(String(50))                    # 偏旁部首
    words = Column(JSON, default=list)              # 组词 ["蝴蝶", "蝴蝶结"]
    example = Column(String(500))                   # 例句
    brainstorm = Column(JSON, default=list)         # 同偏旁字 ["蜻", "蜓", "蚂"]

    # 学习状态: new(新录入) | learning(在学) | known(已掌握) | forgotten(遗忘)
    status = Column(String(20), default="new")

    # 检测统计
    review_count = Column(Integer, default=0)       # 总复习次数
    correct_count = Column(Integer, default=0)      # 认识次数
    wrong_count = Column(Integer, default=0)        # 不认识次数

    # 分组检测用
    group_id = Column(Integer, default=0)           # 当前所属组
    review_round = Column(Integer, default=0)       # 当前复习轮次

    # 复习计划（艾宾浩斯）
    last_reviewed_at = Column(DateTime)
    next_review_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_student_char', 'student_id', 'character', unique=True),
    )


class ReviewLog(Base):
    """复习记录表 - 每次检测的详细记录"""
    __tablename__ = "review_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), nullable=False, index=True)
    character_id = Column(String(36), nullable=False, index=True)

    # 检测结果: know | unknow | study(再学一下)
    result = Column(String(20), nullable=False)
    group_id = Column(Integer, default=0)
    review_round = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
