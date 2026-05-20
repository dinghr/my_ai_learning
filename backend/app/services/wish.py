from sqlalchemy.orm import Session
from app.models.wish import Wish, Reward
from app.services.points import add_points
from app.schemas.wish import WishCreate, WishUpdate


def get_wish(db: Session, wish_id: str):
    return db.query(Wish).filter(Wish.id == wish_id).first()


def get_wishes(db: Session, student_id: str):
    return db.query(Wish).filter(
        Wish.student_id == student_id,
        Wish.status.in_(["active", "completed"])
    ).order_by(Wish.created_at.desc()).all()


def get_featured_wish(db: Session, student_id: str):
    """获取底部展示的愿望。"""
    return db.query(Wish).filter(
        Wish.student_id == student_id,
        Wish.status == "active",
        Wish.is_featured == True
    ).first()


def create_wish(db: Session, student_id: str, wish: WishCreate):
    db_wish = Wish(student_id=student_id, **wish.model_dump())
    db.add(db_wish)
    db.commit()
    db.refresh(db_wish)
    return db_wish


def update_wish(db: Session, wish_id: str, wish: WishUpdate):
    db_wish = db.query(Wish).filter(Wish.id == wish_id).first()
    if not db_wish:
        return None
    update_data = wish.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_wish, key, value)
    db.commit()
    db.refresh(db_wish)
    return db_wish


def add_wish_progress(db: Session, student_id: str, wish_id: str, points: int):
    """向愿望添加进度积分。"""
    db_wish = db.query(Wish).filter(Wish.id == wish_id).first()
    if not db_wish or db_wish.student_id != student_id:
        return None, "愿望不存在"
    
    if db_wish.status != "active":
        return None, "愿望已完成"
    
    db_wish.points_progress = min(db_wish.points_required, db_wish.points_progress + points)
    
    # 扣除积分
    add_points(db, student_id, -points, "wish", wish_id, f"投入「{db_wish.name}」{points} 积分")
    
    db.commit()
    db.refresh(db_wish)
    return db_wish, None


def complete_wish(db: Session, student_id: str, wish_id: str):
    """完成愿望。"""
    db_wish = db.query(Wish).filter(Wish.id == wish_id).first()
    if not db_wish or db_wish.student_id != student_id:
        return None, "愿望不存在"
    
    if db_wish.status == "completed":
        return None, "愿望已达成"
    
    from datetime import datetime
    db_wish.status = "completed"
    db_wish.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(db_wish)
    return db_wish, None


def delete_wish(db: Session, wish_id: str):
    db_wish = db.query(Wish).filter(Wish.id == wish_id).first()
    if not db_wish:
        return False
    db_wish.status = "cancelled"
    db.commit()
    return True


# Reward services

def get_rewards(db: Session):
    return db.query(Reward).filter(Reward.is_active == True).all()


def create_reward(db: Session, reward_data: dict):
    db_reward = Reward(**reward_data)
    db.add(db_reward)
    db.commit()
    db.refresh(db_reward)
    return db_reward
