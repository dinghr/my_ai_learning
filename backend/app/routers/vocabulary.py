from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.vocabulary import (
    CharacterCreate, CharacterOut, CharacterBatchCreate,
    QuizGroup, ReviewSubmitBatch, ReadingRequest, ReadingOut
)
from app.services.vocabulary import (
    create_character, batch_create_characters, get_characters,
    get_quiz_group, submit_reviews, generate_reading
)

router = APIRouter(prefix="/api/students/{student_id}/literacy", tags=["literacy"])


@router.post("/characters", response_model=CharacterOut)
def add_character(student_id: str, data: CharacterCreate, db: Session = Depends(get_db)):
    """录入单个生字，自动调用 AI 补全信息。"""
    return create_character(db, student_id, data)


@router.post("/characters/batch", response_model=List[CharacterOut])
def add_characters_batch(student_id: str, data: CharacterBatchCreate, db: Session = Depends(get_db)):
    """批量录入生字。"""
    return batch_create_characters(db, student_id, data.characters)


@router.get("/characters", response_model=List[CharacterOut])
def list_characters(student_id: str, status: Optional[str] = None, db: Session = Depends(get_db)):
    """获取生字列表，可按状态筛选。"""
    return get_characters(db, student_id, status)


@router.get("/quiz", response_model=QuizGroup)
def get_quiz(student_id: str, db: Session = Depends(get_db)):
    """获取一组待检测生字（4字一组）。"""
    return get_quiz_group(db, student_id)


@router.post("/quiz/submit", response_model=List[CharacterOut])
def submit_quiz(student_id: str, data: ReviewSubmitBatch, db: Session = Depends(get_db)):
    """批量提交检测结果。"""
    return submit_reviews(db, student_id, data.results)


@router.post("/reading", response_model=ReadingOut)
def create_reading(student_id: str, data: Optional[ReadingRequest] = None, db: Session = Depends(get_db)):
    """生成经典优美阅读片段。"""
    req = data or ReadingRequest()
    return generate_reading(db, student_id, theme=req.theme or "随机")
