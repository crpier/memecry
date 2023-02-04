from datetime import datetime
import enum
from functools import partial
from sqlmodel import (
    Field,
    SQLModel,
    Relationship,
    create_engine,
    Session,
    UniqueConstraint,
    Column,
    JSON,
)
from pydantic import EmailStr


def get_engine(source: str | None = None):
    if source is None:
        return create_engine("sqlite+pysqlite:////home/crpier/lol.db", echo=True)
    else:
        raise NotImplementedError("Not allowing persistend DBs yet.")


class User(SQLModel, table=True):
    __tablename__: str = "users"
    id: int | None = Field(default=None, primary_key=True)
    email: EmailStr
    username: str
    pass_hash: str
    # TODO: custom validator or smth
    achievements: list[str] = Field(sa_column=Column(JSON), default=[])
    verified: bool = Field(default=False)
    banned: bool = Field(default=False)
    admin: bool = Field(default=False)

    posts: list["Post"] = Relationship(back_populates="user")
    comments: list["Comment"] = Relationship(back_populates="user")
    reactions: list["Reaction"] = Relationship(back_populates="user")

    class Config:
        arbitrary_types_allowed = True


class Post(SQLModel, table=True):
    __tablename__: str = "posts"
    id: int | None = Field(default=None, primary_key=True)
    title: str
    # TODO: create special type for this
    source: str | None = Field(default=None)
    top: bool = Field(default=False)
    likes: int = Field(default=0)
    dislikes: int = Field(default=0)
    score: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    comment_count: int = Field(default=0)

    user_id: int = Field(foreign_key="users.id")
    user: User = Relationship(back_populates="posts")
    comments: list["Comment"] = Relationship(back_populates="post")

    def add_reaction(self, reaction: "ReactionKind"):
        match reaction:
            case ReactionKind.Like:
                self.likes += 1
            case ReactionKind.Dislike:
                self.dislikes += 1

    def remove_reaction(self, reaction: "ReactionKind"):
        match reaction:
            case ReactionKind.Like:
                self.likes -= 1
            case ReactionKind.Dislike:
                self.dislikes -= 1

    def add_other_reaction(self, reaction: "ReactionKind"):
        match reaction:
            case ReactionKind.Like:
                self.dislikes += 1
            case ReactionKind.Dislike:
                self.likes += 1

    def remove_other_reaction(self, reaction: "ReactionKind"):
        match reaction:
            case ReactionKind.Like:
                self.dislikes -= 1
            case ReactionKind.Dislike:
                self.likes -= 1


class ReactionKind(enum.StrEnum):
    Like = "Like"
    Dislike = "Dislike"


class Reaction(SQLModel, table=True):
    __tablename__: str = "reactions"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user_id: int = Field(foreign_key="users.id")
    user: User = Relationship(back_populates="reactions")

    post_id: int | None = Field(foreign_key="posts.id", default=None)
    comment_id: int | None = Field(foreign_key="posts.id", default=None)
    kind: ReactionKind

    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="unique_post_like"),
        UniqueConstraint("user_id", "comment_id", name="unique_comment_like"),
    )


class Comment(SQLModel, table=True):
    __tablename__: str = "comments"
    id: int | None = Field(default=None, primary_key=True)
    content: str
    # TODO: create special type for this too
    attachment_source: str | None = Field(default=None)
    likes: int = Field(default=0)
    dislikes: int = Field(default=0)

    user_id: int = Field(foreign_key="users.id")
    user: User = Relationship(back_populates="comments")

    post_id: int = Field(foreign_key="posts.id")
    post: Post = Relationship(back_populates="comments")
    parent_id: int | None = Field(foreign_key="comments.id", default=None)
