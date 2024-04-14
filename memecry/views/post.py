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

    return div(classes=["dropdown"]).insert(
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
        input(
            id=text_div_id,
            type="text",
            name="tags",
            attrs={"readonly": "true"},
            classes=[
                "btn",
                "btn-sm",
                "w-max",
                "max-w-full",
                "truncate",
                "align-center",
                "block",
                "leading-8",
                "pointer-events-none" if not editable else "",
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
                "bg-base-100",
                "space-y-1",
                "space-x-1",
                "hidden" if not editable else "",
            ],
        ).insert(options),
    )


@component(key=lambda post: post.id)
def post_title_section(*, post: memecry.schema.PostRead) -> Element:
    return div(classes=["text-center", "text-lg"], text=post.title)
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
    return div(
        classes=[*memecry.views.common.FLEX_ROW_WRAPPER_CLASSES, "max-w-xl"]
    ).insert(
        div(
            classes=[
                "sm:font-semibold",
                "text-sm",
                "sm:text-base",
            ]
        ).text(f"{post.score} good boi points"),
        div(classes=["space-x-1"]).insert(
            span(
                classes=[
                    "sm:font-semibold",
                    "text-sm",
                    "sm:text-base",
                ]
            ).text(f"{post.created_since} by"),
            a(
                href="#",
                classes=[
                    "sm:font-semibold",
                    "text-sm",
                    "sm:text-base",
                    "text-secondary-content",
                ],
            ).text(post.author_name),
        ),
    )


def post_interaction_pane(tags: Element, search_content_id: str) -> Element:
    return div(
        classes=[*memecry.views.common.FLEX_ROW_WRAPPER_CLASSES, "max-w-xl"]
    ).insert(
        div(
            classes=[*memecry.views.common.FLEX_ROW_WRAPPER_CLASSES, "max-w-xl"]
        ).insert(
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
            *memecry.views.common.FLEX_ELEMENT_WRAPPER_CLASSES,
            "outline-none",
            "w-screen",
            "sm:max-w-4xl",
        ]
    ).insert(
        post_title_section(post=post),
        post_content_component(post),
        post_info_pane(post=post),
        post_interaction_pane(
            tags_component(
                post_id=post.id,
                selected_tags=post.tags,
                editable=post.editable,
            ),
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
        # use the "divide-*" class to split posts, instead
        classes=[
            *memecry.views.common.FLEX_COL_WRAPPER_CLASSES,
            "mx-auto",
        ],
    ).insert(
        post_views,
    )
