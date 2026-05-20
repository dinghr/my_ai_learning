from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.wish import WishCreate, WishUpdate, WishOut, RewardCreate, RewardOut
from app.services.wish import get_wishes, get_wish, create_wish, update_wish, add_wish_progress, complete_wish, delete_wish, get_rewards, create_reward, get_featured_wish
from typing import Optional

router = APIRouter(prefix="/api/students/{student_id}/wishes", tags=["wishes"])


@router.get("", response_model=list[WishOut])
def list_wishes(student_id: str, db: Session = Depends(get_db)):
    return get_wishes(db, student_id)


@router.get("/featured", response_model=Optional[WishOut])
def read_featured_wish(student_id: str, db: Session = Depends(get_db)):
    return get_featured_wish(db, student_id)


@router.post("", response_model=WishOut)
def create_new_wish(student_id: str, wish: WishCreate, db: Session = Depends(get_db)):
    return create_wish(db, student_id, wish)


@router.put("/{wish_id}", response_model=WishOut)
def update_existing_wish(student_id: str, wish_id: str, wish: WishUpdate, db: Session = Depends(get_db)):
    db_wish = update_wish(db, wish_id, wish)
    if not db_wish:
        raise HTTPException(status_code=404, detail="愿望不存在")
    return db_wish


from pydantic import BaseModel

class WishProgressRequest(BaseModel):
    points: int

@router.post("/{wish_id}/progress")
def add_progress(student_id: str, wish_id: str, data: WishProgressRequest, db: Session = Depends(get_db)):
    db_wish, error = add_wish_progress(db, student_id, wish_id, data.points)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return db_wish


@router.post("/{wish_id}/complete")
def finish_wish(student_id: str, wish_id: str, db: Session = Depends(get_db)):
    db_wish, error = complete_wish(db, student_id, wish_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return db_wish


@router.delete("/{wish_id}")
def remove_wish(student_id: str, wish_id: str, db: Session = Depends(get_db)):
    if delete_wish(db, wish_id):
        return {"success": True}
    raise HTTPException(status_code=404, detail="愿望不存在")


# 奖励商城（全局）
reward_router = APIRouter(prefix="/api/rewards", tags=["rewards"])


@reward_router.get("", response_model=list[RewardOut])
def list_rewards(db: Session = Depends(get_db)):
    return get_rewards(db)


@reward_router.post("", response_model=RewardOut)
def create_new_reward(reward: RewardCreate, db: Session = Depends(get_db)):
    return create_reward(db, reward.model_dump())
