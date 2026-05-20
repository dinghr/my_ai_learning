from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional


class TaskBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = "⭐"
    task_type: Optional[str] = "daily"  # daily / long_term
    category: Optional[str] = None      # sport / labor / writing / reading / custom
    points: Optional[int] = 10
    target_value: Optional[int] = None
    current_value: Optional[int] = 0
    unit: Optional[str] = None
    is_active: Optional[bool] = True
    sort_order: Optional[int] = 0


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    task_type: Optional[str] = None
    category: Optional[str] = None
    points: Optional[int] = None
    target_value: Optional[int] = None
    current_value: Optional[int] = None
    unit: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class TaskOut(TaskBase):
    id: str
    student_id: str
    created_at: datetime
    updated_at: datetime
    is_completed_today: bool = False
    today_completion_id: Optional[str] = None

    class Config:
        from_attributes = True


class TaskCompletionBase(BaseModel):
    task_id: Optional[str] = None  # URL路径中已提供
    note: Optional[str] = None
    progress_increment: Optional[int] = None


class TaskCompletionOut(BaseModel):
    id: str
    student_id: str
    task_id: str
    completed_date: date
    points_earned: int
    note: Optional[str] = None
    progress_increment: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DailyProgress(BaseModel):
    total: int
    completed: int
    percentage: int
    points_today: int
