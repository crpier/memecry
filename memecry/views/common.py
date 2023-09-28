from typing import Callable, Protocol

from yahgl_py.html import (
    div,
    input,
    form,
    path,
    ul,
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
        meta(name="viewport", content="width=device-width, initial-scale=1"),
        # TODO: use pytailwindcss instead
        script(src="https://cdn.tailwindcss.com"),
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
        body(classes=["bg-black", "text-white"]).insert(
            child,
        ),
    )


def page_nav(signup_url: Callable[[], str], username: str | None = None):
    return nav(classes=["bg-white", "shadow-lg",]).insert(
        div(classes=["max-w-6xl", "mx-auto", "px-4"]).insert(
            div(classes=["flex", "justify-between"]).insert(
                # TODO: checkout space-x-7 in more detail
                div(classes=["flex", "space-x-7"]).insert(
                    # Logo
                    div().insert(
                        a(
                            href="#", classes=["flex", "items-center", "py-4", "px-2"]
                        ).insert(
                            img(
                                src="https://memecry.ceoofmemes.expert/media/123.jpg",
                                alt="Memecry logo",
                                classes=["h-8", "w-8", "mr-2"],
                            ),
                            span(
                                classes=["font-semibold", "text-gray-500", "text-lg"]
                            ).text("Memecry"),
                        )
                    ),
                    # Primary Navbar items
                    div(
                        classes=["hidden", "md:flex", "items-center", "space-x-1"]
                    ).insert(
                        a(
                            href="#",
                            classes=[
                                "py-4",
                                "px-2",
                                "text-green-500",
                                "border-b-4",
                                "border-green-500",
                                "font-semibold",
                            ],
                        ).text("Memes"),
                        a(
                            href="#",
                            classes=[
                                "py-4",
                                "px-2",
                                "text-gray-500",
                                "font-semibold",
                                "hover:text-green-500",
                                "transition",
                                "duration-300",
                            ],
                        ).text("Account"),
                        a(
                            href="#",
                            classes=[
                                "py-4",
                                "px-2",
                                "text-gray-500",
                                "font-semibold",
                                "hover:text-green-500",
                                "transition",
                                "duration-300",
                            ],
                        ).text("Library"),
                    ),
                    # Secondary Navbar items
                    div(
                        classes=["hidden", "md:flex", "items-center", "space-x-3"]
                    ).insert(
                        a(
                            href="#",
                            classes=[
                                "py-2",
                                "px-2",
                                "font-medium",
                                "text-gray-500",
                                "rounded",
                                "hover:bg-green-500",
                                "hover:text-white",
                                "transition",
                                "duration-300",
                            ],
                        ).text("Login"),
                        a(
                            href="#",
                            classes=[
                                "py-2",
                                "px-2",
                                "font-medium",
                                "text-white",
                                "bg-green-500",
                                "rounded",
                                "hover:bg-green-400",
                                "transition",
                                "duration-300",
                            ],
                        ).text("Sign up"),
                    ),
                    div(classes=["md:hidden", "flex", "items-center"]).insert(
                        button(
                            type="button",
                            classes=["mobile-menu-button", "outline-none"],
                        ).insert(
                            hamburger_svg(),
                        )
                    ),
                )
            )
        ),
        # Mobile menu
        div(classes=["hidden", "mobile-menu"]).insert(
            ul().insert(
                li(classes=["active"]).insert(
                    a(
                        href="#",
                        classes=[
                            "block",
                            "text-sm",
                            "px-2",
                            "py-4",
                            "text-white",
                            "bg-green-500",
                            "font-semibold",
                        ],
                    ).text("Memes")
                ),
                li(classes=[""]).insert(
                    a(
                        href="#",
                        classes=[
                            "block",
                            "text-sm",
                            "px-2",
                            "py-4",
                            "text-white",
                            "bg-green-500",
                            "font-semibold",
                        ],
                    ).text("Account")
                ),
                li(classes=[""]).insert(
                    a(
                        href="#",
                        classes=[
                            "block",
                            "text-sm",
                            "px-2",
                            "py-4",
                            "text-white",
                            "bg-green-500",
                            "font-semibold",
                        ],
                    ).text("Library")
                ),
            )
        ),
        script(js="""
               const btn = document.querySelector("button.mobile-menu-button");
               const menu = document.querySelector(".mobile-menu");

               // Add Event Listeners
               btn.addEventListener("click", () => {
                   menu.classList.toggle("hidden");
               });
               """)
    )


# 		<li><a href="#services" class="block text-sm px-2 py-4 hover:bg-green-500 transition duration-300">Services</a></li>
# 		<li><a href="#about" class="block text-sm px-2 py-4 hover:bg-green-500 transition duration-300">About</a></li>
# 		<li><a href="#contact" class="block text-sm px-2 py-4 hover:bg-green-500 transition duration-300">Contact Us</a></li>
# 	</ul>
# </div>


def post_view(post_id: int):
    return div(classes=["p-4", "max-w-3xl"]).insert(
        p(classes=["text-center"]).text("Cool title"),
        img(
            alt="funny meme",
            src="https://memecry.ceoofmemes.expert/media/123.jpg",
        ),
    )


class PostUrlCallable(Protocol):
    def __call__(self, *, post_id: int) -> str:
        ...


def home_view(get_post_url: PostUrlCallable) -> Tag:
    """
    Shows posts in a list
    Requires a function that takes a post id and returns a url to the post
    """
    post_id = 1
    return div().insert(
        button(
            type="button",
            classes=["text-center"],
        )
        .hx_get(get_post_url(post_id=post_id), hx_swap="outerHTML")
        .text("view post"),
    )


def signup_form(get_signup_url: Callable[[], str]):
    return div(
        classes=[
            "fixed",
            "inset-0",
            "bg-black",
            "bg-opacity-50",
            "z-40",
            "flex",
            "flex-col",
            "items-center",
        ],
        hyperscript="on closeModal remove me",
    ).insert(
        div(
            id="underlay",
            classes=["absolute", "inset-0", "-z-10"],
            hyperscript="on click trigger closeModal",
        ),
        form(
            classes=[
                "z-50",
                "max-w-max",
                "bg-gray-800",
                "p-2",
                "rounded-sm",
                "flex",
                "flex-col",
                "items-center",
            ],
        )
        .hx_post(get_signup_url(), hx_encoding="multipart/form-data")
        .insert(
            button(
                classes=["px-2", "bg-red-800", "ml-auto", "mr-2", "rounded-sm"],
                hyperscript="on click trigger closeModal",
                type="button",
            ).text("X"),
            div(
                classes=[
                    "flex",
                    "flex-col",
                    "items-center",
                    "justify-between",
                    "h-screen",
                    "max-h-24",
                    "p-2",
                ],
            ).insert(
                input(
                    type="text",
                    name="username",
                    placeholder="username",
                    classes=["p-1", "rounded-sm", "text-black"],
                ),
                input(
                    type="password",
                    name="password",
                    placeholder="password",
                    classes=["p-1", "rounded-sm", "text-black"],
                ),
            ),
            # TODO: enum for button types
            button(
                classes=["p-2", "bg-blue-800", "rounded-sm"],
                type="submit",
            ).text("Sign up"),
        ),
    )
