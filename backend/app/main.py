import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings, get_cors_origins
from app.database import engine, Base, init_db

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)

# 创建表
init_db()

settings = get_settings()
logger = logging.getLogger(__name__)
logger.info(f"[STARTUP] env={settings.env} | model={settings.deepseek_model} | api_key_set={bool(settings.deepseek_api_key and settings.deepseek_api_key != 'sk-demo')}")

app = FastAPI(
    title="AI助学小程序 API",
    description="亲子共学小程序后端服务",
    version="1.0.0"
)

# CORS - 生产环境只允许特定域名，开发/测试允许所有
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
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
from app.routers.vocabulary import router as vocabulary_router

app.include_router(students_router)
app.include_router(tasks_router)
app.include_router(wishes_router)
app.include_router(reward_router)
app.include_router(points_router)
app.include_router(ai_chat_router)
app.include_router(wechat_router)
app.include_router(vocabulary_router)


@app.get("/")
async def root():
    return {"message": "AI助学小程序 API", "version": "1.0.0", "env": settings.env}


@app.get("/health")
async def health_check():
    return {"status": "ok", "env": settings.env}
