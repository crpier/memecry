from datetime import datetime
from typing import Callable

import babel.dates
import jinja2
from simple_html.nodes import Tag
from simple_html.render import render
from sqlmodel import Session, select
from starlette.responses import HTMLResponse

from src import comment_service, posting_service, schema
from src.models import Post, ReactionKind
from src.schema import User
from src.views import common
from src.views import posts as post_views
from src.views.common import hx_get, hx_swap, hx_trigger


def prepare_post_for_viewing(
    post: schema.Post, session: Callable[[], Session], user_id: int | None = None
):
    now = datetime.utcnow()
    post.created_at = babel.dates.format_timedelta(  # type: ignore
        post.created_at - now, add_direction=True, locale="en_US"
    )

    if user_id:
        reaction = posting_service.get_user_reaction_on_post(
            user_id=user_id, post_id=post.id, session=session
        )
        if reaction == ReactionKind.Like:
            post.liked = True
        elif reaction == ReactionKind.Dislike:
            post.disliked = True


def get_posts_html(
    offset,
    limit,
    session: Callable[[], Session],
    user: User | None,
):
    elements: list[Tag] = []
    posts = posting_service.get_newest_posts(session, offset=offset, limit=limit)
    for post in posts:
        prepare_post_for_viewing(
            post=post, session=session, user_id=user.id if user else None
        )
        posts_html = post_views.single_post_partial(post=post)
        elements.append(posts_html)
    try:
        if len(elements) == limit:
            elements[-1].attributes += (
                hx_get(f"/posts?offset={offset+limit}"),
                hx_trigger("revealed"),
                hx_swap("afterend"),
            )
    except IndexError:
        pass

    return elements


def render_search_results(
    query: str, session: Callable[[], Session], user: User | None = None
) -> list[Tag]:
    elements: list[Tag] = []
    posts = posting_service.search_through_posts(query=query, session=session)
    for post in posts:
        prepare_post_for_viewing(
            post=post, session=session, user_id=user.id if user else None
        )
        posts_html = post_views.single_post_partial(post=post)
        elements.append(posts_html)
    return elements


def render_post(
    post_id: int,
    session: Callable[[], Session],
    user: User | None = None,
    partial=True,
):
    s = session()
    with s.no_autoflush:
        res = s.exec(select(Post).where(Post.id == post_id)).one_or_none()
        post = schema.Post.from_orm(res)
        if not post:
            return jinja2.Environment().from_string("<div></div>")
        prepare_post_for_viewing(
            post=post, session=session, user_id=user.id if user else None
        )
        # TODO: logic about partials should be moved in main.py I think 🤔
        if partial:
            return HTMLResponse(render(post_views.single_post_partial(post=post)))
        else:
            return HTMLResponse(render(post_views.single_post(user=user, post=post)))


def render_post_upload():
    return HTMLResponse(render(common.post_upload_form()))


def render_login():
    return HTMLResponse(render(common.login_form()))


def render_signup():
    return HTMLResponse(render(common.signup_form()))


def render_new_comment_form(comment_id: int, post_id: int):
    post_url = f"/comment/{comment_id}/comment"
    return HTMLResponse(
        render(post_views.new_comment_form(post_url=post_url, post_id=post_id))
    )


def render_comments(
    post_id: int, session: Callable[[], Session], user: User | None = None
):
    comments_dict, ids_tree = comment_service.get_comment_tree(
        post_id=post_id, session=session
    )
    for comment in comments_dict.values():
        comment = comment_service.prepare_comment_for_viewing(
            session=session, comment=comment, user=user
        )
    return HTMLResponse(
        render(
            post_views.comment_tree(
                comments_dict=comments_dict,  # type: ignore
                ids_tree=ids_tree,
                post_id=post_id,
            )
        )
    )
