import enum
from datetime import datetime

from pydantic import EmailStr, PrivateAttr
from sqlmodel import (
    JSON,
    Column,
    Field,
    Relationship,
    SQLModel,
    UniqueConstraint,
    create_engine,
)


def get_engine(source: str):
    return create_engine(source, echo=False)


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
    pfp_src: str | None = Field(default=None)

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
                self.score += 1
            case ReactionKind.Dislike:
                self.dislikes += 1
                self.score -= 1

    def remove_reaction(self, reaction: "ReactionKind"):
        match reaction:
            case ReactionKind.Like:
                self.likes -= 1
                self.score -= 1
            case ReactionKind.Dislike:
                self.dislikes -= 1
                self.score += 1

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


class ReactionKind(str, enum.Enum):
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
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user_id: int = Field(foreign_key="users.id")
    user: User = Relationship(back_populates="comments")

    post_id: int = Field(foreign_key="posts.id")
    post: Post = Relationship(back_populates="comments")
    parent_id: int | None = Field(foreign_key="comments.id", default=None)
