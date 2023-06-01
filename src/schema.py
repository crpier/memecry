from datetime import datetime
from pathlib import Path

import babel.dates
import pydantic

from src import models

### User

# Shared properties
class UserBase(pydantic.BaseModel):
    username: str
    email: str | None = None
    admin: bool | None = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: str
    admin: bool = False
    verified: bool = False
    password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: str | None = None
    email: str | None = None


class UserInDBBase(UserBase):
    id: int
    achievements: dict[str, str]
    verified: bool
    banned: bool
    admin: bool
    pfp_src: str | None = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str


### Login
class Token(pydantic.BaseModel):
    access_token: str
    token_type: str


class TokenData(pydantic.BaseModel):
    username: str


### Post
# Shared properties
class PostBase(pydantic.BaseModel):
    title: str


# Properties to receive via API on creation
class PostCreate(PostBase):
    user_id: int
    top: bool = False


# Properties to receive via API on update
class PostUpdate(PostBase):
    pass


class PostInDBBase(PostBase):
    id: int
    user_id: int
    source: Path
    top: bool
    likes: int
    dislikes: int
    user: User
    liked: bool | None = None
    disliked: bool | None = None
    score: int
    comment_count: int

    @pydantic.validator("source")
    def source_must_be_absolute(cls, v: Path):
        if not v.is_absolute():
            raise ValueError(
                "source must be an absolute path (it is used as url to the file)"
            )
        return v

    class Config:
        orm_mode = True


# Additional properites to return via API
class Post(PostInDBBase):
    created_since: str

    @staticmethod
    def from_model(
        post_in_db: models.Post, reaction: models.ReactionKind | None = None
    ) -> "Post":
        now = datetime.utcnow()

        post_dict = post_in_db.__dict__
        post_dict["created_since"] = babel.dates.format_timedelta(
            post_in_db.created_at - now, add_direction=True, locale="en_US"
        )
        new_post = Post(**post_dict)
        if reaction:
            if reaction == models.ReactionKind.Like:
                new_post.liked = True
            elif reaction == models.ReactionKind.Dislike:
                new_post.disliked = True

        return new_post


class PostInDB(PostInDBBase):
    created_at: datetime


### Comment
# Shared properties
class CommentBase(pydantic.BaseModel):
    content: str | None


# Properties to receive via API on creation
class CommentCreate(CommentBase):
    parent_id: int | None = None
    post_id: int | None = None
    user_id: int


# Properties to receive via API on update
class CommentUpdate(CommentBase):
    pass


class CommentInDBBase(CommentBase):
    id: int
    attachment_source: Path | None = None
    parent_id: int | None = None
    post_id: int
    user_id: int
    dislikes: int
    likes: int

    @pydantic.validator("attachment_source")
    def attachment_source_must_be_absolute(cls, v: Path):
        if v is not None and not v.is_absolute():
            raise ValueError(
                "Attachment_source must be an absolute "
                "path (it is used as url to the file)"
            )
        return v

    class Config:
        orm_mode = True


# Additional properites to return via API
class Comment(CommentInDBBase):
    liked: bool | None = None
    disliked: bool | None = None
    created_at: str | datetime
    user: User

    @staticmethod
    def from_model(
        comment_in_db: models.Comment, reaction: models.ReactionKind | None = None
    ) -> "Comment":
        now = datetime.utcnow()

        comment_dict = comment_in_db.__dict__
        comment_dict["created_at"] = babel.dates.format_timedelta(
            comment_in_db.created_at - now, add_direction=True, locale="en_US"
        )
        new_comment = Comment(**comment_dict)
        if reaction:
            if reaction == models.ReactionKind.Like:
                new_comment.liked = True
            elif reaction == models.ReactionKind.Dislike:
                new_comment.disliked = True

        return new_comment


class CommentInDB(CommentInDBBase):
    pass


### Reaction
# Shared properties
class ReactionBase(pydantic.BaseModel):
    user_id: int
    post_id: int
    comment_id: int
    kind: str


# Properties to receive via API on creation
class ReactionCreate(ReactionBase):
    pass


# Properties to receive via API on update
class ReactionUpdate(ReactionBase):
    pass


class ReactionInDBBase(ReactionBase):
    id: int
    created_at: str
    user: User
    post: Post | None
    comment: Comment | None

    class Config:
        orm_mode = True


# Additional properites to return via API
class Reaction(ReactionInDBBase):
    pass


class ReactionInDB(ReactionInDBBase):
    pass
