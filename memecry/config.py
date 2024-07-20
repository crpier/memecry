from pathlib import Path
from typing import Annotated, Any

from pydantic import Field
from relax.config import BaseConfig


def comma_separated_list_validator(value: Any) -> list[str]:  # noqa: ANN401
    if not isinstance(value, str):
        msg = "Must be a comma separated string"
        raise TypeError(msg)
    return value.split(",")


CommaSeparatedStringList = Annotated[list[str], comma_separated_list_validator]


class Config(BaseConfig):
    SECRET_KEY: str = Field(default=...)

    # optional vars
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24 * 30)
    ALLOW_SIGNUPS: bool = Field(default=False)
    MEDIA_UPLOAD_STORAGE: Path = Field(default=Path("./media"))
    COMMENT_SUBDIR: Path = Field(default=Path("comments"))
    DB_FILE: Path = Field(default=Path("dev.db"))
    DEFAULT_POSTS_LIMIT: int = Field(default=5)

    RESTRICTED_TAGS: CommaSeparatedStringList = Field(default=["postironic"])
    POSTS_LIMIT: int = Field(default=15)

    # This should be in the db instead
    DEFAULT_TAGS: CommaSeparatedStringList = Field(
        default=["reaction", "animals", "postironic", "meirl"]
    )
