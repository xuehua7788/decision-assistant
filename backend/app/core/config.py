from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_title: str = "Decision Assistant API"
    api_version: str = "1.0.0"
    api_root_path: str = ""

    deepseek_api_key: Optional[str] = None

    chat_storage_dir: str = "chat_data"
    max_history_messages: int = 20

    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://*.vercel.app",  # 允许所有 Vercel 部署
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
