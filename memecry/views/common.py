from typing import Callable, Protocol

from yahgl_py.html import (
    div,
    input,
    form,
    img,
    button,
    nav,
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
    return nav().insert(
        p().text(f"Hello, {username}!"),
        button(
            id="signup",
            type="button",
        )
        .hx_get(signup_url(), hx_target="body", hx_swap="beforeend")
        .text("Sign up"),
    )


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
