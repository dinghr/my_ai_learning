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

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
