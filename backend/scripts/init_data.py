#!/usr/bin/env python3
"""
初始化Phase2测试数据：学生 + 默认每日任务 + 愿望
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.student import Student
from app.models.task import Task
from app.models.wish import Wish, Reward
from app.models.points import PointsRecord


def init():
    # 先创建表
    from app.database import init_db
    init_db()
    
    db: Session = SessionLocal()
    
    # 1. 检查是否已有学生
    student = db.query(Student).first()
    if not student:
        print("创建默认学生...")
        student = Student(
            id="demo-student",
            name="小明",
            nickname="小棘",
            age=8,
            gender="boy",
            grade="二年级",
            points_balance=50
        )
        db.add(student)
        db.commit()
        db.refresh(student)
    
    student_id = student.id
    print(f"学生ID: {student_id}")
    
    # 2. 创建默认每日任务
    existing_tasks = db.query(Task).filter(Task.student_id == student_id, Task.is_active == True).count()
    if existing_tasks == 0:
        print("创建默认每日任务...")
        default_tasks = [
            {"name": "运动打卡", "icon": "🏃", "category": "sport", "points": 10},
            {"name": "家务劳动", "icon": "🧹", "category": "labor", "points": 10},
            {"name": "每日练字", "icon": "✍️", "category": "writing", "points": 10},
            {"name": "课外阅读", "icon": "📚", "category": "reading", "points": 15},
        ]
        for i, t in enumerate(default_tasks):
            task = Task(
                student_id=student_id,
                name=t["name"],
                icon=t["icon"],
                task_type="daily",
                category=t["category"],
                points=t["points"],
                sort_order=i
            )
            db.add(task)
        db.commit()
    
    # 3. 创建长期目标示例
    long_term = db.query(Task).filter(Task.student_id == student_id, Task.task_type == "long_term").first()
    if not long_term:
        task = Task(
            student_id=student_id,
            name="读完《西游记》",
            icon="🐵",
            task_type="long_term",
            category="reading",
            points=50,
            target_value=120,
            current_value=0,
            unit="页",
            sort_order=100
        )
        db.add(task)
        db.commit()
    
    # 4. 创建默认愿望
    existing_wishes = db.query(Wish).filter(Wish.student_id == student_id).count()
    if existing_wishes == 0:
        print("创建默认愿望...")
        default_wishes = [
            {"name": "去恐龙博物馆", "icon": "🦕", "points_required": 200, "is_featured": True},
            {"name": "买新积木套装", "icon": "🧱", "points_required": 150},
            {"name": "周末露营", "icon": "⛺", "points_required": 300},
        ]
        for w in default_wishes:
            wish = Wish(
                student_id=student_id,
                name=w["name"],
                icon=w["icon"],
                points_required=w["points_required"],
                is_featured=w.get("is_featured", False)
            )
            db.add(wish)
        db.commit()
    
    # 5. 创建奖励商城示例
    existing_rewards = db.query(Reward).count()
    if existing_rewards == 0:
        print("创建奖励商城...")
        rewards = [
            {"name": "30分钟游戏时间", "icon": "🎮", "points_cost": 50},
            {"name": "选购一本新书", "icon": "📖", "points_cost": 80},
            {"name": "周末公园野餐", "icon": "🧺", "points_cost": 100},
            {"name": "一次家庭电影夜", "icon": "🎬", "points_cost": 120},
        ]
        for r in rewards:
            reward = Reward(**r)
            db.add(reward)
        db.commit()
    
    # 6. 创建积分记录
    existing_records = db.query(PointsRecord).filter(PointsRecord.student_id == student_id).count()
    if existing_records == 0:
        print("创建初始积分记录...")
        record = PointsRecord(
            student_id=student_id,
            points=50,
            balance=50,
            source_type="manual",
            description="初始积分"
        )
        db.add(record)
        db.commit()
    
    print("\n✅ Phase2 数据初始化完成！")
    print(f"   学生: {student.name} (积分: {student.points_balance})")
    print(f"   每日任务: {db.query(Task).filter(Task.student_id == student_id, Task.task_type == 'daily', Task.is_active == True).count()}")
    print(f"   长期目标: {db.query(Task).filter(Task.student_id == student_id, Task.task_type == 'long_term').count()}")
    print(f"   愿望: {db.query(Wish).filter(Wish.student_id == student_id).count()}")
    print(f"   奖励: {db.query(Reward).count()}")
    
    db.close()


if __name__ == "__main__":
    init()
