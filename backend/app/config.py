import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # 数据库
    database_url: str = "sqlite:///./ai_learning.db"

    # JWT
    secret_key: str = "change-this-secret-key"
    algorithm: str = "HS256"
    access_token_expire_days: int = 7

    # DeepSeek
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-chat"

    # 微信
    wechat_appid: str = ""
    wechat_secret: str = ""

    # 阿里云
    aliyun_access_key_id: str = ""
    aliyun_access_key_secret: str = ""

    # 环境
    env: str = "development"

    # CORS 允许域名（生产环境使用）
    cors_origins: str = "*"

    class Config:
        # 根据 ENV 环境变量加载对应的 .env 文件
        # 优先级：ENV 变量 > 默认 .env
        env_file = f".env.{os.getenv('ENV', 'development')}"
        # 如果环境特定的文件不存在，回退到 .env
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def get_cors_origins() -> list[str]:
    """获取 CORS 允许域名列表。"""
    settings = get_settings()
    if settings.cors_origins == "*":
        return ["*"]
    return [origin.strip() for origin in settings.cors_origins.split(",")]
