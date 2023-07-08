from pathlib import Path
from yahgl_py.main import div, button, p, img, Tag, video, i, a

from src import schema


def content_is_image(file_name: Path) -> bool:
    return file_name.suffix in [".png", ".jpg", ".jpeg"]


def post_view(post: schema.Post, editor=False) -> Tag:
    if content_is_image(post.source):
        post_content = img(classes=["w-full"], src=str(post.source), alt=post.title)
    else:
        post_content = video(classes=["w-full"], src=str(post.source), controls=True)
    # if post.editable:
    if True:
        edit_button = button(
            attrs=dict(
                hx_get=(f"/post/{post.id}/edit"),
                hx_target=(f"#post-{post.id}"),
                hx_swap=("outerHTML"),
            ),
            classes=[
                "px-3",
                "py-3",
                "flex",
                "flex-row",
                "rounded-md",
            ],
        ).insert(i(classes=["fa", "fa-bars", "fa-lg"]))
    else:
        edit_button = None
    if editor:
        # title_bar = form.attrs(
        #     _class("w-full text-4xl lg:text-lg"),
        #     hx_encoding("application/x-www-form-urlencoded"),
        #     hx_post(f"/post/{post.id}/edit"),
        #     hx_target(f"#post-{post.id}"),
        #     hx_swap("outerHTML"),
        #     id=f"post-{post.id}-edit-form",
        # )(
        #     textarea.attrs(
        #         _class(
        #             "mb-4 mt-2 px-2 py-1 bg-black text-center w-full text-5xl "
        #             "lg:text-xl"
        #         ),
        #         type="text",
        #         name="title",
        #         rows=str(len(post.title) // 40 + 1),
        #     )(post.title)
        # )
        # cancel_button = button.attrs(
        #     _class(
        #         "px-3 ml-auto mt-2 rounded-md border border-gray-600 font-bold "
        #         "hover:border-gray-700 hover:bg-gray-700"
        #     ),
        #     hx_get(f"/post/{post.id}?partial_html=true"),
        #     hx_target(f"#post-{post.id}"),
        #     hx_swap("outerHTML"),
        # )("X")
        # edit_button = button.attrs(
        #     _class(
        #         "font-bold mr-2 mt-4 px-3 py-2 flex flex-row p-2 rounded-md "
        #         "border-gray-600 hover:border-gray-500 hover:bg-green-700 "
        #         "lg:mt-2"
        #     ),
        #     type="submit",
        #     form=f"post-{post.id}-edit-form",
        # )("Save")
        # delete_button = button.attrs(
        #     _class(
        #         "font-bold mr-2 mt-4 px-3 py-2 flex flex-row p-2 rounded-md "
        #         "bg-red-700 border-gray-600 hover:border-red-600 hover:bg-red-600 "
        #         "lg:mt-2"
        #     ),
        #     hx_delete(f"/post/{post.id}"),
        # )("Delete")
        title_bar = p(classes=["mb-4", "font-bold", "text-xl"]).text(post.title)
        cancel_button = None
        delete_button = None
    else:
        title_bar = p(classes=["mb-4", "font-bold", "text-xl"]).text(post.title)
        cancel_button = None
        delete_button = None

    return div(
        classes=[
            "flex",
            "flex-col",
            "items-center",
            "my-4",
            "text-center",
            "rounded-md",
            "w-full",
            "w-full",
            "lg:p-4",
            "bg-gray-800",
        ],
        id=f"post-{post.id}",
    ).insert(
        cancel_button,
        title_bar,
        a(classes=["w-full"], href=f"/post/{post.id}").insert(post_content),
        div(
            classes=[
                "flex",
                "flex-row",
                "items-center",
                "justify-start",
                "w-full",
                "text-sm",
                "my-2",
                "px-2",
                "lg:px-0",
            ]
        ).insert(
            a(
                href=".",
            ).text(f"{post.score} good boi points"),
            div(classes=["flex-grow"]),
            p(classes=["mr-1"]).text(post.created_since + " by"),
            a(classes=["font-bold", "text-green-300"], href=".").text(
                post.user.username
            ),
        ),
        div(
            classes=[
                "flex",
                "flex-grow-0",
                "flex-row",
                "items-start",
                "justify-start",
                "w-full",
                "mt-1",
            ]
        ).insert(
            button(
                classes=[
                    "mr-3",
                    "py-1",
                    "px-2",
                    "rounded",
                    "bg-yellow-800" if post.liked else "",
                ],
                attrs=dict(
                    hx_put=(f"/post/{post.id}/like"),
                    hx_target=(f"#post-{post.id}"),
                    hx_swap=("outerHTML"),
                ),
            ).insert(i(classes=["fa", "fa-arrow-up", "fa-lg"])),
            button(
                classes=[
                    "mr-3",
                    "py-1",
                    "px-2",
                    "rounded",
                    "bg-blue-900" if post.disliked else "",
                ],
                attrs=dict(
                    hx_put=(f"/post/{post.id}/dislike"),
                    hx_target=(f"#post-{post.id}"),
                    hx_swap=("outerHTML"),
                ),
            ).insert(i(classes=["fa", "fa-arrow-down", "fa-lg"])),
            div(classes=["flex-grow"]),
            delete_button,
            edit_button,
            button(
                classes=[
                    "flex",
                    "p-2",
                    "flex-row",
                    "rounded-md",
                    "items-center",
                    "justify-center",
                    "hover:border-gray-500",
                ],
                attrs=dict(
                    hx_get=(f"/post/{post.id}/comments"),
                    hx_target=(f"#post-comments-{post.id}"),
                ),
            ).insert(
                i(
                    classes=["fa", "fa-comment", "mr-2"],
                ),
                p().text(f"{post.comment_count} comments"),
            ),
        ),
        div(id=f"post-comments-{post.id}"),
    )


def posts_view(posts: list[schema.Post]):
    return div(classes=["max-w-[580px]", "flex", "flex-col", "mx-auto"]).insert(
        *[post_view(post) for post in posts],
    )
