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
    main,
    script,
    span,
    textarea,
    ul,
    video,
)
from relax.injection import Injected, component, injectable_sync

import memecry.config
import memecry.main
import memecry.routes.post
import memecry.schema
import memecry.views.common

IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
VIDEO_FORMATS = [".mp4", ".webm"]


# TODO: allow default values for params used in lambda function
@component(key=lambda post_id: post_id)
def tags_component(  # noqa: PLR0913
    *,
    post_id: int,
    selected_tags: str = "no-tags",
    editable: bool = False,
    config: memecry.config.Config = Injected,
    context: ViewContext = Injected,
    id: str = Injected,
) -> Element:
    update_tags_url = context.url_of(memecry.routes.post.update_tags)
    text_div_id = f"tags-text-{id}"
    useless_element = div(id="empty-useless-target", classes=["hidden"])

    active_tags = selected_tags.split(", ")
    available_tags = config.DEFAULT_TAGS

    def option_input(tag: str, *, active: bool = False) -> input:
        attrs = {"aria-label": tag, "onclick": f"input_clicked_{post_id}(event)"}
        if active:
            attrs["checked"] = "true"
        return input(
            name=id,
            type="checkbox",
            classes=["btn", "btn-xs", "btn-ghost"],
            value=tag,
            attrs=attrs,
        )

    options = [option_input(tag, active=tag in active_tags) for tag in available_tags]

    return div(
        classes=[
            "dropdown",
        ]
    ).insert(
        useless_element,
        script(  # TODO: revert change to dropdown text if we got an error from htmx
            js=f"""
    var input_clicked_{post_id} = function(event) {{
        const target = event.target;
        const siblingOptions = document.getElementsByName(target.name);
        let activeOptions = Array.from(siblingOptions).filter(
            option => option.checked).map(
            option => option.value
        ).join(", ");
        if (activeOptions === "") {{
            activeOptions = "no-tags";
        }}
        const dropdown = document.getElementById("{text_div_id}");
        dropdown.setAttribute("value", activeOptions);
        htmx.ajax("PUT", "{update_tags_url(post_id=post_id)}", {{
            swap: "none",
            target: "#empty-useless-target",
            values: {{
                tag: target.value,
                tags: activeOptions,
            }}
        }});
    }}"""
        ),
        # TODO: find a way to make this a span, or something easier to style
        # so that I can set width to max-content
        input(
            id=text_div_id,
            type="text",
            name="tags",
            attrs={"readonly": "true"},
            classes=[
                "btn",
                "btn-sm",
                "btn-outline",
                "truncate",
                "block",
                "leading-8",
                "pointer-events-none" if not editable else "",
                "max-w-[6rem]",
            ],
            value=", ".join(active_tags),
        ),
        ul(
            attrs={"tabindex": "0"},
            classes=[
                "dropdown-content",
                "menu",
                "z-[1]",
                "p-2",
                "shadow",
                "space-y-2",
                "space-x-1",
                "rounded-b-lg",
                "bg-base-200",
                "hidden" if not editable else "",
            ],
        ).insert(options),
    )


@component(key=lambda post: post.id)
def post_title_section(
    *, post: memecry.schema.PostRead, view_context: ViewContext = Injected
) -> Element:
    return div(classes=["text-center", "p-2"]).insert(
        a(
            href=view_context.url_of(memecry.routes.post.get_post)(post_id=post.id),
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
            ).insert(i(classes=["fa", "fa-arrow-up"])),
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
            ).insert(i(classes=["fa", "fa-arrow-down"])),
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
def post_settings_pane(
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
    searcheable_content_input_name = f"content-input-{post.id}"
    return div(
        classes=[*memecry.views.common.FLEX_COL_WRAPPER_CLASSES, "hidden"],
    ).insert(
        textarea(
            name=searcheable_content_input_name,
            type="text",
            classes=[
                "block",
                "p-2",
                "w-full",
                "my-4",
                "outline-none",
            ],
            disabled=not post.editable,
        ).text(post.searchable_content),
        div(classes=memecry.views.common.FLEX_ROW_WRAPPER_CLASSES).insert(
            button(
                type="button",
                classes=memecry.views.common.SECONDARY_BUTTON_CLASSES,
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
            .hx_delete(
                delete_post_url(post_id=post.id),
                hx_trigger="click",
                hx_swap="delete",
                hx_target=f"#{parent_id}",
            )
            .text("Delete post"),
            button(
                type="button",
                classes=memecry.views.common.SECONDARY_BUTTON_CLASSES,
                hyperscript=f"on click toggle .hidden on #{id}",
            )
            .text("Save")
            .hx_put(
                update_searchable_content_url(post_id=post.id),
                hx_trigger="click",
                hx_swap="none",
                hx_include=searcheable_content_input_name,
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
def home_view(  # noqa: PLR0913
    posts: list[memecry.schema.PostRead],
    offset: int = 0,
    limit: int | None = None,
    *,
    keep_scrolling: bool = False,
    partial: bool = False,
    config: memecry.config.Config = Injected,
) -> Element:
    if limit is None:
        limit = config.POSTS_LIMIT
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
        classes=[
            *memecry.views.common.FLEX_COL_WRAPPER_CLASSES,
            "mx-auto",
        ],
    ).insert(
        post_views,
    )
