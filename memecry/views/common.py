from typing import Callable

from yahgl_py.html import (
    div,
    select,
    option,
    label,
    progress,
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

from memecry.schema import PostRead, UserRead

DEFAULT_TAGS = ["reaction", "animal", "post-ironic", "ro"]


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
    signin_url: Callable[[], str],
    signout_url: Callable[[], str],
    upload_form_url: Callable[[], str],
    user: UserRead | None = None,
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

    signup_button = (
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
        .hx_get(target=signup_url(), hx_target="body", hx_swap="beforeend")
        .text("Sign up")
    )

    signin_button = (
        button(
            classes=[
                "py-2",
                "px-2",
                "font-medium",
                "rounded",
                "hover:bg-gray-700",
                "duration-300",
            ],
        )
        .hx_get(target=signin_url(), hx_target="body", hx_swap="beforeend")
        .text("Sign in")
    )

    upload_button = (
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
        .hx_get(target=upload_form_url(), hx_target="body", hx_swap="beforeend")
        .text("Upload")
    )

    signout_button = (
        button(
            classes=[
                "py-2",
                "px-2",
                "font-medium",
                "rounded",
                "hover:bg-gray-700",
                "duration-300",
            ],
        )
        .hx_get(target=signout_url(), hx_target="body", hx_swap="beforeend")
        .text("Sign out")
    )

    nav_links = [
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
    ]
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
                        nav_links if user else [],  # type: ignore
                    ),
                    # Secondary Navbar items
                    div(
                        classes=["hidden", "md:flex", "items-center", "space-x-3"]
                    ).insert(
                        search_form,
                        signin_button if not user else None,
                        signup_button if not user else None,
                        signout_button if user else None,
                        upload_button if user else None,
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


def home_view(posts: PostRead) -> Tag:
    return posts_wrapper([post_component(post) for post in posts])


def tags_component(post: PostRead | None = None):
    tags_selector_id = f"tags-selector-{post.id if post else 'sentinel'}"
    return div(classes=["relative"]).insert(
        div(classes=["h-10", "flex", "rounded", "items-center", "w-full",]).insert(
            button(
                id="select",
                classes=["border", "border-gray-400", "rounded-md", "px-2", "py-1"],
                hyperscript=f"on click toggle .hidden on #{tags_selector_id}",
            ).text(post.tags if post else "no tags"),
            input(
                type="text",
                value=post.tags if post else "no tags",
                name=f"tags",
                classes=["hidden"],
            ),
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
                "border-gray-400",
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


def post_component(post: PostRead):
    search_content_id = f"search-content-{post.id}"
    return div(
        classes=[
            "rounded-lg",
            "shadow-xl",
            "w-full",
            "border-2",
            "border-gray-500",
            "md:p-4",
        ]
    ).insert(
        p(classes=["text-2xl", "font-extrabold", "pb-4", "text-center"]).text(
            post.title
        ),
        img(
            src=post.source,
            alt=post.title,
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
            tags_component(post),
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
            classes=["border-t", "border-gray-500", "pt-2", "px-2", "mt-4", "hidden"],
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
            "space-y-8",
        ]
    ).insert(posts)


def upload_form(upload_url: Callable[[], str]):
    return div(
        id="upload-form",
        classes=[
            "fixed",
            "inset-48",
            "z-40",
            "flex",
            "flex-col",
            "items-center",
        ],
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
            hyperscript="on click remove #upload-form",
        ),
        form(
            classes=[
                "z-50",
                "bg-gray-800",
                "border",
                "border-gray-500",
                "rounded-md",
                "flex",
                "flex-col",
                "space-y-4",
                "items-center",
                "w-max",
                "p-4",
            ]
        )
        .hx_post(upload_url(), hx_swap="afterend", hx_encoding="multipart/form-data")
        .insert(
            input(
                type="text",
                name="title",
                placeholder="Title",
                classes=["w-96", "text-black"],
            ),
            input(
                classes=["p-2"],
                type="file",
                name="file",
            ),
            tags_component(),
            button(
                type="submit",
                classes=[
                    "py-2",
                    "px-2",
                    "font-medium",
                    "text-white",
                    "bg-green-600",
                    "rounded",
                    "hover:bg-green-400",
                    "duration-300",
                ],
            ).text("Upload"),
        ),
    )


def signin_form(get_signing_url: Callable[[], str]):
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
        .hx_post(get_signing_url(), hx_encoding="multipart/form-data")
        .insert(
            button(
                classes=["px-2", "bg-red-800", "ml-auto", "mr-2", "rounded-sm"],
                hyperscript="on click trigger closeModal",
                type="button",
            ).text("X"),
            p(classes=["text-2xl"]).text("Sign in"),
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
            ).text("Sign in"),
        ),
    )


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
