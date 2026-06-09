from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.student import StudentCreate, StudentUpdate, StudentOut
from app.services.student import get_student, get_students, create_student, update_student

router = APIRouter(prefix="/api/students", tags=["students"])


@router.get("/current", response_model=StudentOut)
def get_current_student(request: Request, db: Session = Depends(get_db)):
    """获取当前学生（从请求头中识别）。"""
    from app.models.student import Student as StudentModel
    student_id = request.headers.get("X-Student-Id")
    if student_id:
        student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
        if student:
            return student
    # fallback: 返回第一个学生
    student = db.query(StudentModel).first()
    if not student:
        raise HTTPException(status_code=404, detail="还没有学生，请先创建")
    return student


@router.get("", response_model=list[StudentOut])
def list_students(db: Session = Depends(get_db)):
    return get_students(db)


@router.post("", response_model=StudentOut)
def create_new_student(student: StudentCreate, db: Session = Depends(get_db)):
    return create_student(db, student)


@router.get("/{student_id}", response_model=StudentOut)
def read_student(student_id: str, db: Session = Depends(get_db)):
    db_student = get_student(db, student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail="学生不存在")
    return db_student


@router.put("/{student_id}", response_model=StudentOut)
def update_existing_student(student_id: str, student: StudentUpdate, db: Session = Depends(get_db)):
    db_student = update_student(db, student_id, student)
    if not db_student:
        raise HTTPException(status_code=404, detail="学生不存在")
    return db_student
