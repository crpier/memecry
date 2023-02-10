from datetime import datetime
from typing import Callable

import babel.dates
from fastapi.templating import Jinja2Templates
from jinja2 import Template
import jinja2
from sqlmodel import Session, col, select

from src import comment_service, posting_service
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


def render_posts(session: Callable[[], Session], top:bool, user: User | None, offset=0, limit=5):
    if top:
        posts = posting_service.get_top_posts(session, offset=offset, limit=limit)
    else:
        posts = posting_service.get_newest_posts(session, offset=offset, limit=limit)
    for post in posts:
        prepare_post_for_viewing(
            post=post, session=session, user_id=user.id if user else None
        )
    if offset==0:
        return templates.TemplateResponse(
            "top.html",
            {"request": {}, "posts": posts, "user": user, "page_number": 0},
        )
    else:
        return templates.TemplateResponse(
            "posts_partial.html",
            {"request": {}, "posts": posts, "user": user, "page_number": offset*limit},
        )



def render_newest_posts(session: Callable[[], Session], user: User | None):
    with session() as s:
        posts = posting_service.get_newest_posts(session)
        for post in posts:
            prepare_post_for_viewing(
                post=post, session=session, user_id=user.id if user else None
            )
        return templates.TemplateResponse(
            "top.html",
            {"request": {}, "posts": posts, "user": user},
        )


def render_post(
    post_id: int,
    session: Callable[[], Session],
    user: User | None = None,
    partial=True,
):
    s = session()
    with s.no_autoflush:
        post = s.exec(select(Post).where(Post.id == post_id)).one_or_none()
        if not post:
            return jinja2.Environment().from_string("<div></div>")
        prepare_post_for_viewing(
            post=post, session=session, user_id=user.id if user else None
        )
        template_name = "only_post.html" if partial else "post_page.html"
        return templates.TemplateResponse(
            template_name,
            {"request": {}, "post": post, "user": user},
        )


def render_post_upload():
    return templates.TemplateResponse("upload.html", {"request": {}})


def render_login():
    return templates.TemplateResponse("login.html", {"request": {}})


def render_signup():
    return templates.TemplateResponse("signup.html", {"request": {}})


def render_comment_partial():
    pass


def render_comment(post_id: int, session: Callable[[], Session]):
    comments_dict, ids_tree = comment_service.get_comment_tree(
        post_id=post_id, session=session
    )
    from pprint import pprint

    pprint(ids_tree)
    return templates.TemplateResponse(
        "comment_tree.html", {"request": {}, "ids_tree": ids_tree}
    )
