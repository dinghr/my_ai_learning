import httpx
from sqlalchemy.orm import Session
from app.models.student import Student
from app.config import get_settings

settings = get_settings()


async def code_to_openid(code: str) -> dict:
    """用微信临时 code 换取 openid。"""
    if not settings.wechat_appid or not settings.wechat_secret:
        # 开发模式：code 直接当 openid 用
        return {"openid": f"dev_{code[:20]}", "unionid": None, "session_key": "dev"}
    
    url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": settings.wechat_appid,
        "secret": settings.wechat_secret,
        "js_code": code,
        "grant_type": "authorization_code",
    }
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, timeout=10)
        data = resp.json()
    
    if "openid" not in data:
        error_msg = data.get("errmsg", "未知错误")
        raise ValueError(f"微信登录失败: {error_msg}")
    
    return {
        "openid": data["openid"],
        "unionid": data.get("unionid"),
        "session_key": data.get("session_key"),
    }


def get_or_create_student_by_openid(db: Session, openid: str) -> Student:
    """根据 openid 查找或创建学生。"""
    student = db.query(Student).filter(Student.openid == openid).first()
    if student:
        return student
    
    # 新用户：自动创建
    student = Student(
        name="小朋友",
        nickname="小棘",
        openid=openid,
        points_balance=50,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    
    # 创建初始积分记录
    from app.models.points import PointsRecord
    record = PointsRecord(
        student_id=student.id,
        points=50,
        balance=50,
        source_type="manual",
        description="新用户初始积分"
    )
    db.add(record)
    db.commit()
    
    return student
