from pathlib import Path

from relax.app import ViewContext
from relax.html import (
    SelfClosingTag,
    Tag,
    a,
    button,
    div,
    i,
    img,
    input,
    li,
    span,
    textarea,
    ul,
    video,
)
from relax.injection import Injected, injectable_sync

import memecry.config
import memecry.routes.post
import memecry.schema
from memecry.views.common import (
    DROPDOWN_CLASSES,
    FLEX_COL_WRAPPER_CLASSES,
    FLEX_ROW_WRAPPER_CLASSES,
    SIMPLE_BUTTON_CLASSES,
    special_button_classes,
)

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
    element_id = f"tags-{post_id}"
    tags_selector_id = f"tags-selector-{post_id}"

    def li_tag(tag: str) -> li:
        return li().insert(
            button(
                attrs={"name": "tag", "value": tag},
                classes=[
                    *SIMPLE_BUTTON_CLASSES,
                    "border-0",
                    "bg-gray-800" if tag in post_tags else "",
                ],
            )
            .text(tag)
            .hx_put(
                context.endpoint(memecry.routes.post.UpdateTags)(post_id=post_id),
                hx_target=f"#{element_id}",
                hx_swap="outerHTML",
            ),
        )

    return div(id=element_id).insert(
        input(name="tags", type="text", value=post_tags, classes=["hidden"]),
        button(
            classes=[
                *SIMPLE_BUTTON_CLASSES,
                "cursor-default" if not editable else "cursor-pointer",
            ],
            hyperscript=f"on click toggle .hidden on #{tags_selector_id}"
            if editable
            else "",
        ).text(post_tags),
        div(
            id=tags_selector_id,
            classes=[*DROPDOWN_CLASSES, "hidden" if hidden_dropdown else ""],
        ).insert(
            ul().insert(
                [li_tag(tag) for tag in config.DEFAULT_TAGS],
            ),
        ),
    )


# TODO: maybe better to have a single update endpoint?
@injectable_sync
def post_component(
    post: memecry.schema.PostRead,
    *,
    context: ViewContext = Injected,
) -> div:
    search_content_id = f"search-{post.id}"
    element_id = f"post-{post.id}"

    delete_post_url = context.endpoint(memecry.routes.post.DeletePost)
    update_searchable_content_url = context.endpoint(
        memecry.routes.post.UpdateSearchableContent
    )
    content: Tag | SelfClosingTag
    if Path(post.source).suffix in IMAGE_FORMATS:
        content = img(
            src=post.source,
            alt=post.title,
            classes=["w-full"],
        )
    elif Path(post.source).suffix in VIDEO_FORMATS:
        content = video(
            src=post.source,
            classes=["w-full"],
            controls=True,
        )
    else:
        content = div().text(f"Unsupported format: {Path(post.source).suffix}")
    title_section = div(
        classes=FLEX_ROW_WRAPPER_CLASSES,
    ).insert(
        input(
            id=f"title-{post.id}",
            classes=[
                "text-white",
                "text-2xl",
                "font-bold",
                "mb-4",
                "px-2",
                "bg-black",
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
            # TODO: edit title when the input element changes, instead
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
    info_pane = div(classes=FLEX_ROW_WRAPPER_CLASSES).insert(
        div(classes=["md:font-semibold"]).text(f"{post.score} good boi points"),
        div(classes=["space-x-1"]).insert(
            span(classes=["md:font-semibold"]).text(f"{post.created_since} by"),
            a(href="#", classes=["md:font-semibold", "text-green-300"]).text(
                post.author_name
            ),
        ),
    )
    tags = tags_component(
        post.id,
        post.tags,
        editable=post.editable,
    )
    info_button = button(
        type="button",
        classes=SIMPLE_BUTTON_CLASSES,
        hyperscript=f"on click toggle .hidden on #{search_content_id}",
    ).insert(i(classes=["fa", "fa-gear", "fa-lg"]))
    interaction_pane = div(classes=FLEX_ROW_WRAPPER_CLASSES).insert(
        div(classes=FLEX_ROW_WRAPPER_CLASSES).insert(
            button(
                type="button",
                classes=[
                    *SIMPLE_BUTTON_CLASSES,
                    "hover:text-green-700",
                    "hover:border-green-700",
                ],
            ).insert(i(classes=["fa", "fa-arrow-up"])),
            button(
                type="button",
                classes=[
                    *SIMPLE_BUTTON_CLASSES,
                    "hover:text-red-800",
                    "hover:border-red-800",
                ],
            ).insert(i(classes=["fa", "fa-arrow-down"])),
        ),
        tags,
        div(classes=["flex-grow"]),
        info_button,
        button(classes=[*SIMPLE_BUTTON_CLASSES, "font-semibold"]).text("0 comments"),
    )
    settings_pane = div(
        classes=[*FLEX_COL_WRAPPER_CLASSES, "hidden"],
        id=search_content_id,
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
        div(classes=FLEX_ROW_WRAPPER_CLASSES).insert(
            button(
                type="button",
                classes=special_button_classes("red"),
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
                hx_target=f"#{element_id}",
            )
            .text("Delete post"),
            button(
                type="button",
                classes=special_button_classes("green"),
                hyperscript=f"on click toggle .hidden on #{search_content_id}",
            )
            .text("Save")
            .hx_put(
                update_searchable_content_url(post_id=post.id),
                hx_trigger="click",
                hx_swap="none",
                hx_include=f"[name='content-input-{post.id}']",
                hx_encoding="multipart/form-data",
            ),
        )
        if post.editable
        else div(),
    )
    return div(
        id=element_id,
        classes=[
            "md:border-2",
            "md:border-gray-500",
            "md:p-4",
            "md:rounded-lg",
            "post-component",
            "space-y-1",
            "w-full",
        ],
    ).insert(
        title_section,
        content,
        info_pane,
        interaction_pane,
        settings_pane,
    )
