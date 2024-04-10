from pathlib import Path

from relax.config import BaseConfig
from starlette.datastructures import CommaSeparatedStrings

# TODO: make sure that alembic can use this
# (i.e. we don't need unnecessary vars to be set)


class Config(BaseConfig):
    def __init__(self) -> None:
        super().__init__()
        # required vars
        self.SECRET_KEY = self.config("SECRET_KEY")

        # optional vars
        self.ALGORITHM = self.config("ALGORITHM", default="HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = self.config(
            "ACCESS_TOKEN_EXPIRE_MINUTES", cast=int, default=720
        )  # 30 days
        self.ALLOW_SIGNUPS = self.config("ALLOW_SIGNUPS", cast=bool, default=False)
        self.MEDIA_UPLOAD_STORAGE = self.config(
            "MEDIA_UPLOAD_STORAGE", cast=Path, default=Path("./media")
        )
        self.COMMENT_SUBDIR = self.config(
            "COMMENT_SUBDIR", cast=Path, default=Path("comments")
        )
        self.DB_FILE = self.config("DB_FILE", cast=Path, default=Path("dev.db"))
        self.DEFAULT_POSTS_LIMIT = self.config(
            "DEFAULT_POSTS_LIMIT", cast=int, default=5
        )
        # This should be in the db instead
        self.DEFAULT_TAGS = self.config(
            "DEFAULT_TAGS",
            cast=CommaSeparatedStrings,
            default=CommaSeparatedStrings("reaction,animals,postironic,meirl"),
        )
        self.RESTRICTED_TAGS = self.config(
            "RESTRICTED_TAGS",
            cast=CommaSeparatedStrings,
            default=CommaSeparatedStrings("postironic"),
        )
        self.POSTS_LIMIT = self.config("POSTS_LIMIT", cast=int, default=15)
