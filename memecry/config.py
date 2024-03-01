from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


# TODO: use starlette config instead of pydantic
# TODO: make sure that alembic can use this
# (i.e. we don't need unnecessary vars to be set)
class Config(BaseSettings):
    TEMPLATES_DIR: str = Field(default=...)
    SECRET_KEY: str = Field(default=...)
    ENV: Literal["dev", "prod", "unit", "acceptance"] = "prod"
    ALGORITHM: str = "HS256"
    ALLOW_SIGNUPS: bool = False
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720  # 30 days
    MEDIA_UPLOAD_STORAGE: Path = Path("./media")
    COMMENT_SUBDIR: Path = Path("comments")
    # TODO: allow using a remote sqlite db
    DB_FILE: Path = Path("dev.db")
    DEFAULT_POSTS_LIMIT: int = 5
    # This should be in the db instead
    # TODO: constraint that tags are one word only
    # guess alphanumeric chars and hyphens are ok?
    # TODO: this can be converted into string only
    DEFAULT_TAGS: list[str] = Field(
        default=[
            "reaction",
            "animals",
            "postironic",
            "meirl",
        ],
        validate_default=False,
    )
    RESTRICTED_TAGS: list[str] = Field(
        default=[
            "postironic",
        ],
        validate_default=False,
    )
