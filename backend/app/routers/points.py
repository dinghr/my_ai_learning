from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.points import PointsRecordOut, PointsSummary
from app.services.points import get_points_records, get_points_summary, add_points

router = APIRouter(prefix="/api/students/{student_id}/points", tags=["points"])


@router.get("/records", response_model=list[PointsRecordOut])
def list_records(student_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_points_records(db, student_id, skip, limit)


@router.get("/summary", response_model=PointsSummary)
def read_summary(student_id: str, db: Session = Depends(get_db)):
    return get_points_summary(db, student_id)


@router.post("/add")
def add_points_manual(student_id: str, points: int, description: str = None, db: Session = Depends(get_db)):
    """手动调整积分（用于奖励发放或人工修正）。"""
    record = add_points(db, student_id, points, "manual", description=description)
    if not record:
        raise HTTPException(status_code=404, detail="学生不存在")
    return record
