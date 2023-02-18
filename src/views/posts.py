from src import schema
from src.views.common import page_root, _class, hx_get, hx_trigger, hx_swap

from simple_html.nodes import (
    body,
    head,
    html,
    div,
    meta,
    title,
    link,
    script,
    nav,
    a,
    span,
    i,
    button,
    img,
    main,
    p,
    video,
)


def content_is_image(file_name: str) -> bool:
    name_ext = file_name.rsplit(".", 1)[1]
    return name_ext in ["png", "jpg", "jpeg"]


def single_post_partial(post: schema.Post):
    if content_is_image(post.source):
        post_content = img.attrs(src=post.source)
    else:
        post_content = video.attrs(_class("w-full"), src=post.source, controls="true")

    return div.attrs(
        _class("mb-8 border-2 border-gray-600 px-6 pb-4 text-center"),
        style="background:#181B1D;width:640px;",
        id=f"post-{post.id}",
    )(
        p.attrs(_class("my-4 text-xl font-bold"))(post.title),
        a.attrs(href=f"/post/{post.id}")(post_content),
        div.attrs(_class("flex flex-grow-0 flex-row items-center justify-start mt-4"))(
            a.attrs(_class("my-2 mr-2 font-semibold w-max"), href=".")(
                f"{post.score} good boi points"
            ),
            div.attrs(_class("flex-grow")),
            # TODO: actually use a differently named delta from created_at
            div.attrs(_class("font-semibold"))(
                post.created_at,  # type: ignore
                " by ",
                a.attrs(_class("font-bold text-green-300"), href=".")(
                    post.user.username
                ),
            ),
        ),
        div.attrs(_class("flex flex-grow-0 flex-row items-center justify-start mt-2"))(
            button.attrs(
                _class(
                    "mr-3 rounded-md border border-gray-600 px-2 py-2 hover:border-gray-900"
                )
            )(i.attrs(_class("fa fa-arrow-up fa-lg"))),
            button.attrs(
                _class(
                    "mr-3 rounded-md border border-gray-600 px-2 py-2 hover:border-gray-900"
                )
            )(i.attrs(_class("fa fa-arrow-down fa-lg"))),
            div.attrs(_class("flex-grow")),
            button.attrs(
                _class(
                    "flex flex-row rounded-md border border-gray-600 p-2 hover:border-gray-500"
                )
            )(
                i.attrs(_class("fa fa-comment fa-lg mt-1 mr-2")),
                div(f"{post.comment_count} comments"),
            ),
        ),
        div.attrs(id=f"post-comments-{post.id}"),
    )


def single_post(user: schema.User | None, post: schema.Post):
    return page_root(user=user, partial=single_post_partial(post))


def post_list(posts: list[schema.Post], user: schema.User | None, partial=False):
    post_partials = [single_post_partial(post=post) for post in posts]
    post_partials[-1] = div.attrs(
        hx_get("/?offset=2"), hx_trigger("revealed"), hx_swap("afterend")
    )(post_partials[-1])
    if not partial:
        return page_root(
            user=user,
            partial=div(*post_partials),
        )
    else:
        return div(*post_partials)
