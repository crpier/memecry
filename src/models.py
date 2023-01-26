import enum
import sqlalchemy
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    Enum,
    func,
    orm,
)


def get_engine(source: str | None = None) -> sqlalchemy.Engine:
    if source is None:
        return sqlalchemy.create_engine(
            "sqlite+pysqlite:////home/crpier/lol.db", echo=True
        )
    else:
        raise NotImplementedError("Not allowing persistend DBs yet.")


def get_sessionmaker(
    engine: sqlalchemy.Engine, opts: dict | None = None
) -> orm.sessionmaker[orm.Session]:
    if opts is None:
        return orm.sessionmaker(engine)
    raise NotImplementedError("Not allowing session options yet")


class Base(orm.DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, autoincrement=True, primary_key=True)
    email = Column(String)
    username = Column(String)
    pass_hash = Column(String)
    # TODO: custom validator or smth
    achievements = Column(JSON, default=[])
    verified = Column(Boolean, default=False)
    banned = Column(Boolean, default=False)
    admin = Column(Boolean, default=False)

    # posts = orm.relationship("Post", back_populates="user")
    # comments = orm.relationship("Comment", back_populates="user")


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, autoincrement=True, primary_key=True)
    title = Column(String)
    # TODO: create special type for this
    source = Column(String)
    top = Column(Boolean, default=False)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)

    user_id = Column(Integer, ForeignKey("users.id"))

    # comments = orm.relationship("Comment", back_populates="Post")
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


class ReactionKind(enum.Enum):
    Like = 0
    Dislike = 1


class Reaction(Base):
    __tablename__ = "reactions"

    id = Column(Integer, autoincrement=True, primary_key=True)
    created_at = Column(DateTime, default=func.current_timestamp())

    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True)
    comment_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    kind = Column(Integer, Enum(ReactionKind))

    __table_args__ = (
        UniqueConstraint(user_id, post_id, name="unique_post_like"),
        UniqueConstraint(user_id, comment_id, name="unique_comment_like"),
    )


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, autoincrement=True, primary_key=True)
    text = Column(String)
    # TODO: create special type for this too
    attachment_source = Column(String)
    likes = Column(Integer)
    dislikes = Column(Integer)

    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    parent_id = Column(Integer, ForeignKey("comments.id"))
