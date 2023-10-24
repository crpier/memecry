from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    SECRET_KEY: str = Field(default=...)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720  # 30 days
    MEDIA_UPLOAD_STORAGE: Path = Path("./media")
    COMMENT_SUBDIR: Path = Path("comments")
    # TODO: allow using a remote sqlite db
    DB_FILE: Path = Path("dev.db")
    DEFAULT_POSTS_LIMIT: int = 5
    SEARCH_TABLE: str = "posts_data"
    # This should be in the db instead
    DEFAULT_TAGS: list[str] = Field(
        default=[
            "reaction",
            "animals",
            "postironic",
            "meirl",
        ],
        validate_default=False,
    )
