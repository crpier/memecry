import contextlib
from pathlib import Path

from relax.html import (
    Element,
    Fragment,
    a,
    button,
    dialog,
    div,
    form,
    i,
    img,
    input,
    main,
    span,
    textarea,
    ul,
    video,
)
from relax.injection import Injected, component, injectable_sync
from starlette.datastructures import URLPath

import memecry.config
import memecry.main
import memecry.routes.post
import memecry.schema
import memecry.views.common

IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
VIDEO_FORMATS = [".mp4", ".webm"]


@component(key=lambda __post_id__: __post_id__)
def tags_button_component(
    __post_id__: int,  # noqa: ARG001
    tags: str,
    *,
    editable: bool,
    id: str = Injected,
) -> Element:
    return div(
        id=id,
        attrs={
            "tabindex": "0",
            "role": "button",
        },
        classes=[
            "btn",
            "btn-sm",
            "truncate",
            "overflow-ellipsis",
            "btn-outline",
            "block",
            "leading-8",
            "pointer-events-none" if not editable else "",
        ],
        text=tags,
    )


@component(key=lambda post_id: post_id)
def tags_component(
    *,
    post_id: int,
    selected_tags: str = "no-tags",
    editable: bool = False,
    config: memecry.config.Config = Injected,
) -> Element:
    active_tags = selected_tags.split(", ")
    all_tags = config.DEFAULT_TAGS

    tags_button = tags_button_component(
        __post_id__=post_id, tags=", ".join(active_tags), editable=editable
    )

    def option_input(tag: str, *, active: bool = False) -> input:
        attrs = {"aria-label": tag}
        if active:
            attrs["checked"] = "true"
        return input(
            name=tag,
            type="checkbox",
            classes=[
                "btn",
                "btn-sm",
                "btn-ghost",
                "text-left",
                "m-0",
                "rounded-none",
                "first:rounded-t-md",
                "last:rounded-b-md",
            ],
            value=tag,
            attrs=attrs,
        )

    return (
        form(classes=["dropdown", "dropdown-end", "max-w-[50%]"])
        .hx_put(
            target=memecry.routes.post.update_tags(post_id=post_id),
            hx_target=f"#{tags_button.id}",
            hx_trigger="change",
            hx_swap="outerHTML",
        )
        .insert(
            tags_button,
            ul(
                attrs={"tabindex": "0"},
                classes=[
                    "dropdown-content",
                    "menu",
                    "z-[1]",
                    "shadow",
                    "rounded-b-md",
                    "bg-base-100",
                    "pt-1",
                    "px-0",
                    "pb-0",
                ],
            ).insert(
                [option_input(tag, active=tag in active_tags) for tag in all_tags]
            ),
        )
    )


@component(key=lambda post: post.id)
def post_title_section(*, post: memecry.schema.PostRead) -> Element:
    return div(classes=["text-center", "p-2"]).insert(
        a(
            href=memecry.routes.post.get_post(post_id=post.id),
            classes=[
                "text-lg",
                "font-bold",
                "link",
                "link-hover",
            ],
            text=post.title,
        )
    )


def post_info_pane(*, post: memecry.schema.PostRead) -> Element:
    return div(
        classes=[
            "flex",
            "justify-between",
            "px-1",
            "sm:px-0",
            "sm:py-2",
        ]
    ).insert(
        div().insert(
            span(
                classes=[
                    "sm:font-semibold",
                ]
            ).text(f"{post.score} good boi points"),
        ),
        div(classes=["space-x-1"]).insert(
            span(
                classes=[
                    "sm:font-semibold",
                ]
            ).text(f"{post.created_since} by"),
            a(
                href="#",
                classes=[
                    "link",
                    "link-hover",
                    "font-semibold",
                    "text-secondary-content",
                ],
            ).text(post.author_name),
        ),
    )


def post_interaction_pane(
    post: memecry.schema.PostRead, search_content_id: str
) -> Element:
    tags = tags_component(
        post_id=post.id,
        selected_tags=post.tags,
        editable=post.editable,
    )
    return div(classes=["flex", "pb-2", "items-center"]).insert(
        div(classes=[]).insert(
            button(
                type="button",
                classes=[
                    *memecry.views.common.SIMPLE_BUTTON_CLASSES,
                    "btn-ghost",
                    "text-primary",
                    "hover:bg-base-100",
                    "hover:text-green-700",
                    "hover:border-green-700",
                ],
            ).insert(i(classes=["fa", "fa-arrow-up", "fa-lg"])),
            button(
                type="button",
                classes=[
                    *memecry.views.common.SIMPLE_BUTTON_CLASSES,
                    "btn-ghost",
                    "text-primary",
                    "hover:bg-base-100",
                    "hover:text-red-800",
                    "hover:border-red-800",
                ],
            ).insert(i(classes=["fa", "fa-arrow-down", "fa-lg"])),
        ),
        div(classes=["flex-grow"]),
        tags.classes(["mr-2"]),
        button(
            type="button",
            classes=[*memecry.views.common.SIMPLE_BUTTON_CLASSES, "btn-ghost"],
            hyperscript=f"on click toggle .hidden on #{search_content_id}",
        ).insert(i(classes=["fa", "fa-gear", "fa-lg"])),
        button(
            classes=[
                *memecry.views.common.SIMPLE_BUTTON_CLASSES,
                "btn-ghost",
                "font-semibold",
                "whitespace-nowrap",
            ]
        ).insert(span(text="0"), i(classes=["fa", "fa-comment"])),
    )


@component(key=lambda post: post.id)
def delete_confirmation_modal(
    *,
    post: memecry.schema.PostRead,
    parent_post_id: str,
) -> Element:
    return dialog(classes=["modal", "modal-bottom", "sm:modal-middle"]).insert(
        div(classes=["modal-box", "space-y-4", "max-w-full", "sm:max-w-lg"]).insert(
            div(
                classes=[
                    "font-bold",
                    "text-xl",
                    "text-center",
                    "items-center",
                    "justify-center",
                ],
                text="Whoa slow down. Are you sure you want to delete this post?",
            ),
            div(classes=["flex", "justify-evenly"]).insert(
                form(
                    attrs={"method": "dialog"},
                ).insert(
                    button(
                        type="submit",
                        classes=["btn"],
                        text="No, go back",
                    ),
                ),
                form(classes=["form-control", "space-y-4", "flex-row"])
                .insert(
                    button(
                        type="submit",
                        classes=["btn", "btn-primary"],
                    ).text("Delete"),
                )
                .hx_delete(
                    memecry.routes.post.delete_post(post_id=post.id),
                    hx_trigger="click",
                    hx_swap="delete",
                    hx_target=f"#{parent_post_id}",
                ),
            ),
        ),
    )


@component(key=lambda post: post.id)
def post_settings_pane(
    post: memecry.schema.PostRead,
    parent_id: str,
    *,
    id: str = Injected,
) -> Element:
    delete_confirmation_element = delete_confirmation_modal(
        post=post, parent_post_id=parent_id
    )
    searcheable_content_input_name = f"content-input-{post.id}"
    return div(classes=["hidden", "m-auto"]).insert(
        delete_confirmation_element,
        form(
            classes=[
                *memecry.views.common.FLEX_COL_WRAPPER_CLASSES,
                "!space-y-4",
                "pb-4",
            ],
        ).insert(
            textarea(
                name=searcheable_content_input_name,
                id=searcheable_content_input_name,
                type="text",
                classes=["textarea", "textarea-bordered", "w-full", "mt-4"],
                disabled=not post.editable,
            ).text(post.searchable_content),
            div(
                classes=[
                    "space-x-4",
                    "flex",
                    "flex-row",
                    "justify-end",
                    "w-full",
                    "px-2",
                ]
            ).insert(
                button(
                    type="button",
                    classes=[*memecry.views.common.SIMPLE_BUTTON_CLASSES],
                    hyperscript=f"on click call #{delete_confirmation_element.id}'s "
                    "showModal()",
                ).text("Delete"),
                button(
                    type="button",
                    classes=[
                        *memecry.views.common.SIMPLE_BUTTON_CLASSES,
                        "btn-neutral",
                    ],
                    hyperscript=f"on click toggle .hidden on #{id}",
                )
                .text("Save")
                .hx_put(
                    memecry.routes.post.update_searchable_content(
                        post_id=post.id
                    ),
                    hx_trigger="click",
                    hx_swap="none",
                    hx_encoding="multipart/form-data",
                ),
            )
            if post.editable
            else div(),
        ),
    )


def post_content_component(post: memecry.schema.PostRead) -> Element:
    if Path(post.source).suffix in IMAGE_FORMATS:
        return img(
            src=post.source,
            alt=post.title,
            classes=["w-full"],
        )
    if Path(post.source).suffix in VIDEO_FORMATS:
        return video(
            src=post.source,
            classes=["w-full", "autoplayable" if post.autoplayable else ""],
            controls=True,
        )
    return div().text(f"Unsupported format: {Path(post.source).suffix}")


@component(key=lambda post: post.id)
def post_component(*, post: memecry.schema.PostRead, id: str = Injected) -> div:
    post_settings = post_settings_pane(post=post, parent_id=id)

    return div(
        classes=[
            "space-y-1",
            "w-full",
            "outline-none",
            "w-screen",
            "sm:max-w-lg",
            "sm:border",
            "sm:border-gray-600",
            "sm:px-4",
            "sm:rounded-lg",
            "bg-base-100",
        ]
    ).insert(
        post_title_section(post=post),
        post_content_component(post),
        post_info_pane(post=post),
        post_interaction_pane(
            post,
            post_settings.id,
        ),
        post_settings,
    )


@injectable_sync
def home_view(
    next_page_url: URLPath,
    posts: list[memecry.schema.PostRead],
    *,
    keep_scrolling: bool = False,
    partial: bool = False,
) -> Element:
    post_views = [
        post_component(
            post=post,
        )
        for post in posts
    ]
    if keep_scrolling:
        with contextlib.suppress(IndexError):
            post_views[-1].hx_get(
                next_page_url,
                hx_trigger="revealed",
                hx_swap="afterend",
            )

    if partial:
        return Fragment(post_views)
    return main(
        classes=[
            *memecry.views.common.FLEX_COL_WRAPPER_CLASSES,
            "mx-auto",
        ],
    ).insert(
        post_views,
    )
