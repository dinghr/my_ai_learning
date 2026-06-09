from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from app.models.task import Task, TaskCompletion
from app.models.points import PointsRecord
from app.schemas.task import TaskCreate, TaskUpdate, TaskCompletionBase
from app.services.student import update_points


def get_task(db: Session, task_id: str):
    return db.query(Task).filter(Task.id == task_id).first()


def get_tasks(db: Session, student_id: str, task_type: str = None):
    query = db.query(Task).filter(Task.student_id == student_id, Task.is_active == True)
    if task_type:
        query = query.filter(Task.task_type == task_type)
    return query.order_by(Task.sort_order, Task.created_at).all()


def create_task(db: Session, student_id: str, task: TaskCreate):
    db_task = Task(student_id=student_id, **task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: str, task: TaskUpdate):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        return None
    update_data = task.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: str):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        return False
    db_task.is_active = False
    db.commit()
    return True


def complete_task(db: Session, student_id: str, task_id: str, data: TaskCompletionBase):
    """完成任务并发放积分。"""
    today = date.today()
    
    # 检查今日是否已完成
    existing = db.query(TaskCompletion).filter(
        TaskCompletion.task_id == task_id,
        TaskCompletion.completed_date == today
    ).first()
    if existing:
        return None, "今日已完成"
    
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        return None, "任务不存在"
    
    points = db_task.points
    progress_increment = data.progress_increment
    
    # 长期任务进度更新
    if db_task.task_type == "long_term" and progress_increment:
        db_task.current_value = min(db_task.target_value or 999999, db_task.current_value + progress_increment)
        # 如果完成，根据剩余进度比例给分
        if db_task.current_value >= (db_task.target_value or 999999):
            progress_increment = None  # 不重复计分
    
    # 创建完成记录
    completion = TaskCompletion(
        student_id=student_id,
        task_id=task_id,
        completed_date=today,
        points_earned=points,
        note=data.note,
        progress_increment=progress_increment
    )
    db.add(completion)
    
    # 更新学生积分（如学生不存在则自动创建）
    from app.services.student import get_student, create_student
    student = get_student(db, student_id)
    if not student:
        from app.schemas.student import StudentCreate
        student = create_student(db, StudentCreate(id=student_id, name="小朋友", avatar="🦕"))
    
    student = update_points(db, student_id, points)
    balance = student.points_balance if student else points
    
    # 创建积分记录
    points_record = PointsRecord(
        student_id=student_id,
        points=points,
        balance=balance,
        source_type="task",
        source_id=completion.id,
        description=f"完成「{db_task.name}」获得 {points} 积分"
    )
    db.add(points_record)
    
    db.commit()
    db.refresh(completion)
    return completion, None


def get_daily_progress(db: Session, student_id: str):
    """获取今日打卡进度。"""
    today = date.today()
    tasks = db.query(Task).filter(
        Task.student_id == student_id,
        Task.is_active == True,
        Task.task_type == "daily"
    ).all()
    
    total = len(tasks)
    completions = db.query(TaskCompletion).filter(
        TaskCompletion.student_id == student_id,
        TaskCompletion.completed_date == today
    ).all()
    
    completed_task_ids = {c.task_id for c in completions}
    completed = len(completed_task_ids)
    
    # 今日获得积分
    points_today = db.query(func.sum(TaskCompletion.points_earned)).filter(
        TaskCompletion.student_id == student_id,
        TaskCompletion.completed_date == today
    ).scalar() or 0
    
    return {
        "total": total,
        "completed": completed,
        "percentage": int((completed / total * 100)) if total > 0 else 100,
        "points_today": points_today
    }


def get_completion_status(db: Session, student_id: str, task_id: str):
    """获取任务今日完成状态。"""
    today = date.today()
    completion = db.query(TaskCompletion).filter(
        TaskCompletion.student_id == student_id,
        TaskCompletion.task_id == task_id,
        TaskCompletion.completed_date == today
    ).first()
    return completion
