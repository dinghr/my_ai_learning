from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.points import PointsRecord
from app.services.student import update_points


def get_points_records(db: Session, student_id: str, skip: int = 0, limit: int = 100):
    return db.query(PointsRecord).filter(
        PointsRecord.student_id == student_id
    ).order_by(PointsRecord.created_at.desc()).offset(skip).limit(limit).all()


def get_points_summary(db: Session, student_id: str):
    total_earned = db.query(func.sum(PointsRecord.points)).filter(
        PointsRecord.student_id == student_id,
        PointsRecord.points > 0
    ).scalar() or 0
    
    total_spent = abs(db.query(func.sum(PointsRecord.points)).filter(
        PointsRecord.student_id == student_id,
        PointsRecord.points < 0
    ).scalar() or 0)
    
    balance = db.query(PointsRecord).filter(
        PointsRecord.student_id == student_id
    ).order_by(PointsRecord.created_at.desc()).first()
    
    return {
        "balance": balance.balance if balance else 0,
        "total_earned": total_earned,
        "total_spent": total_spent
    }


def add_points(db: Session, student_id: str, points: int, source_type: str, 
               source_id: str = None, description: str = None):
    """手动添加积分（扣分时points为负数）。"""
    student = update_points(db, student_id, points)
    if not student:
        return None
    
    record = PointsRecord(
        student_id=student_id,
        points=points,
        balance=student.points_balance,
        source_type=source_type,
        source_id=source_id,
        description=description or f"{'获得' if points > 0 else '消耗'} {abs(points)} 积分"
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
