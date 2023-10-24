import json
from pathlib import Path
from typing import Annotated, Any, Type, override

from pydantic import BeforeValidator, Field, UrlConstraints, validator
from pydantic.fields import FieldInfo
from pydantic_core import Url
from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

SqliteDSN = Annotated[
    Url,
    UrlConstraints(
        host_required=True,
        allowed_schemes=[
            "sqlite+aiosqlite",
        ],
        default_host="",
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
    SEARCH_TABLE: str = "posts_data"
    DEFAULT_TAGS: list[str] = Field(
        default=[
            "reaction",
            "animals",
            "postironic",
            "meirl",
        ],
        validate_default=False,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (MyCustomSource(settings_cls),)


# copied straight from the docs https://docs.pydantic.dev/latest/concepts/pydantic_settings/#parsing-environment-variable-values
# in order to allow writing in env vars: "DEFAULT_TAGS=tag1,tag2,tag3"
class MyCustomSource(EnvSettingsSource):
    def prepare_field_value(
        self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool
    ) -> Any:
        if field_name == "DEFAULT_TAGS":
            if value is None:
                return field.default
            return value.split(",")
        return value
