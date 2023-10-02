from typing import Callable, Protocol

from yahgl_py.html import (
    div,
    main,
    input,
    form,
    textarea,
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

DEFAULT_TAGS = ["reaction", "animals", "postironic", "romemes", "meirl"]


class PostUpdateTagsUrl(Protocol):
    def __call__(self, *, post_id: int) -> str:
        ...


class PostUrlCallable(Protocol):
    def __call__(self, *, post_id: int) -> str:
        ...


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
                                href="/",
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
                        upload_button if user else None,
                        signout_button if user else None,
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


def home_view(
    post_update_tags_url: PostUpdateTagsUrl,
    post_url: PostUrlCallable,
    posts: list[PostRead],
) -> Tag:
    return posts_wrapper(
        [post_component(post_update_tags_url, post_url, post) for post in posts]
    )


def tags_component(
    post_update_tags_url: PostUpdateTagsUrl,
    post_id: int = 0,
    post_tags: str = "no tags",
    hidden_dropdown: bool = True,
):
    element_id = f"tags-{post_id}"
    tags_selector_id = f"tags-selector-{post_id}"

    def li_tag(tag: str):
        return li().insert(
            button(
                attrs={"name": "tag", "value": tag},
                classes=[
                    "px-2",
                    "py-1",
                    "hover:bg-gray-900",
                    "w-full",
                    "cursor-pointer",
                    "bg-gray-800" if tag in post_tags else "",
                ],
            )
            .text(tag)
            .hx_put(
                post_update_tags_url(post_id=post_id),
                hx_target=f"#{element_id}",
                hx_swap="outerHTML",
            )
        )

    return div(id=element_id, classes=["relative"]).insert(
        input(name="tags", type="text", value=post_tags, classes=["hidden"]),
        div(classes=["h-10", "flex", "rounded", "items-center", "w-full",]).insert(
            button(
                classes=["border", "border-gray-400", "rounded-md", "px-2", "py-1"],
                hyperscript=f"on click toggle .hidden on #{tags_selector_id}",
            ).text(post_tags),
        ),
        div(
            id=tags_selector_id,
            classes=[
                "absolute",
                "rounded",
                "shadow",
                "overflow-hidden",
                "hidden" if hidden_dropdown else "",
                "flex-col",
                "w-max",
                "mt-1",
                "border",
                "border-gray-400",
                "bg-black",
            ],
        ).insert(
            ul().insert(
                [li_tag(tag) for tag in DEFAULT_TAGS],
            ),
        ),
    )


def post_component(
    post_update_tags_url: PostUpdateTagsUrl, post_url: PostUrlCallable, post: PostRead
):
    search_content_id = f"search-content-{post.id}"
    tags = tags_component(post_update_tags_url, post.id, post.tags)
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
        a(href=post_url(post_id=post.id),).insert(
            p(classes=["text-2xl", "font-bold", "pb-4", "text-center", "w-full"]).text(
                post.title
            )
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
            tags,
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
            classes=[
                "border-t",
                "border-gray-500",
                "flex",
                "flex-col",
                "space-y-4",
            ],
            id=search_content_id,
        ).insert(
            textarea(
                id="textarea",
                classes=[
                    "autoExpand",
                    "block",
                    "overflow-hidden",
                    "p-2",
                    "w-full",
                    "mx-auto",
                    "my-4",
                    "bg-black"
                ],
                attrs={"name": f"content-{post.id}", "data-min-rows": 4},
            )
            .hx_put(
                f"/posts/{post.id}/searchable-content",
                hx_trigger="keyup changed delay:1s",
                hx_swap="none",
            )
            .text(post.searchable_content),
            script(
                js="""
                function getScrollHeight(elm){
                    var savedValue = elm.value
                    elm.value = ''
                    elm._baseScrollHeight = elm.scrollHeight
                    elm.value = savedValue
                    }

                document.getElementsByClassName("autoExpand").forEach((elem) => {onExpandableTextareaInput({target: elem})})
                function onExpandableTextareaInput({ target:elm }){
                    // make sure the input event originated from a textarea and it's desired to be auto-expandable
                    if( !elm.classList.contains('autoExpand') || !elm.nodeName == 'TEXTAREA' ) return

                    var minRows = elm.getAttribute('data-min-rows')|0, rows;
                    !elm._baseScrollHeight && getScrollHeight(elm)

                    elm.rows = minRows
                    rows = Math.ceil((elm.scrollHeight - elm._baseScrollHeight) / 16)
                    elm.rows = Math.max(minRows, rows)
                }


                // global delegated event listener
                document.addEventListener('input', onExpandableTextareaInput)
                   """
            ),
            button(
                type="button",
                classes=[
                    "py-2",
                    "px-4",
                    "bg-red-600",
                    "rounded-lg",
                    "text-white",
                    "font-semibold",
                    "hover:bg-red-700",
                    "duration-300",
                    "ml-auto",
                ],
            ).text("Delete post"),
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


def upload_form(upload_url: Callable[[], str], post_update_tags_url: PostUpdateTagsUrl):
    tags = tags_component(post_update_tags_url)
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
                "border-gray-100",
                "rounded-md",
                "flex",
                "flex-col",
                "space-y-4",
                "items-start",
                "w-max",
                "p-4",
            ]
        )
        .hx_post(
            upload_url(),
            hx_swap="afterend",
            hx_encoding="multipart/form-data",
        )
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
            tags,
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


def response_404():
    return div().text("404 resource not found")
