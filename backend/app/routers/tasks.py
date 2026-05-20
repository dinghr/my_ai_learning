from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut, TaskCompletionBase, TaskCompletionOut, DailyProgress
from app.services.task import get_tasks, get_task, create_task, update_task, delete_task, complete_task, get_daily_progress, get_completion_status
from typing import Optional

router = APIRouter(prefix="/api/students/{student_id}/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskOut])
def list_tasks(student_id: str, task_type: Optional[str] = None, db: Session = Depends(get_db)):
    tasks = get_tasks(db, student_id, task_type)
    # 标记今日完成状态
    for t in tasks:
        completion = get_completion_status(db, student_id, t.id)
        t.is_completed_today = completion is not None
        t.today_completion_id = completion.id if completion else None
    return tasks


@router.post("", response_model=TaskOut)
def create_new_task(student_id: str, task: TaskCreate, db: Session = Depends(get_db)):
    return create_task(db, student_id, task)


@router.put("/{task_id}", response_model=TaskOut)
def update_existing_task(student_id: str, task_id: str, task: TaskUpdate, db: Session = Depends(get_db)):
    db_task = update_task(db, task_id, task)
    if not db_task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return db_task


@router.delete("/{task_id}")
def remove_task(student_id: str, task_id: str, db: Session = Depends(get_db)):
    if delete_task(db, task_id):
        return {"success": True}
    raise HTTPException(status_code=404, detail="任务不存在")


@router.post("/{task_id}/complete", response_model=TaskCompletionOut)
def complete_daily_task(student_id: str, task_id: str, data: TaskCompletionBase, db: Session = Depends(get_db)):
    completion, error = complete_task(db, student_id, task_id, data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return completion


@router.get("/progress/daily", response_model=DailyProgress)
def read_daily_progress(student_id: str, db: Session = Depends(get_db)):
    return get_daily_progress(db, student_id)
