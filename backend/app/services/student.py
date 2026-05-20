from sqlalchemy.orm import Session
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate


def get_student(db: Session, student_id: str):
    return db.query(Student).filter(Student.id == student_id).first()


def get_students(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Student).offset(skip).limit(limit).all()


def create_student(db: Session, student: StudentCreate):
    db_student = Student(**student.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def update_student(db: Session, student_id: str, student: StudentUpdate):
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        return None
    update_data = student.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_student, key, value)
    db.commit()
    db.refresh(db_student)
    return db_student


def update_points(db: Session, student_id: str, points_delta: int):
    """Update student points balance."""
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        return None
    db_student.points_balance = max(0, db_student.points_balance + points_delta)
    db.commit()
    db.refresh(db_student)
    return db_student
