from datetime import datetime
from typing import TypedDict

import babel.dates
import zoneinfo
from pydantic import BaseModel
from starlette.authentication import SimpleUser

from memecry import model


class UserCreate(BaseModel):
    password: str
    username: str


class UserRead(BaseModel, SimpleUser):
    id: int
    username: str
    pass_hash: str
    created_at: datetime
    verified: bool
    pfp_src: str

    class Config:
        from_attributes = True


class PostCreate(BaseModel):
    title: str
    user_id: int
    tags: str
    searchable_content: str


class PostRead(BaseModel):
    id: int
    created_at: datetime
    title: str
    source: str
    user_id: int
    tags: str
    searchable_content: str
    editable: bool = False

    class Config:
        from_attributes = True

    @staticmethod
    def from_model(
        post_in_db: model.Post,
        *,
        editable: bool = False,
    ) -> "PostRead":
        now = datetime.now(tz=zoneinfo.ZoneInfo("UTC"))
        post_in_db.created_at = post_in_db.created_at.replace(
            tzinfo=zoneinfo.ZoneInfo("UTC"),
        )

        post_dict = post_in_db.__dict__
        post_dict["created_since"] = babel.dates.format_timedelta(
            post_in_db.created_at - now,
            add_direction=True,
            locale="en_US",
        )
        post_dict["editable"] = editable
        return PostRead(**post_dict)


class QueryTags(TypedDict):
    included: list[str]
    excluded: list[str]


class Query:
    def __init__(self, raw_input: str) -> None:
        # Example query:
        # wawa >animals !reaction
        self._raw_input = raw_input
        parts = raw_input.split(" ")
        self._content_parts: list[str] = []
        self.tags: QueryTags = {"included": [], "excluded": []}
        for part in parts:
            match part[0]:
                case ">":
                    self.tags["included"].append(part[1:])
                case "!":
                    self.tags["excluded"].append(part[1:])
                case _:
                    self._content_parts.append(part)

    def __str__(self) -> str:
        return " ".join(self._content_parts)

    @property
    def content(self) -> str:
        return " ".join(self._content_parts)
