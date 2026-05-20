from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from datetime import datetime, timedelta
from typing import List, Optional
from app.models.vocabulary import Character, ReviewLog
from app.schemas.vocabulary import CharacterCreate, ReviewSubmit
from app.services.ai import enrich_character

GROUP_SIZE = 4  # 每组检测字数


def get_character_by_text(db: Session, student_id: str, character: str) -> Optional[Character]:
    return db.query(Character).filter(
        Character.student_id == student_id,
        Character.character == character
    ).first()


def create_character(db: Session, student_id: str, data: CharacterCreate) -> Character:
    """录入单个生字，如有需要调用 AI 补全信息。"""
    # 检查是否已存在
    existing = get_character_by_text(db, student_id, data.character)
    if existing:
        return existing

    # 如果有拼音，直接录入；否则调用 AI 补全
    char_data = data.model_dump()
    if not char_data.get("pinyin"):
        enriched = enrich_character(data.character)
        char_data.update(enriched)

    db_char = Character(
        student_id=student_id,
        **{k: v for k, v in char_data.items() if v is not None}
    )
    db.add(db_char)
    db.commit()
    db.refresh(db_char)
    return db_char


def batch_create_characters(db: Session, student_id: str, characters: List[str]) -> List[Character]:
    """批量录入生字。"""
    results = []
    for char in characters:
        char = char.strip()
        if not char:
            continue
        existing = get_character_by_text(db, student_id, char)
        if existing:
            results.append(existing)
            continue

        # 调用 AI 补全
        enriched = enrich_character(char)
        db_char = Character(
            student_id=student_id,
            character=char,
            **{k: v for k, v in enriched.items() if v is not None}
        )
        db.add(db_char)
        db.commit()
        db.refresh(db_char)
        results.append(db_char)
    return results


def get_characters(db: Session, student_id: str, status: Optional[str] = None) -> List[Character]:
    """获取学生的生字列表。"""
    query = db.query(Character).filter(Character.student_id == student_id)
    if status:
        query = query.filter(Character.status == status)
    return query.order_by(Character.created_at.desc()).all()


def get_quiz_group(db: Session, student_id: str) -> dict:
    """
    获取一组待检测生字。
    优先级：
    1. 已到复习时间的字
    2. 最近新录入的字（status=new）
    3. 在学中的字（status=learning）
    """
    now = datetime.utcnow()

    # 1. 已到复习时间的字
    due_chars = db.query(Character).filter(
        Character.student_id == student_id,
        Character.next_review_at <= now
    ).order_by(Character.next_review_at).limit(GROUP_SIZE).all()

    chars = list(due_chars)
    need_more = GROUP_SIZE - len(chars)

    # 2. 新录入的字
    if need_more > 0:
        existing_ids = [c.id for c in chars]
        new_chars = db.query(Character).filter(
            Character.student_id == student_id,
            Character.status == "new",
            ~Character.id.in_(existing_ids) if existing_ids else True
        ).order_by(Character.created_at.desc()).limit(need_more).all()
        chars.extend(new_chars)
        need_more = GROUP_SIZE - len(chars)

    # 3. 在学中的字
    if need_more > 0:
        existing_ids = [c.id for c in chars]
        learning_chars = db.query(Character).filter(
            Character.student_id == student_id,
            Character.status == "learning",
            ~Character.id.in_(existing_ids) if existing_ids else True
        ).order_by(Character.last_review_at).limit(need_more).all()
        chars.extend(learning_chars)

    if not chars:
        return {"group_id": 0, "characters": [], "total": 0}

    # 分配组 ID
    max_group = db.query(func.max(Character.group_id)).filter(
        Character.student_id == student_id
    ).scalar() or 0
    group_id = max_group + 1

    for c in chars:
        c.group_id = group_id
        c.review_round = 0

    db.commit()

    return {
        "group_id": group_id,
        "characters": chars,
        "total": len(chars)
    }


def submit_review(db: Session, student_id: str, result: ReviewSubmit) -> Character:
    """提交单个字的检测结果。"""
    char = db.query(Character).filter(
        Character.id == result.character_id,
        Character.student_id == student_id
    ).first()

    if not char:
        return None

    # 记录复习日志
    log = ReviewLog(
        student_id=student_id,
        character_id=result.character_id,
        result=result.result,
        group_id=result.group_id,
        review_round=result.review_round
    )
    db.add(log)

    # 更新统计
    char.review_count += 1
    char.last_reviewed_at = datetime.utcnow()

    if result.result == "know":
        char.correct_count += 1
        char.status = "known"
        # 艾宾浩斯：正确则延后复习
        char.next_review_at = datetime.utcnow() + timedelta(days=1)
    elif result.result == "unknow":
        char.wrong_count += 1
        char.status = "learning"
        # 不认识：很快再复习
        char.next_review_at = datetime.utcnow() + timedelta(minutes=30)
    elif result.result == "study":
        # 再学一下：不更新统计，只记录
        pass

    db.commit()
    db.refresh(char)
    return char


def submit_reviews(db: Session, student_id: str, results: List[ReviewSubmit]) -> List[Character]:
    """批量提交检测结果。"""
    updated = []
    for r in results:
        char = submit_review(db, student_id, r)
        if char:
            updated.append(char)
    return updated


def generate_reading(db: Session, student_id: str, character_ids: Optional[List[str]] = None, theme: str = "日常") -> dict:
    """
    生成精读短文。
    使用 DeepSeek 生成包含指定生字的短文，并标注拼音。
    """
    from app.services.ai import generate_reading_passage

    if character_ids:
        chars = db.query(Character).filter(
            Character.id.in_(character_ids),
            Character.student_id == student_id
        ).all()
    else:
        # 默认取最近不认识的字
        chars = db.query(Character).filter(
            Character.student_id == student_id,
            Character.status.in_(["learning", "new"])
        ).order_by(Character.wrong_count.desc()).limit(10).all()

    if not chars:
        return {
            "title": "暂无生字",
            "content": [{"hz": "请", "py": "qǐng"}, {"hz": "先", "py": "xiān"}, {"hz": "录", "py": "lù"}, {"hz": "入", "py": "rù"}, {"hz": "生", "py": "shēng"}, {"hz": "字", "py": "zì"}],
            "summary": "还没有录入生字哦，快去 AI学 页面录几个吧！"
        }

    char_list = [{
        "character": c.character,
        "pinyin": c.pinyin,
        "words": c.words or [],
        "example": c.example
    } for c in chars]

    return generate_reading_passage(char_list, theme)
