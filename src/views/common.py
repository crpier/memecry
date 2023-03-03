from simple_html.attributes import str_attr
from simple_html.nodes import (
    TagBase,
    Tag,
    body,
    head,
    html,
    div,
    meta,
    title,
    link,
    script,
    nav,
    a,
    span,
    i,
    button,
    img,
    main,
    p,
    form,
    label,
    script,
    FlatGroup,
)
from simple_html.render import render

from src import schema

_class = str_attr("class")
hx_get = str_attr("hx-get")
hx_post = str_attr("hx-post")
hx_put = str_attr("hx-put")
hx_target = str_attr("hx-target")
hx_trigger = str_attr("hx-trigger")
hx_swap = str_attr("hx-swap")
hx_encoding = str_attr("hx-encoding")

input = TagBase("input")
DOCTYPE = TagBase("!DOCTYPE html")


def page_head():
    return head(
        meta.attrs(charset="UTF-8"),
        title("Memecry"),
        link.attrs(
            href="https://unpkg.com/tailwindcss@^2/dist/tailwind.min.css",
            rel="stylesheet",
        ),
        link.attrs(
            href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css",
            rel="stylesheet",
        ),
        script.attrs(src="/static/js/htmx.min.js?v=1.5.0"),
        script.attrs(src="/static/js/close_modals.js"),
        script(
            """
           """
        ),
    )


def page_nav(user: schema.User | None):
    nav_container = nav.attrs(
        _class("flex flex-row items-center justify-start bg-gray-900 p-3 fixed w-full h-14")
    )
    app_logo = a.attrs(_class("mr-6 flex flex-shrink-0 items-center"), href="/")(
        span.attrs(_class("text-xl font-semibold tracking-tight"))("Memecry")
    )
    new_link = a.attrs(
        _class("mr-4 block hover:text-gray-300 lg:mt-0 lg:inline-block"),
        href="/new",
    )("New")
    search_button = button(i.attrs(_class("fa fa-search fa-lg h-6 mr-4")))
    signup_button = button.attrs(
        _class(
            "mr-4 inline-block rounded border border-white px-4 py-2 text-sm leading-none "
            "hover:border-transparent hover:bg-white hover:text-teal-500"
        ),
        hx_get("/signup-form"),
        hx_target("#signup-modal"),
    )("Sign up")
    signin_button = button.attrs(
        _class(
            "mr-4 inline-block rounded border border-white px-4 py-2 text-sm leading-none "
            "hover:border-transparent hover:bg-white hover:text-teal-500"
        ),
        hx_get("/login-form"),
        hx_target("#login-modal"),
    )("Sign in")
    upload_button = button.attrs(
        _class(
            "mr-4 inline-block rounded border-white bg-blue-500 px-4 py-2 text-sm "
            "font-semibold leading-none "
            "hover:border-transparent hover:bg-white hover:text-teal-500 "
        ),
        hx_get("/upload-form"),
        hx_target("#upload-modal"),
    )("Upload")
    profile_section = (
        a.attrs(
            _class(
                "flex flex-row items-center pr-2 hover:bg-gray-800 hover:text-white mr-2"
            ),
            href="#responsive-header",
        )(
            button.attrs(_class("h-12 w-12"))(
                img.attrs(
                    _class("m-auto w-8 h-8 rounded-md"),
                    alt="profile-picture",
                    src="https://avatars.githubusercontent.com/u/31815875?v=4",
                )
            ),
            span(user.username),  # type: ignore
        )
        if user
        else None
    )
    signout_button = button.attrs(
        _class(
            "inline-block rounded border border-white p-1 mr-2 text-md leading-none"
            "hover:border-transparent hover:bg-white hover:text-teal-500"
        ),
        hx_post("/logout"),
    )("Sign out")
    return FlatGroup(
        nav_container(
            app_logo,
            new_link,
            div.attrs(_class("flex-grow")),
            search_button,
            signup_button if not user else None,
            signin_button if not user else None,
            upload_button if user else None,
            profile_section if user else None,
            signout_button if user else None,
        ),
        div.attrs(id="upload-modal"),
        div.attrs(id="login-modal"),
        div.attrs(id="signup-modal"),
    )


def page_root(user: schema.User | None, partial: Tag | None = None):
    return FlatGroup(
        DOCTYPE,
        html.attrs(lang="en")(
            page_head(),
            body.attrs(_class("bg-black text-white h-screen"))(
                page_nav(user),
                div.attrs(
                    _class(
                        "flex flex-grow-0 flex-row items-start justify-center justify-center"
                    )
                )(
                    main.attrs(
                        _class(
                            "m-16 flex flex-col items-center justify-center justify-items-center"
                        )
                    )(partial)
                ),
            ),
        ),
    )


def login_form():
    return div.attrs(
        _class("fixed flex flex-col rounded border bg-gray-700 px-4 pb-2"),
        style="left:35vw;top:20vh;width:30vw",
    )(
        div.attrs(_class("mt-2 flex justify-end items-end"))(
            button.attrs(
                _class(
                    "w-max rounded border border bg-gray-900 px-2 text-right hover:bg-gray-700"
                ),
                onclick="closeLoginModal()",
            )("X"),
        ),
        p.attrs(_class("mb-1 text-center text-2xl"))("Login"),
        form.attrs(
            hx_encoding("multipart/form-data"), hx_post("/token"), id="upload-form"
        )(
            div.attrs(_class("mb-4"))(
                label.attrs(("for", "username"))("Username"),
                input.attrs(
                    _class("w-full rounded border p-1"),
                    name="username",
                ),
            ),
            div.attrs(_class("mb-4"))(
                label.attrs(("for", "password"))("Password"),
                input.attrs(
                    _class("w-full rounded border p-1"),
                    name="password",
                    type="password",
                ),
            ),
            div.attrs(_class("m-auto flex flex-col justify-center items-center"))(
                button.attrs(
                    _class(
                        "m-auto rounded border border bg-gray-900 px-2 py-1 text-right hover:bg-gray-700"
                    ),
                    type="submit",
                )("Sign in")
            ),
        ),
    )


def signup_form():
    return div.attrs(
        _class("fixed flex flex-col rounded border bg-gray-700 px-4 pb-4"),
        style="left:35vw;top:20vh;width:30vw",
    )(
        div.attrs(_class("mt-2 flex justify-end items-end"))(
            button.attrs(
                _class(
                    "w-max rounded border border bg-gray-900 px-2 text-right hover:bg-gray-700"
                ),
                onclick="closeSignupModal()",
            )("X"),
        ),
        p.attrs(_class("mb-1 text-center text-2xl"))("Signup"),
        form.attrs(
            hx_encoding("multipart/form-data"), hx_post("/signup"), id="upload-form"
        )(
            div.attrs(_class("mb-4"))(
                label.attrs(("for", "username"))("Username"),
                input.attrs(
                    _class("w-full rounded border p-1"),
                    name="username",
                ),
            ),
            div.attrs(_class("mb-4"))(
                label.attrs(("for", "email"))("Email"),
                input.attrs(
                    _class("w-full rounded border p-1"),
                    name="email",
                ),
            ),
            div.attrs(_class("mb-4"))(
                label.attrs(("for", "password"))("Password"),
                input.attrs(
                    _class("w-full rounded border p-1"),
                    name="password",
                    type="password",
                ),
            ),
            div.attrs(_class("m-auto flex flex-col justify-center items-center"))(
                button.attrs(
                    _class(
                        "m-auto rounded border border bg-gray-900 px-2 py-1 text-right hover:bg-gray-700"
                    ),
                    type="submit",
                )("Sign up")
            ),
        ),
    )


def post_upload_form():
    return div.attrs(
        _class("fixed flex flex-col rounded border bg-gray-700 px-4 pb-4"),
        style="left:20vw;top:10vh;width:60vw",
    )(
        div.attrs(_class("mt-2 flex justify-end items-end"))(
            button.attrs(
                _class(
                    "w-max rounded border border bg-gray-900 px-2 text-right hover:bg-gray-700"
                ),
                onclick="closeUploadModal()",
            )("X"),
        ),
        p.attrs(_class("mb-1 text-center text-2xl"))("Upload"),
        form.attrs(
            hx_encoding("multipart/form-data"), hx_post("/upload"), id="upload-form"
        )(
            div.attrs(_class("mb-4"))(
                label.attrs(("for", "title"))("Title"),
                input.attrs(
                    _class("w-full rounded border p-1"),
                    name="title",
                ),
            ),
            input.attrs(type="file", name="file"),
            div.attrs(_class("flex flex-row justify-start"))(
                button.attrs(
                    _class(
                        "mt-4 rounded border border-white px-4 py-1 text-sm font-semibold hover:border-transparent hover:bg-white hover:text-teal-500"
                    )
                )("Cancel"),
                button.attrs(
                    _class(
                        "mt-4 ml-4 rounded border-white bg-blue-500 px-4 py-1 text-sm font-semibold hover:border-transparent hover:bg-white hover:text-teal-500"
                    ),
                    type="submit",
                )("Submit"),
            ),
        ),
    )
