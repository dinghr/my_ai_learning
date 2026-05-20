from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base, init_db

# 创建表
init_db()

app = FastAPI(
    title="AI助学小程序 API",
    description="亲子共学小程序后端服务",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
from app.routers.students import router as students_router
from app.routers.tasks import router as tasks_router
from app.routers.wishes import router as wishes_router, reward_router
from app.routers.points import router as points_router
from app.routers.ai_chat import router as ai_chat_router
from app.routers.wechat import router as wechat_router

app.include_router(students_router)
app.include_router(tasks_router)
app.include_router(wishes_router)
app.include_router(reward_router)
app.include_router(points_router)
app.include_router(ai_chat_router)
app.include_router(wechat_router)


@app.get("/")
async def root():
    return {"message": "AI助学小程序 API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}
