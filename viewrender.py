from datetime import datetime
from sqlmodel import select, Session, col
from typing import Callable

from fastapi.templating import Jinja2Templates
import babel.dates
from sqlmodel import Session
from src import posting_service

from src.models import Post, ReactionKind
from src.schema import User

templates = Jinja2Templates(directory="src/templates")


def prepare_post_for_viewing(
    post: Post, session: Callable[[], Session], user_id: int | None = None
):
    now = datetime.utcnow()
    post.created_at = babel.dates.format_timedelta(  # type: ignore
        post.created_at - now, add_direction=True, locale="en_US"
    )

    if post.id is None:
        raise ValueError("Why is there a post without id in the db?")
    if user_id:
        reaction = posting_service.get_user_reaction_on_post(
            user_id=user_id, post_id=post.id, session=session
        )
        if reaction == ReactionKind.Like:
            post._liked = True
        elif reaction == ReactionKind.Dislike:
            post._disliked = True


def render_top_posts(session: Callable[[], Session], user: User | None):
    with session() as s:
        posts = posting_service.get_top_posts(session)
        for post in posts:
            prepare_post_for_viewing(
                post=post, session=session, user_id=user.id if user else None
            )
        return templates.TemplateResponse(
            "top.html",
            {"request": {}, "posts": posts, "authenticated": True if user else None},
        )


def render_post(post_id: int, session: Callable[[], Session], user_id: int):
    s = session()
    with s.no_autoflush:
        post = s.exec(select(Post).where(Post.id == post_id)).one()
        prepare_post_for_viewing(post=post, session=session, user_id=user_id)
        return templates.TemplateResponse(
            "only_post.html", {"request": {}, "post": post}
        )


def render_post_upload():
    return templates.TemplateResponse("upload.html", {"request": {}})


def render_login():
    return templates.TemplateResponse("login.html", {"request": {}})
