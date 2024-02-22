import contextlib

from relax.app import ViewContext
from relax.html import (
    Element,
    Fragment,
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
from relax.injection import Injected, component, injectable_sync
from starlette.datastructures import URL

import memecry.config
import memecry.routes.auth
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


@injectable_sync
def tailwind_css(*, config: memecry.config.Config = Injected) -> Element:
    return (
        link(href="/static/css/tailwind.css", rel="stylesheet")
        if config.ENV == "prod"
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
        # TODO: support the type arg too
        link(
            rel="stylesheet",
            href="https://cdn.jsdelivr.net/npm/toastify-js/src/toastify.min.css",
        ),
        # TODO: add these attrs to args
        script(
            src="/static/js/key_handler.js", attrs={"defer": "true", "type": "module"}
        ),
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
        script(src="https://cdn.jsdelivr.net/npm/toastify-js"),
    )


def page_root(child: Element | list[Element]) -> html:
    return html(lang="en").insert(
        page_head(),
        body(
            classes=[
                "bg-black",
                "text-white",
                "pt-14",
                "flex",
                "flex-row",
                "justify-between",
            ]
        ).insert(
            child,
        ),
    )


# TODO: use urls from context lol
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

    # TODO: implement component that lets you set an id
    signin_button = (
        button(
            id="signin",
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
            div(
                classes=[
                    "flex",
                    "flex-row",
                ]
            ).insert(
                a(
                    href="/",
                    classes=[
                        "hidden",
                        "md:block",
                        "items-center",
                        "md:px-2",
                        "md:py-2",
                    ],
                ).insert(
                    span(
                        classes=[
                            "font-bold",
                            "text-2xl",
                            "md:hover:text-green-500",
                        ],
                    ).text("Memecry"),
                ),
                # TODO: get url from context
                a(href="/random", classes=["my-auto", "mx-4"]).text("Random"),
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


def keybind_helper(keybind: str, explanation: str) -> Element:
    return div(classes=["space-x-2", "px-4", "text-left", "text-sm", "ml-4"]).insert(
        span(classes=["font-bold"], text=keybind),
        span(text="-"),
        span(text=explanation),
    )


def section_separator(name: str) -> Element:
    return div(
        classes=["space-x-2", "px-4", "text-left", "text-sm", "font-semibold", "mt-4"],
        text=name,
    )


# TODO: I might want this to move with the scroll element
def commands_helper(*, display_hack: bool = False) -> Element:
    # TODO: would be nice to use aside instead of div
    return div(
        classes=[
            "hidden",
            "md:block",
            "px-8",
            "max-h-full",
            "text-white",
            "md:max-w-lg",
            "invisible" if display_hack is True else "",
        ]
    ).insert(
        div(
            classes=[
                "block",
                "rounded-lg",
                "text-center",
                "bg-black",
                "border",
                "border-gray-600",
                "text-white",
            ]
        ).insert(
            div(
                classes=[
                    "border-b",
                    "border-gray-600",
                    "px-6",
                    "py-3",
                ]
            ).text("Keybindings"),
            div(classes=["pb-4"]).insert(
                section_separator("Movement"),
                keybind_helper("j", "focus on next post"),
                keybind_helper("k", "focus on previous post"),
                keybind_helper("u", "focus on the next 5th post"),
                keybind_helper("d", "focus on the previous 5th post"),
                keybind_helper("gg", "focus on first post"),
                keybind_helper("G", "focus last loaded post"),
                #
                section_separator("Post actions"),
                keybind_helper("za", "open settings pane in post"),
                keybind_helper("zc", "close settings pane in post"),
                keybind_helper(
                    "y",
                    "yank image file in focused post "
                    "(but your browser might not support it)",
                ),
                keybind_helper("gy", "yank url to post media"),
                #
                section_separator("Video posts"),
                keybind_helper("space", "play/pause video in focused post"),
                keybind_helper(",", "skip 1 second of video in focused post"),
                keybind_helper(".", "rewind 1 second of video in focused post"),
                keybind_helper(">", "increase volume of video in focused post"),
                keybind_helper("<", "decrease volume of video in focused post"),
                #
                section_separator("Site navigation"),
                keybind_helper("/", "focus search bar"),
                keybind_helper("r", "Go to random post"),
                keybind_helper("a", "open upload"),
                keybind_helper("i", "open signing form"),
                keybind_helper("gu", "go to root of site"),
                keybind_helper("gi", "focus most proeminent input"),
                keybind_helper("esc", "unfocus from input"),
            ),
        ),
    )


# TODO: move this to posts route
def home_view(
    posts: list[memecry.schema.PostRead],
    offset: int = 0,
    limit: int = 5,
    *,
    keep_scrolling: bool = False,
    partial: bool = False,
) -> Element:
    post_views = [
        memecry.views.post.post_component(
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
        classes=[*FLEX_COL_WRAPPER_CLASSES, "md:w-[32rem]", "mx-auto"],
    ).insert(
        post_views,
    )


# TODO: get url from context
def upload_form(upload_url: URL) -> div:
    tags = memecry.views.post.tags_component(editable=True)
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


@component()
def signin_form(*, context: ViewContext = Injected) -> div:
    return div(
        classes=[*FLEX_COL_WRAPPER_CLASSES, "fixed", "inset-48", "z-40"],
        hyperscript="on closeModal remove me",
    ).insert(
        MODAL_UNDERLAY,
        form(
            classes=BASIC_FORM_CLASSES,
        )
        .hx_post(
            context.endpoint(memecry.routes.auth.SigninSig)(),
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
