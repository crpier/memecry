from simple_html.attributes import str_attr
from simple_html.nodes import (
    TagBase,
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
)
from simple_html.render import render

from src import schema

_class = str_attr("class")


def get_nav(user: schema.User | None, child: TagBase | None = None):
    head_element = head(
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
    )

    nav_container = nav.attrs(
        _class("flex flex-row items-center bg-gray-900 p-3 fixed w-full h-14")
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
        )
    )("Sign up")
    signin_button = button.attrs(
        _class(
            "mr-4 inline-block rounded border border-white px-4 py-2 text-sm leading-none "
            "hover:border-transparent hover:bg-white hover:text-teal-500"
        )
    )("Sign in")
    upload_button = button.attrs(
        _class(
            "mr-4 inline-block rounded border-white bg-blue-500 px-4 py-2 text-sm "
            "font-semibold leading-none "
            "hover:border-transparent hover:bg-white hover:text-teal-500 "
        )
    )("Upload")
    profile_section = (
        a.attrs(
            _class(
                "flex flex-row items-center pr-2 hover:bg-gray-800 hover:text-white"
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
            "mr-4 inline-block rounded border border-white px-4 py-2 text-sm leading-none"
            "hover:border-transparent hover:bg-white hover:text-teal-500"
        )
    )("Sign out")

    return html(
        head_element,
        body.attrs(_class("bg-black text-white h-screen"))(
            nav_container(
                app_logo,
                new_link,
                div.attrs(_class("lg:flex-grow")),
                search_button,
                signup_button if not user else None,
                signin_button if not user else None,
                upload_button if user else None,
                profile_section if user else None,
                signout_button if user else None,
            ),
            child,
        ),
    )
