from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class WishBase(BaseModel):
    name: str = Field(..., max_length=100)
    icon: Optional[str] = "🎁"
    description: Optional[str] = None
    points_required: int


class WishCreate(WishBase):
    is_featured: Optional[bool] = False


class WishUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    points_required: Optional[int] = None
    status: Optional[str] = None
    is_featured: Optional[bool] = None


class WishOut(WishBase):
    id: str
    student_id: str
    points_progress: int
    status: str
    is_featured: bool
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RewardBase(BaseModel):
    name: str = Field(..., max_length=100)
    icon: Optional[str] = "🎁"
    description: Optional[str] = None
    points_cost: int


class RewardCreate(RewardBase):
    pass


class RewardOut(RewardBase):
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
