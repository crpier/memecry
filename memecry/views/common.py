from typing import Callable, Protocol

from yahgl_py.html import (
    div,
    select,
    option,
    label,
    main,
    input,
    form,
    path,
    ul,
    i,
    img,
    button,
    li,
    nav,
    svg,
    span,
    a,
    title,
    meta,
    script,
    link,
    head,
    html,
    body,
    Tag,
    p,
)


def hamburger_svg():
    return svg(
        classes=["h-6", "w-6", "text-gray-500"],
        attrs={
            "x-show": "!showMenu",
            "fill": "none",
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
            "stroke-width": "2",
            "viewBox": "0 0 24 24",
            "stroke": "currentColor",
        },
    ).insert(path(attrs={"d": "M4 6h16M4 12h16M4 18h16"}))


def page_head():
    return head().insert(
        title("Memecry"),
        meta(charset="UTF-8"),
        meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        # TODO: use pytailwindcss instead
        script(src="https://cdn.tailwindcss.com"),
        script(src="https://unpkg.com/tailwindcss-jit-cdn"),
        link(
            href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css",
            rel="stylesheet",
        ),
        script(
            src="https://unpkg.com/htmx.org@1.9.5",
            attrs=dict(
                integrity="sha384-xcuj3WpfgjlKF+FXhSQFQ0ZNr39ln+hwjN3npfM9VBnUskLolQAcN80McRIVOPuO",
                crossorigin="anonymous",
            ),
        ),
        script(src="https://unpkg.com/hyperscript.org@0.9.11"),
    )


def page_root(child: Tag | list[Tag]):
    return html(lang="en").insert(
        page_head(),
        body(classes=["bg-black", "text-white", "pt-20"]).insert(
            child,
        ),
    )


def page_nav(
    signup_url: Callable[[], str],
    login_url: Callable[[], str],
    username: str | None = None,
):
    search_form = form(
        classes=["flex", "flex-row", "items-center", "justify-end"]
    ).insert(
        input(
            id="search",
            name="search",
            type="text",
            classes=["rounded", "mr-4", "text-black", "hidden"],
        ),
        button(classes=[], hyperscript="on click toggle .hidden on #search").insert(
            i(classes=["fa", "fa-search", "fa-lg"])
        ),
    )
    return nav(
        classes=["bg-gray-900", "shadow-lg", "fixed", "top-0", "left-0", "w-full"]
    ).insert(
        div(classes=["px-4"]).insert(
            div(classes=["flex", "justify-evenly"]).insert(
                div(classes=["flex", "w-full", "justify-between"]).insert(
                    # Logo
                    # Primary Navbar items
                    div(
                        classes=["hidden", "md:flex", "items-center", "space-x-1"]
                    ).insert(
                        div().insert(
                            a(
                                href="#",
                                classes=["flex", "items-center", "py-4", "px-2"],
                            ).insert(
                                span(
                                    classes=[
                                        "font-semibold",
                                        "text-xl",
                                        "md:hover:text-green-500",
                                        "duration-300",
                                    ]
                                ).text("Memecry"),
                            )
                        ),
                        a(
                            href="#",
                            classes=[
                                "py-4",
                                "px-2",
                                "hover:text-green-500",
                                "duration-300",
                                "font-semibold",
                            ],
                        ).text("Memes"),
                        a(
                            href="#",
                            classes=[
                                "py-4",
                                "px-2",
                                "font-semibold",
                                "hover:text-green-500",
                                "duration-300",
                            ],
                        ).text("Account"),
                        a(
                            href="#",
                            classes=[
                                "py-4",
                                "px-2",
                                "font-semibold",
                                "hover:text-green-500",
                                "duration-300",
                            ],
                        ).text("Library"),
                    ),
                    # Secondary Navbar items
                    div(
                        classes=["hidden", "md:flex", "items-center", "space-x-3"]
                    ).insert(
                        search_form,
                        button(
                            classes=[
                                "py-2",
                                "px-2",
                                "font-medium",
                                "rounded",
                                "hover:bg-green-500",
                                "hover:text-white",
                                "duration-300",
                            ],
                        )
                        .hx_get(
                            target=login_url(), hx_target="body", hx_swap="beforeend"
                        )
                        .text("Login"),
                        button(
                            classes=[
                                "py-2",
                                "px-2",
                                "font-medium",
                                "text-white",
                                "bg-green-500",
                                "rounded",
                                "hover:bg-green-400",
                                "duration-300",
                            ],
                        )
                        .hx_get(
                            target=signup_url(), hx_target="body", hx_swap="beforeend"
                        )
                        .text("Sign up"),
                    ),
                    div(classes=["md:hidden", "flex", "items-center"]).insert(
                        button(
                            type="button",
                            classes=["outline-none"],
                            hyperscript="on click toggle .hidden on #menu",
                        ).insert(
                            hamburger_svg(),
                        )
                    ),
                )
            )
        ),
        # Mobile menu
        div(id="menu", classes=["hidden"]).insert(
            ul().insert(
                li(classes=["text-right"]).insert(
                    a(
                        href="#",
                        classes=[
                            "block",
                            "text-sm",
                            "px-2",
                            "py-4",
                            "font-semibold",
                        ],
                    ).text("Memes")
                ),
                li(classes=["text-right"]).insert(
                    a(
                        href="#",
                        classes=[
                            "block",
                            "text-sm",
                            "px-2",
                            "py-4",
                            "font-semibold",
                        ],
                    ).text("Account")
                ),
                li(classes=["text-right"]).insert(
                    a(
                        href="#",
                        classes=[
                            "block",
                            "text-sm",
                            "px-2",
                            "py-4",
                            "font-semibold",
                        ],
                    ).text("Library")
                ),
            )
        ),
    )


def home_view(post_id: int) -> Tag:
    return posts_wrapper(post_partial_view(post_id))


def tags_component(post_id: int):
    tags_selector_id = f"tags-selector-{post_id}"
    return div(classes=["relative"]).insert(
        div(classes=["h-10", "flex", "rounded", "items-center", "w-full",]).insert(
            button(
                id="select",
                classes=["border", "rounded-md", "px-2", "py-1"],
                hyperscript=f"on click toggle .hidden on #{tags_selector_id}",
            ).text("shitpost, animals"),
        ),
        div(
            id=tags_selector_id,
            classes=[
                "absolute",
                "rounded",
                "shadow",
                "overflow-hidden",
                "hidden",
                "flex-col",
                "w-full",
                "mt-1",
                "border",
                "border-gray-200",
                "bg-black",
            ],
        ).insert(
            ul().insert(
                li(
                    classes=[
                        "px-2",
                        "py-1",
                        "bg-gray-800",
                        "hover:bg-gray-900",
                        "cursor-pointer",
                    ]
                ).text("shitpost"),
                li(
                    classes=[
                        "px-2",
                        "py-1",
                        "hover:bg-gray-900",
                        "cursor-pointer",
                    ]
                ).text("meirl"),
                li(
                    classes=[
                        "px-2",
                        "py-1",
                        "bg-gray-800",
                        "hover:bg-gray-900",
                        "cursor-pointer",
                    ]
                ).text("animals"),
                li(
                    classes=[
                        "px-2",
                        "py-1",
                        "hover:bg-gray-900",
                        "cursor-pointer",
                    ]
                ).text("reaction"),
            ),
        ),
    )


def post_partial_view(post_id: int):
    search_content_id = f"search-content-{post_id}"
    return div(
        classes=["rounded-lg", "shadow-xl", "w-full", "border-2", "md:p-4"]
    ).insert(
        p(classes=["text-2xl", "font-extrabold", "pb-4", "text-center"]).text(
            "Some funny title"
        ),
        img(
            src="https://avatars.githubusercontent.com/u/31815875?v=4",
            alt="some funny picture",
            classes=["w-full"],
        ),
        div(
            classes=[
                "flex",
                "flex-row",
                "justify-between",
                "items-center",
                "pt-4",
                "px-4",
                "md:px-0",
            ]
        ).insert(
            tags_component(post_id),
            div(classes=["space-x-2", "text-right", "py-3", "text-gray-500"]).insert(
                button(
                    type="button",
                    classes=[
                        "py-2",
                        "px-4",
                        "bg-green-500",
                        "rounded-lg",
                        "text-white",
                        "font-semibold",
                        "hover:bg-green-600",
                        "duration-300",
                    ],
                    hyperscript=f"on click toggle .hidden on #{search_content_id}",
                ).insert(i(classes=["fa", "fa-info", "fa-lg"])),
            ),
        ),
        div(
            classes=["border-t", "pt-2", "px-2", "mt-4", "hidden"],
            attrs={"contenteditable": "true"},
            id=search_content_id,
        ).text(
            "One morning, when Gregor Samsa woke from troubled dreams, he found himself transformed in his bed into a horrible vermin. He lay on his armour-like back, and if he lifted his head a little he could see his brown belly, slightly domed and divided by arches into stiff sections."
        ),
    )


def posts_wrapper(posts: Tag | list[Tag]):
    return main(
        classes=[
            "flex",
            "flex-col",
            "items-center",
            "justify-center",
            "justify-items-center",
            "w-full",
            "lg: max-w-2xl",
            "mx-auto",
        ]
    ).insert(posts)


class PostUrlCallable(Protocol):
    def __call__(self, *, post_id: int) -> str:
        ...


def signup_form(get_signup_url: Callable[[], str]):
    return div(
        classes=[
            "fixed",
            "inset-48",
            "z-40",
            "flex",
            "flex-col",
            "items-center",
        ],
        hyperscript="on closeModal remove me",
    ).insert(
        div(
            id="underlay",
            classes=[
                "fixed",
                "inset-0",
                "w-screen",
                "-z-10",
                "bg-black",
                "bg-opacity-50",
            ],
            hyperscript="on click trigger closeModal",
        ),
        form(
            classes=[
                "z-50",
                "bg-gray-800",
                "p-2",
                "rounded-sm",
                "flex",
                "flex-col",
                "space-y-2",
                "items-center",
                "w-96",
            ],
        )
        .hx_post(get_signup_url(), hx_encoding="multipart/form-data")
        .insert(
            button(
                classes=["px-2", "bg-red-800", "ml-auto", "mr-2", "rounded-sm"],
                hyperscript="on click trigger closeModal",
                type="button",
            ).text("X"),
            p(classes=["text-2xl"]).text("Sign up"),
            div(
                classes=[
                    "flex",
                    "flex-col",
                    "items-center",
                    "justify-between",
                    "h-screen",
                    "max-h-24",
                    "p-2",
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
            # TODO: enum for button types
            button(
                classes=["p-2", "bg-blue-800", "rounded-sm"],
                type="submit",
            ).text("Sign up"),
        ),
    )
