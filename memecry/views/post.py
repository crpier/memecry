import textwrap
from pathlib import Path
from typing import Protocol

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
    script,
    span,
    ul,
    video,
)
from relax.injection import Injected, injectable_sync
from starlette.datastructures import URL

from memecry.config import ViewContext
from memecry.schema import PostRead
from memecry.views.common import (
    DROPDOWN_CLASSES,
    FLEX_COL_WRAPPER_CLASSES,
    FLEX_ROW_WRAPPER_CLASSES,
    SIMPLE_BUTTON_CLASSES,
    special_button_classes,
)

IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
VIDEO_FORMATS = [".mp4", ".webm"]


class PostUpdateTagsUrl(Protocol):
    def __call__(self, *, post_id: int) -> URL:
        ...


class PostUrlCallable(Protocol):
    def __call__(self, *, post_id: int) -> URL:
        ...


@injectable_sync
def tags_component(  # noqa: PLR0913
    post_update_tags_url: PostUpdateTagsUrl,
    post_id: int = 0,
    post_tags: str = "no-tags",
    *,
    editable: bool = False,
    hidden_dropdown: bool = True,
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
                post_update_tags_url(post_id=post_id),
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
                [li_tag(tag) for tag in context.tags],
            ),
        ),
    )


def edit_hidden_title_script(post: PostRead) -> str:
    return textwrap.dedent(
        f"""
        setTimeout(() => {{
            let editableElement = document.getElementById("title-display-{post.id}")
            editableElement.addEventListener("input", function(event) {{
                console.log(event.target.innerText)
                let targetInput = document.getElementById("title-{post.id}")
                targetInput.value = event.target.innerText
            }})
        }})""",
    )


def edit_hidden_content_script(post: PostRead) -> str:
    return textwrap.dedent(
        f"""
        setTimeout(() => {{
            let editableElement = document.getElementsByName("content-{post.id}")[0]
            editableElement.addEventListener("input", function(event) {{
                let targetInput = document.getElementsByName(
                        "content-input-{post.id}"
                    )[0]
                targetInput.value = event.target.innerText
            }})
        }})""",
    )


def post_component(
    post_update_tags_url: PostUpdateTagsUrl,
    post_url: PostUrlCallable,
    update_searchable_content_url: PostUrlCallable,
    post: PostRead,
) -> div:
    search_content_id = f"search-{post.id}"
    element_id = f"post-{post.id}"

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
    info_pane = div(classes=FLEX_ROW_WRAPPER_CLASSES).insert(
        div(classes=["font-semibold"]).text(f"{post.score} good boi points"),
        div(classes=["space-x-1"]).insert(
            span(classes=["font-semibold"]).text(f"{post.created_since} by"),
            a(href="#", classes=["font-semibold", "text-green-300"]).text(
                post.author_name
            ),
        ),
    )
    tags = tags_component(
        post_update_tags_url,
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
        div(classes=["space-x-2"]).insert(
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
        button(classes=["border", "rounded-md", "py-1", "px-2"]).text("0 comments"),
    )
    settings_pane = div(
        classes=[*FLEX_COL_WRAPPER_CLASSES, "hidden"],
        id=search_content_id,
    ).insert(
        input(name=f"content-input-{post.id}", type="text", classes=["hidden"]),
        script(
            js=edit_hidden_content_script(post),
        ),
        div(
            classes=[
                "block",
                "p-2",
                "w-full",
                "my-4",
                "bg-black",
                "outline-none",
            ],
            attrs={
                "contenteditable": "true" if post.editable else "false",
                "name": f"content-{post.id}",
            },
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
                post_url(post_id=post.id),
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
            "rounded-lg",
            "w-full",
            "border-2",
            "border-gray-500",
            "p-4",
            "post-component",
        ],
    ).insert(
        div(
            classes=FLEX_ROW_WRAPPER_CLASSES,
        ).insert(
            input(
                id=f"title-{post.id}",
                classes=["hidden"],
                type="text",
                name=f"title-{post.id}",
                value=post.title,
            ),
            div(classes=["flex-1"]).text(""),
            span(
                id=f"title-display-{post.id}",
                classes=["text-white", "text-2xl", "font-bold", "mb-4", "px-2"],
                attrs={
                    "contenteditable": "true" if post.editable else "false",
                    "spellcheck": "false",
                },
            ).text(post.title),
            script(
                js=edit_hidden_title_script(post),
            ),
            div(
                classes=[
                    "flex-1",
                    "mx-auto",
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
        ),
        content,
        info_pane,
        interaction_pane,
        settings_pane,
    )
