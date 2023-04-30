from simple_html.nodes import Tag
from src import models, schema
from src.views.common import (
    page_root,
    _class,
    hx_get,
    hx_trigger,
    hx_swap,
    hx_target,
    hx_post,
    hx_encoding,
    input,
    div,
    a,
    i,
    button,
    img,
    p,
    video,
    form,
    li,
    ul,
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
                    "mr-3 px-2 py-2 rounded-md border border-gray-600"
                    "hover:border-gray-900"
                )
            )(i.attrs(_class("fa fa-arrow-up fa-lg"))),
            button.attrs(
                _class(
                    "mr-3 px-2 py-2 rounded-md border border-gray-600"
                    "hover:border-gray-900"
                )
            )(i.attrs(_class("fa fa-arrow-down fa-lg"))),
            div.attrs(_class("flex-grow")),
            button.attrs(
                _class(
                    "flex flex-row p-2 rounded-md border border-gray-600"
                    "hover:border-gray-500"
                ),
                hx_get(f"post/{post.id}/comments"),
                hx_target(f"#post-comments-{post.id}"),
            )(
                i.attrs(
                    _class("fa fa-comment fa-lg mt-1 mr-2"),
                ),
                div(f"{post.comment_count} comments"),
            ),
        ),
        div.attrs(id=f"post-comments-{post.id}"),
    )


def single_post(user: schema.User | None, post: schema.Post):
    return page_root(user=user, partial=single_post_partial(post))


def post_list(posts: list[schema.Post], user: schema.User | None, partial=False):
    post_partials = [single_post_partial(post=post) for post in posts]
    try:
        post_partials[-1] = div.attrs(
            hx_get("/?offset=2"), hx_trigger("revealed"), hx_swap("afterend")
        )(post_partials[-1])
    except IndexError:
        post_partials = []
    if not partial:
        return page_root(
            user=user,
            partial=div(*post_partials),
        )
    else:
        return div(*post_partials)


def new_comment_form(post_url: str, post_id: int):
    return form.attrs(
        _class("mb-2 pb-2"),
        hx_encoding("multipart/form-data"),
        hx_post(post_url),
        hx_target(f"#post-{post_id}-comments"),
        hx_swap("replace"),
        id="comment-upload-form",
    )(
        input.attrs(
            _class("w-full rounded border p-1 mb-2 text-black"),
            type="text",
            name="content",
            placeholder="write comment pls",
        ),
        input.attrs(type="file", name="file"),
        button.attrs(
            _class(
                "ml-4 px-4 py-1 rounded border-white bg-blue-500 text-sm font-semibold"
                "hover:border-transparent hover:bg-white hover:text-teal-500"
            ),
            type="submit",
        )("Submit"),
    )


# TODO: use comment from schema instead
def single_comment(comment: models.Comment):
    return li.attrs(_class("flex flex-col text-sm"))(
        div.attrs(_class("flex flex-row mb-4"))(
            img.attrs(
                _class("mt-1"),
                src=comment.user.pfp_src
                or "https://avatars.githubusercontent.com/u/31815875?v=4",
                alt="funny meme",
                width="45px",
                height="45px",
            ),
            div.attrs(_class("flex flex-col ml-2"))(
                div.attrs(_class("flex flex-row"))(
                    a.attrs(_class("text-blue-500 mr-2 font-bold"), href=".")(
                        comment.user.username
                    ),
                    div.attrs(_class("text-sm text-gray-400 mr-1"))(
                        f"{comment.likes} Ws"
                    ),
                    div.attrs(_class("text-sm text-gray-400 mr-1"))("-"),
                    div.attrs(_class("text-sm text-gray-400 mr-1"))(
                        f"{comment.dislikes} Ls"
                    ),
                    div.attrs(_class("text-sm text-gray-400 mr-1"))("-"),
                    div.attrs(_class("text-sm text-gray-400 mr-1"))(
                        # TODO: remove this str after moving to schema
                        str(comment.created_at)
                    ),
                ),
                div.attrs(_class("text-left"))(comment.content),
                div.attrs(_class("flex flex-row"))(
                    button.attrs(_class("mr-2"))(i.attrs(_class("fa fa-arrow-up"))),
                    button.attrs(_class("mr-4"))(i.attrs(_class("fa fa-arrow-down"))),
                    button.attrs(_class("text-blue-500 font-bold"))("Reply"),
                ),
            ),
        )
    )


def build_comment_list(
    comments_dict: dict[int, models.Comment], ids_tree: dict, post_id: int, top=False
) -> Tag:
    comments: list[Tag] = []
    for comment_id, children in ids_tree.items():
        comments.append(single_comment(comments_dict[comment_id]))
        if children:
            comments.append(build_comment_list(comments_dict, children, post_id))

    return ul.attrs(_class("ml-16" if not top else ""))(*comments)


def comment_tree(
    comments_dict: dict[int, models.Comment], ids_tree: dict, post_id: int
):
    comments = build_comment_list(comments_dict, ids_tree, post_id, top=True)
    return div.attrs(
        _class(
            "mt-4 pt-4 flex flex-col justify-start items-start"
            "border-gray-600 items-stretch"
        ),
        id=(f"post-{post_id}-comments"),
    )(new_comment_form(post_url=f"/post/{post_id}/comment", post_id=post_id), comments)
