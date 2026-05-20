from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.wechat import code_to_openid, get_or_create_student_by_openid

router = APIRouter(prefix="/api/wechat", tags=["wechat"])


@router.post("/login")
async def wechat_login(data: dict, db: Session = Depends(get_db)):
    """
    微信小程序登录。
    前端通过 wx.login() 获取 code，传入后端换取 openid 并自动创建/登录用户。
    """
    code = data.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="缺少 code 参数")
    
    try:
        wx_data = await code_to_openid(code)
        openid = wx_data["openid"]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"微信接口调用失败: {str(e)}")
    
    # 查找或创建用户
    student = get_or_create_student_by_openid(db, openid)
    
    return {
        "student_id": student.id,
        "openid": openid,
        "name": student.name,
        "nickname": student.nickname,
        "points_balance": student.points_balance,
        "is_new": student.created_at == student.updated_at,  # 粗略判断是否新用户
    }


@router.get("/check")
def check_login(student_id: str, db: Session = Depends(get_db)):
    """检查用户登录状态。"""
    from app.services.student import get_student
    student = get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {
        "student_id": student.id,
        "name": student.name,
        "points_balance": student.points_balance,
    }
