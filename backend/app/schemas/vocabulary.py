from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class CharacterCreate(BaseModel):
    """录入生字请求"""
    character: str
    pinyin: Optional[str] = None
    radical: Optional[str] = None
    words: Optional[List[str]] = None
    example: Optional[str] = None
    brainstorm: Optional[List[str]] = None


class CharacterOut(BaseModel):
    """生字返回"""
    id: str
    character: str
    pinyin: Optional[str]
    radical: Optional[str]
    words: List[str]
    example: Optional[str]
    brainstorm: List[str]
    status: str
    review_count: int
    correct_count: int
    wrong_count: int
    group_id: int
    review_round: int
    last_reviewed_at: Optional[datetime]
    next_review_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class CharacterBatchCreate(BaseModel):
    """批量录入生字"""
    characters: List[str]


class QuizGroup(BaseModel):
    """检测分组返回"""
    group_id: int
    characters: List[CharacterOut]
    total: int


class ReviewSubmit(BaseModel):
    """提交检测结果"""
    character_id: str
    result: str  # know | unknow | study
    group_id: int
    review_round: int = 0


class ReviewSubmitBatch(BaseModel):
    """批量提交检测结果"""
    results: List[ReviewSubmit]


class ReadingRequest(BaseModel):
    """生成精读短文请求"""
    character_ids: Optional[List[str]] = None  # 指定生字，不传则取最近不认识的
    theme: Optional[str] = "日常"               # 主题


class ReadingOut(BaseModel):
    """精读短文返回"""
    title: str
    content: List[dict]  # [{"hz": "春", "py": "chūn", "highlight": false}, ...]
    summary: str
