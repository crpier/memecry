from typing import Protocol

from yahgl_py.html import (
    InputType,
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
    )


def page_root(child: Tag | list[Tag]):
    return html(lang="en").insert(
        page_head(),
        body(classes=["bg-black", "text-white"]).insert(
            child,
        ),
    )


def page_nav(username: str | None = None):
    return nav().insert(
        p().text(f"Hello, {username}!"),
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
            classes=["text-center"],
            attrs={"hx-get": get_post_url(post_id=post_id), "hx-swap": "outerHTML"},
        ).text("view post"),
    )


def signup_form():
    return form(
        attrs={
            "hx-post": "/signup",
            "hx-encoding": "multipart/form-data",
        },
    ).insert(
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
                type=InputType.text,
                name="username",
                placeholder="username",
                classes=["p-1"],
            ),
            input(
                type=InputType.password,
                name="password",
                placeholder="password",
                classes=["p-1"],
            ),
        ),
        button(
            type="submit",
            ).text("Sign up"),
    )
