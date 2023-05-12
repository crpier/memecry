from pathlib import Path

import pydantic


class Settings(pydantic.BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720  # 30 days
    # TODO: check this path is absolute (or mb convert it?)
    MEDIA_UPLOAD_STORAGE = Path("./media")
    SUPER_ADMIN_ID: int = -1
    SUPER_ADMIN_EMAIL: pydantic.EmailStr = pydantic.EmailStr("admin@example.com")
    SUPER_ADMIN_USERNAME: str = "cristi"
    SUPER_ADMIN_PASSWORD: str
    DB_URL: str = "sqlite+pysqlite:///lol.db"
    DEFAULT_POSTS_PER_PAGE: int = 5

    class Config:
        env_file = ".env"
