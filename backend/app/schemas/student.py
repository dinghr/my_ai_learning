from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class StudentBase(BaseModel):
    name: str = Field(..., max_length=64)
    nickname: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    grade: Optional[str] = None
    avatar: Optional[str] = None


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    nickname: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    grade: Optional[str] = None
    avatar: Optional[str] = None


class StudentOut(StudentBase):
    id: str
    openid: Optional[str] = None
    points_balance: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
