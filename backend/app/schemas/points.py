from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PointsRecordBase(BaseModel):
    points: int
    source_type: str
    description: Optional[str] = None


class PointsRecordOut(PointsRecordBase):
    id: str
    student_id: str
    balance: int
    source_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PointsSummary(BaseModel):
    balance: int
    total_earned: int
    total_spent: int
