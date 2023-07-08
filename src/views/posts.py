from pathlib import Path
from typing import Any

from simple_html.nodes import FlatGroup, Tag, li, ul, video
from simple_html.render import render

from src.views import posts_yahgl
from src import schema
from src.views.common import (
    _class,
    a,
    button,
    div,
    form,
    hx_delete,
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
    textarea,
)


def content_is_image(file_name: Path) -> bool:
    return file_name.suffix in [".png", ".jpg", ".jpeg"]


def post_partial(post: schema.Post, editor: bool = False, old: bool = False) -> Tag:
    if old:
        if content_is_image(post.source):
            post_content = img.attrs(_class("w-full"), src=str(post.source))
        else:
            post_content = video.attrs(
                _class("w-full"), src=str(post.source), controls="true"
            )
        if post.editable:
            edit_button = button.attrs(
                _class(
                    "mr-8 mt-4 px-3 py-3 flex flex-row p-2 rounded-md " "lg:mt-2 lg:mr-2"
                ),
                hx_get(f"/post/{post.id}/edit"),
                hx_target(f"#post-{post.id}"),
                hx_swap("outerHTML"),
            )(i.attrs(_class("fa fa-bars fa-lg")))
        else:
            edit_button = None
        if editor:
            title_bar = form.attrs(
                _class("w-full text-4xl lg:text-lg"),
                hx_encoding("application/x-www-form-urlencoded"),
                hx_post(f"/post/{post.id}/edit"),
                hx_target(f"#post-{post.id}"),
                hx_swap("outerHTML"),
                id=f"post-{post.id}-edit-form",
            )(
                textarea.attrs(
                    _class(
                        "mb-4 mt-2 px-2 py-1 bg-black text-center w-full text-5xl "
                        "lg:text-xl"
                    ),
                    type="text",
                    name="title",
                    rows=str(len(post.title) // 40 + 1),
                )(post.title)
            )
            cancel_button = button.attrs(
                _class(
                    "px-3 ml-auto mt-2 rounded-md border border-gray-600 font-bold "
                    "hover:border-gray-700 hover:bg-gray-700"
                ),
                hx_get(f"/post/{post.id}?partial_html=true"),
                hx_target(f"#post-{post.id}"),
                hx_swap("outerHTML"),
            )("X")
            edit_button = button.attrs(
                _class(
                    "font-bold mr-2 mt-4 px-3 py-2 flex flex-row p-2 rounded-md "
                    "border-gray-600 hover:border-gray-500 hover:bg-green-700 "
                    "lg:mt-2"
                ),
                type="submit",
                form=f"post-{post.id}-edit-form",
            )("Save")
            delete_button = button.attrs(
                _class(
                    "font-bold mr-2 mt-4 px-3 py-2 flex flex-row p-2 rounded-md "
                    "bg-red-700 border-gray-600 hover:border-red-600 hover:bg-red-600 "
                    "lg:mt-2"
                ),
                hx_delete(f"/post/{post.id}"),
            )("Delete")
        else:
            title_bar = p.attrs(_class("my-4 text-5xl font-bold " "lg:text-xl"))(post.title)
            cancel_button = None
            delete_button = None

        return div.attrs(
            _class(
                "flex flex-col items-center mb-10 pb-4 text-center w-full "
                "lg:px-6 lg:border"
            ),
            id=f"post-{post.id}",
        )(
            cancel_button,
            title_bar,
            a.attrs(_class("w-full"), href=f"/post/{post.id}")(post_content),
            div.attrs(
                _class(
                    "flex flex-grow-0 flex-row items-center justify-start ml-8 "
                    "mt-4 w-full lg:ml-0 lg:mt-0"
                )
            )(
                a.attrs(
                    _class(
                        "my-2 mr-2 font-semibold w-max text-3xl " "lg:text-base lg:mr-0"
                    ),
                    href=".",
                )(f"{post.score} good boi points"),
                div.attrs(_class("flex-grow")),
                div.attrs(_class("font-semibold mr-8 " "lg:mr-0 lg:text-base"))(
                    post.created_since,
                    " by ",
                    a.attrs(_class("font-bold text-green-300"), href=".")(
                        post.user.username
                    ),
                ),
            ),
            div.attrs(
                _class(
                    "flex flex-grow-0 flex-row items-start justify-start mt-2 ml-8 w-full "
                    "lg:ml-0"
                )
            )(
                button.attrs(
                    _class(
                        "mr-3 p-2 rounded-xl w-20 h-20 "
                        "lg:w-12 lg:h-12 " + (" bg-yellow-800" if post.liked else "")
                    ),
                    hx_put(f"/post/{post.id}/like"),
                    hx_target(f"#post-{post.id}"),
                    hx_swap("outerHTML"),
                )(i.attrs(_class("fa fa-arrow-up fa-lg"))),
                button.attrs(
                    _class(
                        "mr-3 p-2 rounded-xl w-20 h-20 "
                        "lg:w-12 lg:h-12 " + (" bg-blue-900" if post.disliked else "")
                    ),
                    hx_put(f"/post/{post.id}/dislike"),
                    hx_target(f"#post-{post.id}"),
                    hx_swap("outerHTML"),
                )(i.attrs(_class("fa fa-arrow-down fa-lg"))),
                div.attrs(_class("flex-grow")),
                delete_button,
                edit_button,
                button.attrs(
                    _class(
                        "flex flex-row p-2 mr-8 rounded-md items-center justify-center "
                        "mt-4 lg:mt-2 lg:mr-0 "
                        "hover:border-gray-500"
                    ),
                    hx_get(f"/post/{post.id}/comments"),
                    hx_target(f"#post-comments-{post.id}"),
                )(
                    i.attrs(
                        _class("fa fa-comment mr-4"),
                    ),
                    p.attrs(
                        _class("text-4xl " "lg:text-base"),
                    )(f"{post.comment_count} comments"),
                ),
            ),
            div.attrs(id=f"post-comments-{post.id}"),
        )
    else:
        return posts_yahgl.post_view()


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
            _class("w-full rounded border p-1 mb-2 text-black text-3xl lg:text-base "),
            type="text",
            name="content",
            placeholder="To be fair, you have to have a very high IQ to understand "
            "Rick and Morty. The humour is extremely subtle",
        ),
        input.attrs(type="file", name="file"),
        button.attrs(
            _class(
                "ml-4 mt-4 px-4 py-2 rounded bg-blue-500 text-3xl font-semibold "
                "hover:bg-white hover:text-teal-500 lg:mt-0 lg:text-sm "
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
            div.attrs(_class("flex flex-col ml-2 lg:max-w-xs"))(
                div.attrs(_class("flex flex-row"))(
                    a.attrs(
                        _class("text-blue-500 mr-2 font-bold text-3xl lg:text-base"),
                        href=".",
                    )(comment.user.username),
                    div.attrs(_class("text-2xl lg:text-sm text-gray-400 mr-1"))(
                        f"{comment.likes} Ws"
                    ),
                    div.attrs(_class("text-2xl lg:text-sm text-gray-400 mr-1"))("-"),
                    div.attrs(_class("text-2xl lg:text-sm text-gray-400 mr-1"))(
                        f"{comment.dislikes} Ls"
                    ),
                    div.attrs(_class("text-2xl lg:text-sm text-gray-400 mr-1"))("-"),
                    div.attrs(_class("text-2xl lg:text-sm text-gray-400 mr-1"))(
                        str(comment.created_at)
                    ),
                ),
                img.attrs(
                    _class("mt-1"),
                    src=str(comment.attachment_source),
                    # TODO: get the alt from the database
                    alt="funny image",
                )
                if comment.attachment_source
                else None,
                div.attrs(_class("text-left text-4xl lg:text-base"))(comment.content),
                div.attrs(_class("flex flex-row mt-4"))(
                    button.attrs(
                        _class(
                            "mr-3 p-2 rounded-xl w-20 h-20 "
                            "lg:w-12 lg:h-12 "
                            + (" bg-yellow-800" if comment.liked else "")
                        ),
                        hx_put(f"/comment/{comment.id}/like"),
                        hx_target(f"#post-{comment.post_id}-comments"),
                        hx_swap("outerHTML"),
                    )(i.attrs(_class("fa fa-arrow-up fa-2x"))),
                    button.attrs(
                        _class(
                            "mr-3 p-2 rounded-xl w-20 h-20 "
                            "lg:w-12 lg:h-12 "
                            + (" bg-blue-900" if comment.disliked else "")
                        ),
                        hx_put(f"/comment/{comment.id}/dislike"),
                        hx_target(f"#post-{comment.post_id}-comments"),
                        hx_swap("outerHTML"),
                    )(i.attrs(_class("fa fa-arrow-down fa-2x"))),
                    button.attrs(
                        _class("text-blue-500 font-bold text-4xl lg:text-sm"),
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
    root_comment: schema.Comment, comments: list[schema.Comment], top: bool = False
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

    if top:
        return single_comment(
            root_comment,
            child=ul.attrs(_class("ml-16"))(*comment_elements),
        )
    else:
        return ul.attrs(_class("ml-16"))(*comment_elements)


def comment_tree_view(comments: list[schema.Comment], post_id: int) -> str:
    comment_trees: list[Tag] = []
    for top_comment in filter(lambda c: c.parent_id is None, comments):
        comment_trees.append(
            one_comment_tree(root_comment=top_comment, comments=comments, top=True)
        )
    return render(
        div.attrs(
            _class(
                "mt-4 pt-4 flex flex-col justify-start items-start "
                "border-gray-600 items-stretch max-w-max"
            ),
            id=(f"post-{post_id}-comments"),
        )(
            new_comment_form_partial(
                post_url=f"/post/{post_id}/comment", post_id=post_id
            ),
            ul(*comment_trees),
        )
    )

def transition_render(elem: Any):
    return elem.render()

def post_view(
    post: schema.Post,
    user: schema.User | None = None,
    partial_html: bool = False,
    editor: bool = False,
) -> str:
    post_html = post_partial(post, editor=editor)
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
