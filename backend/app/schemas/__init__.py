from app.schemas.student import StudentCreate, StudentUpdate, StudentOut
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut, TaskCompletionBase, TaskCompletionOut, DailyProgress
from app.schemas.wish import WishCreate, WishUpdate, WishOut, RewardCreate, RewardOut
from app.schemas.points import PointsRecordOut, PointsSummary

__all__ = [
    "StudentCreate", "StudentUpdate", "StudentOut",
    "TaskCreate", "TaskUpdate", "TaskOut", "TaskCompletionBase", "TaskCompletionOut", "DailyProgress",
    "WishCreate", "WishUpdate", "WishOut", "RewardCreate", "RewardOut",
    "PointsRecordOut", "PointsSummary",
]
