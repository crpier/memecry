from datetime import datetime

from fastapi.templating import Jinja2Templates
import babel.dates

from src.models import Post

templates = Jinja2Templates(directory="src/templates")


def render_top_posts(posts: list[Post], authenticated: bool = True):
    now = datetime.utcnow()
    for post in posts:
        post.created_at = babel.dates.format_timedelta(  # type: ignore
            post.created_at - now, add_direction=True, locale="en_US"
        )
    return templates.TemplateResponse(
        "top.html", {"request": {}, "posts": posts, "authenticated": authenticated}
    )


def render_post_upload():
    return templates.TemplateResponse("upload.html", {"request": {}})


def render_login():
    return templates.TemplateResponse("login.html", {"request": {}})
