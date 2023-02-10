from pathlib import Path

import pydantic


class Settings(pydantic.BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720  # 30 days
    UPLOAD_STORAGE = Path("media")
    SUPER_ADMIN_ID: int = -1
    SUPER_ADMIN_EMAIL: pydantic.EmailStr = pydantic.EmailStr("admin@example.com")
    SUPER_ADMIN_USERNAME: str = "admin"
    SUPER_ADMIN_PASSWORD: str
    DB_URL: str = "sqlite+pysqlite:///lol.db"

    class Config:
        env_file = ".env"
