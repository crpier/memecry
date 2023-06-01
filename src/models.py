import datetime
import enum

from pydantic import EmailStr
from sqlmodel import (
    JSON,
    Column,
    Field,
    Relationship,
    SQLModel,
    UniqueConstraint,
    create_engine,
)


def get_engine(source: str = "sqlite+pysqlite:///lol.db"):
    return create_engine(source, echo=False)


class User(SQLModel, table=True):
    __tablename__: str = "users"  # type: ignore
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
    __tablename__: str = "posts"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    title: str
    # TODO: create special type for this
    source: str | None = Field(default=None)
    top: bool = Field(default=False)
    likes: int = Field(default=0)
    dislikes: int = Field(default=0)
    score: int = Field(default=0)
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(tz=datetime.UTC)
    )
    comment_count: int = Field(default=0)
    content: str = Field(default="")

    user_id: int = Field(foreign_key="users.id")
    # we always want the poster's row in the schema, so eagerly load it with JOIN
    user: User = Relationship(
        back_populates="posts", sa_relationship_kwargs={"lazy": "joined"}
    )
    comments: list["Comment"] = Relationship(back_populates="post")
    reactions: list["Reaction"] = Relationship(back_populates="post")

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
    __tablename__: str = "reactions"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(tz=datetime.UTC)
    )

    user_id: int = Field(foreign_key="users.id")
    user: User = Relationship(back_populates="reactions")

    post_id: int | None = Field(foreign_key="posts.id", default=None)
    post: Post = Relationship(back_populates="reactions")

    comment_id: int | None = Field(foreign_key="comments.id", default=None)
    comment: "Comment" = Relationship(back_populates="reactions")

    kind: ReactionKind

    __table_args__ = (
        UniqueConstraint("user_id", "post_id", "comment_id", name="unique_post_like"),
    )


class Comment(SQLModel, table=True):
    __tablename__: str = "comments"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    content: str | None = Field(default=None)
    # TODO: create special type for this too
    attachment_source: str | None = Field(default=None)
    likes: int = Field(default=0)
    dislikes: int = Field(default=0)
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(tz=datetime.UTC)
    )

    user_id: int = Field(foreign_key="users.id")
    user: User = Relationship(back_populates="comments")

    post_id: int = Field(foreign_key="posts.id")
    post: Post = Relationship(back_populates="comments")
    parent_id: int | None = Field(foreign_key="comments.id", default=None)

    reactions: list["Reaction"] = Relationship(back_populates="comment")
