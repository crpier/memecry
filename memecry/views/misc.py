from relax.app import ViewContext
from relax.html import (
    Element,
    a,
    aside,
    body,
    button,
    div,
    form,
    head,
    hmr_scripts,
    html,
    i,
    input,
    link,
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
import memecry.routes.post
import memecry.schema
import memecry.views.common
import memecry.views.post

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
        link(
            rel="stylesheet",
            href="https://cdn.jsdelivr.net/npm/toastify-js/src/toastify.min.css",
        ),
        script(src="/static/js/key_handler.js", type="module", defer=True),
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


@injectable_sync
def page_root(
    child: Element | list[Element],
    *,
    config: memecry.config.Config = Injected,
) -> html:
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
        ).insert(child, hmr_scripts() if config.ENV == "dev" else None),
    )


@component()
def page_nav(
    user: memecry.schema.UserRead | None = None,
    *,
    context: ViewContext = Injected,
    config: memecry.config.Config = Injected,
) -> nav:
    search_form = form(
        classes=[*memecry.views.common.FLEX_ROW_WRAPPER_CLASSES],
        # TODO: find a way to provide this url and its args from context
        action="/search",
    ).insert(
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
    )

    signin_button = (
        button(
            id="signin",
            classes=[*memecry.views.common.SIMPLE_BUTTON_CLASSES, "border-0"],
        )
        .hx_get(
            target=context.url_of(memecry.routes.auth.signin_form)(),
            hx_target="body",
            hx_swap="beforeend",
        )
        .text("Sign in")
    )

    signup_button = (
        button(
            classes=[*memecry.views.common.special_button_classes("green")],
        )
        .hx_get(
            target=context.url_of(memecry.routes.auth.signup_form)(),
            hx_target="body",
            hx_swap="beforeend",
        )
        .text("Sign up")
    )

    upload_button = (
        button(
            classes=[*memecry.views.common.special_button_classes("green"), "mr-1"],
        )
        .hx_get(
            target=context.url_of(memecry.routes.post.upload_form)(),
            hx_target="body",
            hx_swap="beforeend",
        )
        .text("Upload")
    )

    signout_button = (
        button(
            classes=[*memecry.views.common.SIMPLE_BUTTON_CLASSES, "border-0"],
        )
        .hx_get(
            target=context.url_of(memecry.routes.auth.signout)(),
            hx_target="body",
            hx_swap="beforeend",
        )
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
                a(
                    href=context.url_of(memecry.routes.post.random_post)(),
                    classes=["my-auto", "mx-4"],
                ).text("Random"),
            ),
            # Secondary Navbar items
            div(
                classes=[*memecry.views.common.FLEX_ROW_WRAPPER_CLASSES],
            ).insert(
                search_form,
                signin_button if not user else None,
                signup_button if not user and config.ALLOW_SIGNUPS else None,
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


@component(lambda key: key)
def commands_helper(*, key: str, display_hack: bool = False) -> Element:
    return aside(
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
                    key,
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
                keybind_helper("space", "play/pause video in focused"),
                keybind_helper(",", "skip 1 second of video"),
                keybind_helper(".", "rewind 1 second of video"),
                keybind_helper(">", "increase volume of video"),
                keybind_helper("<", "decrease volume of video"),
                #
                section_separator("Site navigation"),
                keybind_helper("/", "focus search bar"),
                keybind_helper("r", "Go to random post"),
                keybind_helper("a", "open upload"),
                keybind_helper("i", "open signing form"),
                keybind_helper("Q", "sign out"),
                keybind_helper("gu", "go to root of site"),
                keybind_helper("gi", "focus most proeminent input"),
                keybind_helper("esc", "unfocus from input"),
            ),
        ),
    )


@component()
def upload_form(*, context: ViewContext = Injected) -> div:
    tags = memecry.views.post.tags_component(editable=True)
    upload_url = context.url_of(memecry.routes.post.upload)
    return div(
        id="upload-form",
        classes=[
            *memecry.views.common.FLEX_COL_WRAPPER_CLASSES,
            "fixed",
            "inset-48",
            "z-40",
        ],
        hyperscript="on closeModal remove me",
    ).insert(
        memecry.views.common.MODAL_UNDERLAY,
        form(
            classes=memecry.views.common.BASIC_FORM_CLASSES,
        )
        .hx_post(
            upload_url(),  # type: ignore
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
                    classes=memecry.views.common.special_button_classes("green"),
                ).text("Upload"),
            ),
        ),
    )


@component()
def signin_form(*, context: ViewContext = Injected) -> div:
    return div(
        classes=[
            *memecry.views.common.FLEX_COL_WRAPPER_CLASSES,
            "fixed",
            "inset-48",
            "z-40",
        ],
        hyperscript="on closeModal remove me",
    ).insert(
        memecry.views.common.MODAL_UNDERLAY,
        form(
            classes=memecry.views.common.BASIC_FORM_CLASSES,
        )
        .hx_post(
            context.url_of(memecry.routes.auth.signin)(),
            hx_encoding="multipart/form-data",
            hx_target="#signin-error",
        )
        .insert(
            p(classes=["text-2xl"]).text("Sign in"),
            div(
                classes=[
                    *memecry.views.common.FLEX_COL_WRAPPER_CLASSES,
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
                classes=memecry.views.common.special_button_classes("green"),
                type="submit",
            ).text("Sign in"),
        ),
        div(id="signin-error"),
    )


def signup_form(signup_url: URL) -> div:
    return div(
        classes=[
            *memecry.views.common.FLEX_COL_WRAPPER_CLASSES,
            "fixed",
            "inset-48",
            "z-40",
        ],
        hyperscript="on closeModal remove me",
    ).insert(
        memecry.views.common.MODAL_UNDERLAY,
        form(
            classes=memecry.views.common.BASIC_FORM_CLASSES,
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
                    *memecry.views.common.FLEX_COL_WRAPPER_CLASSES,
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
                classes=memecry.views.common.special_button_classes("green"),
                type="submit",
            ).text("Sign up"),
        ),
        div(id="signup-error"),
    )
