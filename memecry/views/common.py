import textwrap
from pathlib import Path
from typing import Callable, Protocol

from relax.html import (
    Tag,
    a,
    body,
    button,
    div,
    form,
    head,
    html,
    i,
    img,
    video,
    input,
    li,
    link,
    main,
    meta,
    nav,
    p,
    path,
    script,
    span,
    svg,
    title,
    ul,
)
from relax.injection import Injected, injectable_sync

from memecry.config import Config
from memecry.schema import PostRead, UserRead

IMAGE_FORMATS = [".jpg", ".png"]
VIDEO_FORMATS = [".mp4"]


class PostUpdateTagsUrl(Protocol):
    def __call__(self, *, post_id: int) -> str:
        ...


class PostUrlCallable(Protocol):
    def __call__(self, *, post_id: int) -> str:
        ...


def hamburger_svg() -> svg:
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


def page_head() -> head:
    return head().insert(
        title("Memecry"),
        meta(charset="UTF-8"),
        meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        # TODO: only use this in dev
        script(src="https://cdn.tailwindcss.com"),
        link(href="/static/css/tailwind.css", rel="stylesheet"),
        link(
            href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css",
            rel="stylesheet",
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
    )


def page_root(child: Tag | list[Tag]) -> html:
    return html(lang="en").insert(
        page_head(),
        body(classes=["bg-black", "text-white", "pt-20"]).insert(
            child,  # type: ignore[arg-type]
        ),
    )


# TODO: think of a way to group urls in a single variable
def page_nav(
    signup_url: Callable[[], str],
    signin_url: Callable[[], str],
    signout_url: Callable[[], str],
    upload_form_url: Callable[[], str],
    user: UserRead | None = None,
) -> nav:
    search_form = form(
        classes=["flex", "flex-row", "items-center", "justify-end"],
        action="/",
    ).insert(
        input(
            id="search",
            name="query",
            type="text",
            classes=["rounded", "mr-4", "text-black"],
        ),
        button(classes=[], hyperscript="on click toggle .hidden on #search").insert(
            i(classes=["fa", "fa-search", "fa-lg"]),
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

    nav_links: list[Tag] = [
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
        classes=[
            "bg-gray-900",
            "shadow-lg",
            "fixed",
            "top-0",
            "left-0",
            "w-full",
            "z-50",
        ],
        attrs={"style": "min-height: 2.5rem;"},
    ).insert(
        div(classes=["px-4"]).insert(
            div(classes=["flex", "justify-evenly"]).insert(
                div(classes=["flex", "w-full", "justify-between"]).insert(
                    # Logo
                    # Primary Navbar items
                    div(
                        classes=["hidden", "md:flex", "items-center", "space-x-1"],
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
                                    ],
                                ).text("Memecry"),
                            ),
                        ),
                        nav_links if user else None,  # type: ignore[arg-type]
                    ),
                    # Secondary Navbar items
                    div(
                        classes=["hidden", "md:flex", "items-center", "space-x-3"],
                    ).insert(
                        search_form,
                        signin_button if not user else None,
                        signup_button if not user else None,
                        upload_button if user else None,
                        signout_button if user else None,
                    ),
                    div(
                        classes=["md:hidden", "flex", "items-center", "ml-auto"],
                    ).insert(
                        button(
                            type="button",
                            classes=["outline-none", "mt-2"],
                            hyperscript="on click toggle .hidden on #menu",
                        ).insert(
                            hamburger_svg(),
                        ),
                    ),
                ),
            ),
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
                    ).text("Memes"),
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
                    ).text("Account"),
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
                    ).text("Library"),
                ),
            ),
        ),
    )


def home_view(
    post_update_tags_url: PostUpdateTagsUrl,
    post_url: PostUrlCallable,
    update_searchable_content_url: PostUrlCallable,
    posts: list[PostRead],
) -> Tag:
    return posts_wrapper(
        [
            post_component(
                post_update_tags_url,
                post_url,
                update_searchable_content_url,
                post,
            )
            for post in posts
        ],
    )


@injectable_sync
def tags_component(  # noqa: PLR0913
    post_update_tags_url: PostUpdateTagsUrl,
    post_id: int = 0,
    post_tags: str = "no tags",
    *,
    editable: bool = False,
    hidden_dropdown: bool = True,
    config: Config = Injected,
) -> div:
    element_id = f"tags-{post_id}"
    tags_selector_id = f"tags-selector-{post_id}"

    def li_tag(tag: str) -> li:
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
            ),
        )

    return div(id=element_id, classes=["relative"]).insert(
        input(name="tags", type="text", value=post_tags, classes=["hidden"]),
        div(
            classes=[
                "h-10",
                "flex",
                "rounded",
                "items-center",
                "w-full",
            ],
        ).insert(
            button(
                classes=[
                    "border",
                    "border-gray-400",
                    "rounded-md",
                    "px-2",
                    "py-1",
                    "cursor-default" if not editable else "cursor-pointer",
                ],
                hyperscript=f"on click toggle .hidden on #{tags_selector_id}"
                if editable
                else "",
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
                [li_tag(tag) for tag in config.DEFAULT_TAGS],
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
    tags = tags_component(
        post_update_tags_url,
        post.id,
        post.tags,
        editable=post.editable,
    )
    element_id = f"post-{post.id}"
    return div(
        id=element_id,
        classes=[
            "rounded-lg",
            "shadow-xl",
            "w-full",
            "border-2",
            "border-gray-500",
            "md:p-4",
        ],
    ).insert(
        div(
            classes=[
                "flex",
                "flex-row",
                "flex-nowrap",
                "items-center",
                "justify-center",
                "text-black",
                "hover:text-white",
                "duration-300",
            ],
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
        div(
            classes=[
                "flex",
                "flex-row",
                "justify-between",
                "items-center",
                "pt-4",
                "px-4",
                "md:px-0",
            ],
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
                "hidden",
            ],
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
            div(classes=["flex", "flex-row", "justify-end", "space-x-4"]).insert(
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
                    ],
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
                    classes=[
                        "py-2",
                        "px-4",
                        "rounded-lg",
                        "text-white",
                        "font-semibold",
                        "bg-green-600",
                        "hover:bg-green-700",
                        "duration-300",
                    ],
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
        ),
    )


def posts_wrapper(posts: Tag | list[Tag]) -> main:
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
        ],
    ).insert(
        posts,  # type: ignore[arg-type]
    )


def upload_form(
    upload_url: Callable[[], str],
    post_update_tags_url: PostUpdateTagsUrl,
) -> div:
    tags = tags_component(post_update_tags_url, editable=True)
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
            ],
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
        ),
    )


def signin_form(get_signing_url: Callable[[], str]) -> div:
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
        .hx_post(
            get_signing_url(),
            hx_encoding="multipart/form-data",
            hx_target="#signin-error",
        )
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
            button(
                classes=["p-2", "bg-blue-800", "rounded-sm"],
                type="submit",
            ).text("Sign in"),
        ),
        div(id="signin-error"),
    )


def error_element(error: str) -> div:
    return div(classes=["bg-red-800", "my-4", "p-2", "border-lg", "w-max"]).text(error)


def signup_form(get_signup_url: Callable[[], str]) -> div:
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
        .hx_post(
            get_signup_url(),
            hx_encoding="multipart/form-data",
            hx_target="#signup-error",
        )
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
            button(
                classes=["p-2", "bg-blue-800", "rounded-sm"],
                type="submit",
            ).text("Sign up"),
        ),
        div(id="signup-error"),
    )


def response_404() -> Tag:
    return div().text("404 resource not found")
