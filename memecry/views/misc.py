import contextlib
from typing import Protocol

from relax.html import (
    Element,
    Fragment,
    Tag,
    a,
    body,
    button,
    div,
    form,
    head,
    html,
    i,
    input,
    link,
    main,
    meta,
    nav,
    p,
    script,
    span,
    title,
)
from relax.injection import Injected, injectable_sync
from starlette.datastructures import URL

import memecry.config
import memecry.schema
import memecry.views.post
from memecry.views.common import (
    BASIC_FORM_CLASSES,
    FLEX_COL_WRAPPER_CLASSES,
    FLEX_ROW_WRAPPER_CLASSES,
    MODAL_UNDERLAY,
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
def tailwind_css(*, context: memecry.config.ViewContext = Injected) -> Element:
    return (
        link(href="/static/css/tailwind.css", rel="stylesheet")
        if context.prod
        else script(src="https://cdn.tailwindcss.com")
    )


def page_head() -> head:
    return head().insert(
        title("Memecry"),
        meta(charset="UTF-8"),
        meta(
            name="viewport",
            content="width=device-width; initial-scale=1.0; maximum-scale=1.0;",
        ),
        tailwind_css(),
        link(href="/static/css/global.css", rel="stylesheet"),
        link(
            href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css",
            rel="stylesheet",
        ),
        script(src="/static/js/key_handler.js", attrs={"defer": "true"}),
        script(
            src="https://unpkg.com/htmx.org@1.9.5",
            attrs={
                "integrity": "sha384-xcuj3WpfgjlKF+FXhSQF"
                "Q0ZNr39ln+hwjN3npfM9VBnUskLolQAcN80McRIVOPuO",
                "crossorigin": "anonymous",
            },
        ),
        script(src="https://unpkg.com/hyperscript.org@0.9.11"),
        script(src="https://cdn.jsdelivr.net/npm/sweetalert2@11"),
    )


def page_root(child: Element | list[Element]) -> html:
    return html(lang="en").insert(
        page_head(),
        body(classes=["bg-black", "text-white", "pt-20"]).insert(
            child,
        ),
    )


def page_nav(
    signup_url: URL,
    signin_url: URL,
    signout_url: URL,
    upload_form_url: URL,
    user: memecry.schema.UserRead | None = None,
) -> nav:
    search_form = (
        form(
            classes=[*FLEX_ROW_WRAPPER_CLASSES],
        )
        .insert(
            div(id="search-error"),
            input(
                id="search",
                name="query",
                type="text",
                classes=[
                    "rounded",
                    "px-1",
                    "md:mr-4",
                    "text-black",
                ],
            ),
            button(
                classes=["hidden", "md:block"],
                hyperscript="on click toggle .hidden on #search",
            ).insert(
                i(classes=["fa", "fa-search", "fa-lg"]),
            ),
            # TODO: get url as param
        )
        .hx_get("/search", hx_target="#search-error")
    )

    signup_button = (
        button(
            classes=[*special_button_classes("green")],
        )
        .hx_get(target=signup_url, hx_target="body", hx_swap="beforeend")
        .text("Sign up")
    )

    signin_button = (
        button(
            classes=[*SIMPLE_BUTTON_CLASSES, "border-0"],
        )
        .hx_get(target=signin_url, hx_target="body", hx_swap="beforeend")
        .text("Sign in")
    )

    upload_button = (
        button(
            classes=[*special_button_classes("green"), "mr-1"],
        )
        .hx_get(target=upload_form_url, hx_target="body", hx_swap="beforeend")
        .text("Upload")
    )

    signout_button = (
        button(
            classes=[*SIMPLE_BUTTON_CLASSES, "border-0"],
        )
        .hx_get(target=signout_url, hx_target="body", hx_swap="beforeend")
        .text("Sign out")
    )

    return nav(
        classes=["bg-gray-900", "fixed", "top-0", "left-0", "w-full"],
    ).insert(
        div(classes=["flex", "w-full", "justify-end", "md:justify-between"]).insert(
            # Logo
            # Primary Navbar items
            a(
                href="/",
                classes=["hidden", "md:block", "items-center", "md:px-2", "md:py-2"],
            ).insert(
                span(
                    classes=[
                        "font-bold",
                        "text-2xl",
                        "md:hover:text-green-500",
                    ],
                ).text("Memecry"),
            ),
            # Secondary Navbar items
            div(
                classes=[*FLEX_ROW_WRAPPER_CLASSES],
            ).insert(
                search_form,
                signin_button if not user else None,
                signup_button if not user else None,
                signout_button if user else None,
                upload_button if user else None,
            ),
        ),
    )


def home_view(  # noqa: PLR0913
    post_update_tags_url: PostUpdateTagsUrl,
    post_url: PostUrlCallable,
    update_searchable_content_url: PostUrlCallable,
    posts: list[memecry.schema.PostRead],
    offset: int = 0,
    limit: int = 5,
    *,
    keep_scrolling: bool = False,
    partial: bool = False,
) -> Tag:
    post_views = [
        memecry.views.post.post_component(
            post_update_tags_url,
            post_url,
            update_searchable_content_url,
            post,
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
        classes=[*FLEX_COL_WRAPPER_CLASSES, "md:max-w-xl", "mx-auto"],
    ).insert(
        post_views,
    )


def upload_form(
    upload_url: URL,
    post_update_tags_url: PostUpdateTagsUrl,
) -> div:
    tags = memecry.views.post.tags_component(post_update_tags_url, editable=True)
    return div(
        id="upload-form",
        classes=[*FLEX_COL_WRAPPER_CLASSES, "fixed", "inset-48", "z-40"],
        hyperscript="on closeModal remove me",
    ).insert(
        MODAL_UNDERLAY,
        form(
            classes=BASIC_FORM_CLASSES,
        )
        .hx_post(
            upload_url,
            hx_swap="afterend",
            hx_encoding="multipart/form-data",
        )
        .insert(
            input(
                type="text",
                name="title",
                placeholder="Title",
                classes=["w-96", "text-black", "px-2"],
            ),
            input(
                type="file",
                name="file",
            ),
            tags,
            div(classes=["w-full", "flex", "flex-col", "items-end"]).insert(
                button(
                    type="submit",
                    classes=special_button_classes("green"),
                ).text("Upload"),
            ),
        ),
    )


def signin_form(signin_url: URL) -> div:
    return div(
        classes=[*FLEX_COL_WRAPPER_CLASSES, "fixed", "inset-48", "z-40"],
        hyperscript="on closeModal remove me",
    ).insert(
        MODAL_UNDERLAY,
        form(
            classes=BASIC_FORM_CLASSES,
        )
        .hx_post(
            signin_url,
            hx_encoding="multipart/form-data",
            hx_target="#signin-error",
        )
        .insert(
            p(classes=["text-2xl"]).text("Sign in"),
            div(
                classes=[
                    *FLEX_COL_WRAPPER_CLASSES,
                    "max-h-24",
                    "w-full",
                ],
            ).insert(
                input(
                    type="text",
                    name="username",
                    placeholder="username",
                    classes=["p-1", "rounded-sm", "text-black", "w-full"],
                ),
                input(
                    type="password",
                    name="password",
                    placeholder="password",
                    classes=["p-1", "rounded-sm", "text-black", "w-full"],
                ),
            ),
            button(
                classes=special_button_classes("green"),
                type="submit",
            ).text("Sign in"),
        ),
        div(id="signin-error"),
    )


def signup_form(signup_url: URL) -> div:
    return div(
        classes=[*FLEX_COL_WRAPPER_CLASSES, "fixed", "inset-48", "z-40"],
        hyperscript="on closeModal remove me",
    ).insert(
        MODAL_UNDERLAY,
        form(
            classes=BASIC_FORM_CLASSES,
        )
        .hx_post(
            signup_url,
            hx_encoding="multipart/form-data",
            hx_target="#signup-error",
        )
        .insert(
            p(classes=["text-xl"]).text("Sign up"),
            div(
                classes=[
                    *FLEX_COL_WRAPPER_CLASSES,
                    "h-screen",
                    "max-h-24",
                    "w-full",
                ],
            ).insert(
                input(
                    type="text",
                    name="username",
                    placeholder="username",
                    classes=["p-1", "rounded-sm", "text-black", "w-full"],
                ),
                input(
                    type="password",
                    name="password",
                    placeholder="password",
                    classes=["p-1", "rounded-sm", "text-black", "w-full"],
                ),
            ),
            button(
                classes=special_button_classes("green"),
                type="submit",
            ).text("Sign up"),
        ),
        div(id="signup-error"),
    )
