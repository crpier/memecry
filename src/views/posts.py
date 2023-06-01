from simple_html.nodes import FlatGroup, Tag, li, ul, video
from simple_html.render import render

from src import schema
from src.views.common import (
    _class,
    a,
    button,
    div,
    form,
    hx_encoding,
    hx_get,
    hx_post,
    hx_put,
    hx_swap,
    hx_target,
    hx_trigger,
    i,
    img,
    input,
    p,
    page_root,
)


def content_is_image(file_name: str) -> bool:
    name_ext = file_name.rsplit(".", 1)[1]
    return name_ext in ["png", "jpg", "jpeg"]


def post_partial(post: schema.Post) -> Tag:
    if content_is_image(post.source):
        post_content = img.attrs(src=post.source)
    else:
        post_content = video.attrs(_class("w-full"), src=post.source, controls="true")

    return div.attrs(
        _class(
            "flex flex-col items-center mb-8 px-6 pb-4 "
            "border-2 border-gray-600 text-center"
        ),
        style="background:#181B1D;width:520px;",
        id=f"post-{post.id}",
    )(
        p.attrs(_class("my-4 text-xl font-bold"))(post.title),
        a.attrs(href=f"/post/{post.id}")(post_content),
        div.attrs(
            _class(
                "flex flex-grow-0 flex-row items-center justify-start " "mt-4 w-full"
            )
        )(
            a.attrs(_class("my-2 mr-2 font-semibold w-max"), href=".")(
                f"{post.score} good boi points"
            ),
            div.attrs(_class("flex-grow")),
            # TODO: actually use a differently named delta from created_at
            div.attrs(_class("font-semibold"))(
                post.created_since,
                " by ",
                a.attrs(_class("font-bold text-green-300"), href=".")(
                    post.user.username
                ),
            ),
        ),
        div.attrs(
            _class("flex flex-grow-0 flex-row items-start justify-start mt-2 w-full")
        )(
            button.attrs(
                _class(
                    "mr-3 px-2 py-2 rounded-md border border-gray-600 "
                    "hover:border-gray-900 " + ("bg-yellow-800" if post.liked else "")
                ),
                hx_put(f"/post/{post.id}/like"),
                hx_target(f"#post-{post.id}"),
                hx_swap("outerHTML"),
            )(i.attrs(_class("fa fa-arrow-up fa-lg"))),
            button.attrs(
                _class(
                    "mr-3 px-2 py-2 rounded-md border border-gray-600 "
                    "hover:border-gray-900 " + ("bg-blue-900" if post.disliked else "")
                ),
                hx_put(f"/post/{post.id}/dislike"),
                hx_target(f"#post-{post.id}"),
                hx_swap("outerHTML"),
            )(i.attrs(_class("fa fa-arrow-down fa-lg"))),
            div.attrs(_class("flex-grow")),
            button.attrs(
                _class(
                    "flex flex-row p-2 rounded-md border border-gray-600"
                    "hover:border-gray-500"
                ),
                hx_get(f"/post/{post.id}/comments"),
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
    return page_root(user=user, child=post_partial(post))


def new_comment_form_partial(post_url: str, post_id: int) -> Tag:
    return form.attrs(
        _class("mb-2 pb-2"),
        hx_encoding("multipart/form-data"),
        hx_post(post_url),
        hx_target(f"#post-{post_id}-comments"),
        hx_swap("outerHTML"),
        id="comment-upload-form",
    )(
        input.attrs(
            _class("w-full rounded border p-1 mb-2 text-black"),
            type="text",
            name="content",
            placeholder="To be fair, you have to have a very high IQ to understand "
            "Rick and Morty. The humour is extremely subtle",
        ),
        input.attrs(type="file", name="file"),
        button.attrs(
            _class(
                "ml-4 px-4 py-1 rounded border-white bg-blue-500 text-sm font-semibold "
                "hover:border-transparent hover:bg-white hover:text-teal-500"
            ),
            type="submit",
        )("Submit"),
    )


def single_comment(comment: schema.Comment, child: Tag | None = None) -> Tag:
    return li.attrs(_class("flex flex-col text-sm"), id=f"single-comment-{comment.id}")(
        div.attrs(_class("flex flex-row mb-4"))(
            img.attrs(
                _class("mt-1"),
                style="display:block;max-width:45px;max-height:45px;width:auto;height:auto;",
                src=comment.user.pfp_src
                or "https://avatars.githubusercontent.com/u/31815875?v=4",
                alt="user profile picture",
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
                img.attrs(
                    _class("mt-1 w-9/12"),
                    src=comment.attachment_source,
                    # TODO: get the alt from the database
                    alt="funny image",
                )
                if comment.attachment_source
                else None,
                div.attrs(_class("text-left"))(comment.content),
                div.attrs(_class("flex flex-row"))(
                    button.attrs(
                        _class(
                            "rounded px-1 " + ("bg-yellow-800" if comment.liked else "")
                        ),
                        hx_put(f"/comment/{comment.id}/like"),
                        hx_target(f"#post-{comment.post_id}-comments"),
                        hx_swap("outerHTML"),
                    )(i.attrs(_class("fa fa-arrow-up"))),
                    button.attrs(
                        _class(
                            "mr-4 rounded px-1 "
                            + ("bg-blue-900" if comment.disliked else "")
                        ),
                        hx_put(f"/comment/{comment.id}/dislike"),
                        hx_target(f"#post-{comment.post_id}-comments"),
                        hx_swap("outerHTML"),
                    )(i.attrs(_class("fa fa-arrow-down"))),
                    button.attrs(
                        _class("text-blue-500 font-bold"),
                        hx_get(f"/comment/{comment.id}/{comment.post_id}/form"),
                        hx_target(f"#single-comment-{comment.id}"),
                        hx_swap("beforeend"),
                    )("Reply"),
                ),
            ),
        ),
        child,
    )


def new_comment_form_view(post_url: str, post_id: int) -> str:
    return render(new_comment_form_partial(post_url=post_url, post_id=post_id))


def one_comment_tree(
    root_comment: schema.Comment, comments: list[schema.Comment]
) -> Tag:
    comment_elements: list[Tag] = []
    for comment in filter(lambda c: c.parent_id == root_comment.id, comments):
        if any(c.parent_id == comment.id for c in comments):
            # comment has children
            new_comment = single_comment(
                comment, child=one_comment_tree(root_comment=comment, comments=comments)
            )
        else:
            new_comment = single_comment(comment)

        comment_elements.append(new_comment)

    return single_comment(
        root_comment,
        child=ul.attrs(_class("ml-16"))(*comment_elements),
    )


def comment_tree_view(comments: list[schema.Comment], post_id: int) -> str:
    comment_trees: list[Tag] = []
    for top_comment in filter(lambda c: c.parent_id is None, comments):
        comment_trees.append(
            one_comment_tree(root_comment=top_comment, comments=comments)
        )
    return render(
        div.attrs(
            _class(
                "mt-4 pt-4 flex flex-col justify-start items-start "
                "border-gray-600 items-stretch"
            ),
            id=(f"post-{post_id}-comments"),
        )(
            new_comment_form_partial(
                post_url=f"/post/{post_id}/comment", post_id=post_id
            ),
            ul(*comment_trees),
        )
    )


def post_view(
    post: schema.Post, user: schema.User | None = None, partial_html: bool = False
) -> str:
    post_html = post_partial(post)
    if partial_html:
        return render(post_html)
    else:
        return render(page_root(child=post_html, user=user))


def posts_view(
    posts: list[schema.Post],
    user: schema.User | None = None,
    partial_html: bool = False,
    scroll_continue_url: str | None = None,
) -> str:
    elements = [post_partial(post) for post in posts]
    if scroll_continue_url:
        elements[-1].attributes += (
            hx_get(scroll_continue_url),
            hx_trigger("revealed"),
            hx_swap("afterend"),
        )
    if partial_html:
        return render(FlatGroup(*elements))
    else:
        return render(page_root(child=FlatGroup(*elements), user=user))
