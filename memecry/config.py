from pathlib import Path
from typing import Annotated
from pydantic import Field, UrlConstraints
from pydantic_core import Url

from pydantic_settings import BaseSettings, SettingsConfigDict


SqliteDSN = Annotated[
    Url,
    UrlConstraints(
        host_required=True,
        allowed_schemes=[
            'sqlite+aiosqlite',
        ],
        default_host=''
    ),
]

class Config(BaseSettings):
    SECRET_KEY: str = Field(default=...)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720  # 30 days
    MEDIA_UPLOAD_STORAGE: Path = Path("./media")
    COMMENT_SUBDIR: Path = Path("comments")
    DB_URL: SqliteDSN = SqliteDSN("sqlite+aiosqlite:///dev.db")
    DEFAULT_POSTS_LIMIT: int = 5

    model_config= SettingsConfigDict(env_file=".env")
