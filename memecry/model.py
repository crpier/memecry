from __future__ import annotations

import datetime
from typing import List

from relax.app import StrEnum
from sqlalchemy import ForeignKey, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

    username: Mapped[str] = mapped_column(unique=True)
    pass_hash: Mapped[str]
    verified: Mapped[bool] = mapped_column(default=False)
    pfp_src: Mapped[str] = mapped_column(default="default.png")

    posts: Mapped[List[Post]] = relationship()
    comments: Mapped[List[Comment]] = relationship()
    reactions: Mapped[List[Reaction]] = relationship()


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

    title: Mapped[str]
    source: Mapped[str]
    tags: Mapped[str]
    searchable_content: Mapped[str] = mapped_column(default="")

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship("User", back_populates="posts", lazy="joined")
    comments: Mapped[Comment] = relationship(
        "Comment", back_populates="post", cascade="all, delete"
    )
    reactions: Mapped[list[Reaction]] = relationship(
        "Reaction", back_populates="post", cascade="all, delete"
    )


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

    content: Mapped[str]
    attachment_src: Mapped[str]

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    parent_id: Mapped[int] = mapped_column(ForeignKey("comments.id"))

    user: Mapped[User] = relationship("User", back_populates="comments")
    post: Mapped[Post] = relationship("Post", back_populates="comments")
    replies: Mapped[list[Comment]] = relationship(
        "Comment", back_populates="parent", cascade="all, delete"
    )
    parent: Mapped[Comment] = relationship(
        "Comment", back_populates="replies", remote_side=[id]
    )
    reactions: Mapped[list[Reaction]] = relationship(
        "Reaction", back_populates="comment", cascade="all, delete"
    )


class ReactionKind(StrEnum):
    Like = "Like"
    Dislike = "Dislike"


class Reaction(Base):
    __tablename__ = "reactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

    kind: Mapped[ReactionKind]

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    comment_id: Mapped[int] = mapped_column(ForeignKey("comments.id"))

    user: Mapped[User] = relationship("User", back_populates="reactions")
    post: Mapped[Post] = relationship("Post", back_populates="reactions")
    comment: Mapped[Comment] = relationship("Comment", back_populates="reactions")

    # TODO: add unique constraint on user_id and post_id or comment_id
