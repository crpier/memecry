import contextlib
from pathlib import Path

from relax.app import ViewContext
from relax.html import (
    Element,
    Fragment,
    a,
    button,
    div,
    i,
    img,
    input,
    li,
    main,
    span,
    textarea,
    ul,
    video,
)
from relax.injection import Injected, component, injectable_sync
from uvicorn.supervisors.watchfilesreload import WatchFilesReload

import memecry.config
import memecry.routes.post
import memecry.schema
import memecry.views.common
import memecry.main

IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
VIDEO_FORMATS = [".mp4", ".webm"]


@injectable_sync
def tags_component(  # noqa: PLR0913
    post_id: int = 0,
    post_tags: str = "no-tags",
    *,
    editable: bool = False,
    hidden_dropdown: bool = True,
    config: memecry.config.Config = Injected,
    context: ViewContext = Injected,
) -> div:
    # TODO: get put element_id in component
    element_id = f"tags-{post_id}"
    tags_selector_id = f"tags-selector-{post_id}"

    # TODO: can I use "truncate" class to hide overflow instead?
    def li_tag(tag: str) -> li:
        return li(
            classes=[
                *memecry.views.common.SIMPLE_BUTTON_CLASSES,
                "!p-0",
                "!border-0",
                "[&:not(:first-child)]:!rounded-t-none",
                "[&:not(:last-child)]:!rounded-b-none",
                "bg-gray-800" if tag in post_tags else "",
                "w-full",
            ]
        ).insert(
            button(
                attrs={"name": "tag", "value": tag},
                classes=[
                    *memecry.views.common.SIMPLE_BUTTON_CLASSES,
                    "!border-0",
                    "!rounded-none",
                    "w-full",
                    "m-auto",
                ],
            )
            .text(tag)
            .hx_put(
                # TODO: fixme
                context.url_of(memecry.routes.post.update_tags)(post_id=post_id),  # type: ignore
                hx_target=f"#{element_id}",
                hx_swap="outerHTML",
            ),
        )

    return div(
        id=element_id,
        classes=[
            "max-w-full",
            "whitespace-nowrap",
            "overflow-hidden",
        ],
    ).insert(
        input(name="tags", type="text", value=post_tags, classes=["hidden"]),
        button(
            classes=[
                *memecry.views.common.SIMPLE_BUTTON_CLASSES,
                "cursor-default" if not editable else "cursor-pointer",
                "max-w-full",
                "overflow-hidden",
                "overflow-ellipsis",
            ],
            hyperscript=f"on click toggle .hidden on #{tags_selector_id}"
            if editable
            else "",
        ).text(post_tags),
        div(
            id=tags_selector_id,
            classes=[
                *memecry.views.common.DROPDOWN_CLASSES,
                "hidden" if hidden_dropdown else "",
            ],
        ).insert(
            ul().insert(
                [li_tag(tag) for tag in config.DEFAULT_TAGS],
            ),
        ),
    )


def post_title_section(post: memecry.schema.PostRead) -> Element:
    return div(
        classes=memecry.views.common.FLEX_ROW_WRAPPER_CLASSES,
    ).insert(
        input(
            id=f"title-{post.id}",
            classes=[
                *memecry.views.common.INPUT_CLASSES,
                "text-center",
                "flex-1",
            ],
            type="text",
            name=f"title-{post.id}",
            value=post.title,
            disabled=not post.editable,
        ),
        div(
            classes=[
                "flex-0",
                "text-right",
                "invisible" if not post.editable else "",
            ],
        ).insert(
            button(classes=["w-max", "pb-4", "px-2"])
            .insert(i(classes=["fa", "fa-lg", "fa-gear"]))
            .hx_put(
                f"/posts/{post.id}/title",
                hx_swap="none",
                hx_encoding="multipart/form-data",
                hx_include=f"#title-{post.id}",
            ),
        ),
    )


def post_info_pane(*, post: memecry.schema.PostRead) -> Element:
    return div(classes=memecry.views.common.FLEX_ROW_WRAPPER_CLASSES).insert(
        div(
            classes=[
                "md:font-semibold",
                "text-sm",
                "md:text-base",
            ]
        ).text(f"{post.score} good boi points"),
        div(classes=["space-x-1"]).insert(
            span(
                classes=[
                    "md:font-semibold",
                    "text-sm",
                    "md:text-base",
                ]
            ).text(f"{post.created_since} by"),
            a(
                href="#",
                classes=[
                    "md:font-semibold",
                    "text-sm",
                    "md:text-base",
                    "text-green-300",
                ],
            ).text(post.author_name),
        ),
    )


def post_interaction_pane(tags: Element, search_content_id: str) -> Element:
    return div(classes=memecry.views.common.FLEX_ROW_WRAPPER_CLASSES).insert(
        div(classes=memecry.views.common.FLEX_ROW_WRAPPER_CLASSES).insert(
            button(
                type="button",
                classes=[
                    *memecry.views.common.SIMPLE_BUTTON_CLASSES,
                    "hover:text-green-700",
                    "hover:border-green-700",
                ],
            ).insert(i(classes=["fa", "fa-arrow-up"])),
            button(
                type="button",
                classes=[
                    *memecry.views.common.SIMPLE_BUTTON_CLASSES,
                    "hover:text-red-800",
                    "hover:border-red-800",
                ],
            ).insert(i(classes=["fa", "fa-arrow-down"])),
        ),
        tags,
        div(classes=["flex-grow"]),
        button(
            type="button",
            classes=memecry.views.common.SIMPLE_BUTTON_CLASSES,
            hyperscript=f"on click toggle .hidden on #{search_content_id}",
        ).insert(i(classes=["fa", "fa-gear", "fa-lg"])),
        button(
            classes=[
                *memecry.views.common.SIMPLE_BUTTON_CLASSES,
                "font-semibold",
                "whitespace-nowrap",
            ]
        ).text("0 comments"),
    )


@component(key=lambda post: post.id)
def post_settings_pane(
    # TODO: we should ensure it's mandatory that framwork params are keyword only
    post: memecry.schema.PostRead,
    parent_id: str,
    *,
    id: str = Injected,
    context: ViewContext = Injected,
) -> Element:
    delete_post_url = context.url_of(memecry.routes.post.delete_post)
    update_searchable_content_url = context.url_of(
        memecry.routes.post.update_searchable_content
    )
    return div(
        classes=[*memecry.views.common.FLEX_COL_WRAPPER_CLASSES, "hidden"],
    ).insert(
        textarea(
            name=f"content-input-{post.id}",
            type="text",
            classes=[
                "block",
                "p-2",
                "w-full",
                "my-4",
                "bg-black",
                "outline-none",
            ],
            disabled=not post.editable,
        ).text(post.searchable_content),
        div(classes=memecry.views.common.FLEX_ROW_WRAPPER_CLASSES).insert(
            button(
                type="button",
                classes=memecry.views.common.DANGER_SPECIAL_BUTTON_CLASSES,
                hyperscript="""on htmx:confirm(issueRequest)
             halt the event
             call Swal.fire({
                 title: 'Confirm',
                 text: 'Are you sure you want to delete this post?',
                 // same color as the navbar
                 background: '#111827',
                 color: '#ffffff',
                 buttonsStyling: false,
                 customClass: {
                     confirmButton: 'bg-green-600 px-4 py-1 rounded-md text-lg'
                 }
             })
             if result.isConfirmed issueRequest()""",
            )
            # TODO: can I do something like hx_request(url_func, kwargs, hx_trigger, ..)
            .hx_delete(
                delete_post_url(post_id=post.id),
                hx_trigger="click",
                hx_swap="delete",
                hx_target=f"#{parent_id}",
            )
            .text("Delete post"),
            button(
                type="button",
                classes=memecry.views.common.ATTENTION_SPECIAL_BUTTON_CLASSES,
                hyperscript=f"on click toggle .hidden on #{id}",
            )
            .text("Save")
            .hx_put(
                update_searchable_content_url(post_id=post.id),
                hx_trigger="click",
                hx_swap="none",
                # TODO: weird that I have to duplicate this
                hx_include=f"[name='content-input-{post.id}']",
                hx_encoding="multipart/form-data",
            ),
        )
        if post.editable
        else div(),
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
            classes=["w-full"],
            controls=True,
        )
    return div().text(f"Unsupported format: {Path(post.source).suffix}")


# TODO: either allow positional args, or encode their absence in a type sig somehow
@component(key=lambda post: post.id)
def post_component(post: memecry.schema.PostRead, *, id: str = Injected) -> div:
    post_settings = post_settings_pane(post=post, parent_id=id)

    return div(
        classes=[
            *memecry.views.common.FLEX_ELEMENT_WRAPPER_CLASSES,
            "focus:!border-gray-400",
            "outline-none",
            "md:max-w-2xl",
        ],
        attrs={"tabindex": -1},
    ).insert(
        post_title_section(post),
        post_content_component(post),
        post_info_pane(post=post),
        post_interaction_pane(
            tags_component(
                post.id,
                post.tags,
                editable=post.editable,
            ),
            post_settings.id,
        ),
        post_settings,
    )


def home_view(
    posts: list[memecry.schema.PostRead],
    offset: int = 0,
    limit: int = 5,
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
                f"/?offset={offset+limit}",
                hx_trigger="revealed",
                hx_swap="afterend",
            )

    if partial:
        return Fragment(post_views)
    return main(
        # use the "divide-*" class to split posts, instead
        classes=[
            *memecry.views.common.FLEX_COL_WRAPPER_CLASSES,
            "md:w-[32rem]",
            "mx-auto",
        ],
    ).insert(
        post_views,
    )
