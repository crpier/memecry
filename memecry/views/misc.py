from relax.app import ViewContext
from relax.html import (
    Element,
    Fragment,
    a,
    aside,
    body,
    button,
    dialog,
    div,
    form,
    head,
    hmr_script,
    html,
    i,
    img,
    input,
    label,
    li,
    link,
    meta,
    script,
    span,
    title,
    ul,
    video,
)
from relax.injection import Injected, component, injectable_sync

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
    if config.ENV == "prod":
        return link(href="/static/css/tailwind.css", rel="stylesheet")

    return Fragment(
        [
            link(
                href="https://cdn.jsdelivr.net/npm/daisyui@4.10.1/dist/full.min.css",
                rel="stylesheet",
                type="text/css",
            ),
            script(src="https://cdn.tailwindcss.com"),
        ],
    )


def page_head() -> head:
    return head().insert(
        title("Memecry"),
        meta(charset="UTF-8"),
        meta(
            name="viewport",
            content="width=device-width, initial-scale=1.0, maximum-scale=1.0",
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
    return html(
        lang="en", attrs={"data-theme": "luxury"}, classes=["bg-base-200"]
    ).insert(
        page_head(),
        body(
            classes=[
                "pt-20",
                "flex",
                "flex-row",
                "justify-between",
            ]
            # TODO: find a more visible place to put this (or at least document it)
        ).insert(child, hmr_script() if config.ENV == "dev" else None),
    )


@component()
def page_nav(
    *,
    user: memecry.schema.UserRead | None = None,
    context: ViewContext = Injected,
) -> Element:
    upload_form_element = upload_form()
    large_upload_button = (
        button(classes=["btn", "btn-primary"], text="Upload").hyperscript(
            f"on click call #{upload_form_element.id}'s showModal()"
        )
        if user
        else None
    )
    small_upload_button = (
        (
            li().insert(
                button(text="Upload").hyperscript(
                    f"on click call #{upload_form_element.id}'s showModal()"
                )
            ),
        )
        if user
        else None
    )

    large_signout_button = (
        li().insert(
            button(text="Sign out").hx_get(
                target=context.url_of(memecry.routes.auth.signout)(),
                hx_target="body",
                hx_swap="beforeend",
            )
        )
        if user
        else None
    )
    small_signout_button = (
        li().insert(
            button(text="Sign out").hx_get(
                target=context.url_of(memecry.routes.auth.signout)(),
                hx_target="body",
                hx_swap="beforeend",
            )
        )
        if user
        else None
    )

    signin_form_element = signin_form()
    large_signin_button = (
        (
            button(
                id="signin",
                classes=["btn", "btn-primary"],
                text="Sign in",
            ).hyperscript(f"on click call #{signin_form_element.id}'s showModal()")
        )
        if not user
        else None
    )

    small_signin_button = (
        li().insert(
            button(
                id="signin",
                text="Sign in",
            ).hyperscript(f"on click call #{signin_form_element.id}'s showModal()")
        )
        if not user
        else None
    )

    signup_form_element = signup_form()
    large_signup_button = (
        button(classes=["btn", "btn-neutral"], text="Sign up").hyperscript(
            f"on click call #{signup_form_element.id}'s showModal()"
        )
        # TODO: make this a disabled button if signups are disabled
        if not user
        else None
    )
    small_signup_button = li().insert(
        button(text="Sign up").hyperscript(
            f"on click call #{signup_form_element.id}'s showModal()"
        )
        if not user
        else None
    )

    small_preferences_button = (
        li().insert(
            a(
                href="/preferences",
                text="Preferences",
            )
        )
        if user
        else None
    )

    large_preferences_button = (
        li().insert(
            a(
                text="Preferences",
                href="/preferences",
            )
        )
        if user
        else None
    )

    avatar_dropdown = (
        div(classes=["dropdown", "dropdown-end"]).insert(
            div(
                attrs={"tabindex": "0", "role": "button"},
                classes=["btn", "btn-ghost", "btn-circle", "avatar"],
            ).insert(
                div(classes=["w-10", "rounded-full"]).insert(
                    img(
                        alt="avatar",
                        src="https://avatars.githubusercontent.com/u/31815875?v=4",
                    ),
                )
            ),
            ul(
                attrs={"tabindex": "0"},
                classes=[
                    "menu",
                    "menu-sm",
                    "dropdown-content",
                    "mt-3",
                    "p-2",
                    "shadow",
                    "bg-base-100",
                    "rounded-box",
                ],
            ).insert(
                large_preferences_button,
                large_signout_button,
            ),
        )
        if user
        else None
    )

    return div(
        classes=["navbar", "bg-base-100", "fixed", "top-0", "left-0", "z-[1]"]
    ).insert(
        signup_form_element,
        signin_form_element,
        upload_form_element,
        # always visible elements
        div(classes=["flex-1", "navbar-start", "gap-4"]).insert(
            a(classes=["btn", "btn-ghost", "text-2xl"], text="Memecry", href="/"),
        ),
        div(classes=["flex-auto", "navbar-start", "hidden", "lg:flex"]).insert(
            a(
                classes=["btn", "btn-ghost", "text-lg", "text-secondary-content"],
                text="Random",
                href="/random",
            ),
        ),
        # > md screen elements
        div(classes=["gap-2", "navbar-end", "hidden", "sm:flex"]).insert(
            form(
                classes=["form-control"],
                action="/search",
            ).insert(
                input(
                    name="query",
                    classes=["input", "input-bordered", "w-24", "sm:w-auto"],
                    type="text",
                    placeholder="Search",
                    attrs={"enterkeyhint": "search"},
                ),
            ),
            large_signin_button,
            large_signup_button,
            large_upload_button,
            avatar_dropdown,
        ),
        # < md screen elements
        div(classes=["navbar-end", "gap-2", "w-auto", "sm:hidden"]).insert(
            form(classes=["form-control"], action="/search").insert(
                input(
                    name="query",
                    classes=["input", "input-bordered", "w-full"],
                    type="text",
                    placeholder="Search",
                    attrs={"enterkeyhint": "search"},
                ),
            ),
            div(
                classes=[
                    "dropdown",
                    "dropdown-end",
                ]
            ).insert(
                button(
                    attrs={"tabindex": "0", "role": "button"},
                    classes=["btn", "btn-sm"],
                ).insert(i(classes=["fa", "fa-bars", "fa-sm"])),
                ul(
                    attrs={"tabindex": "1"},
                    classes=[
                        "menu",
                        "menu-sm",
                        "dropdown-content",
                        "mt-3",
                        "p-2",
                        "shadow",
                        "bg-base-100",
                        "rounded-box",
                    ],
                ).insert(
                    small_upload_button,
                    small_preferences_button,
                    li().insert(
                        a(
                            classes=[],
                            text="Random",
                            href="/random",
                        ),
                    ),
                    small_signout_button,
                    small_signin_button,
                    small_signup_button,
                ),
            ),
        ),
    )


def keybind_helper(keybind: str, explanation: str) -> Element:
    return div(classes=["space-x-2", "px-2", "text-left", "text-sm"]).insert(
        span(classes=["font-bold", "kbd"], text=keybind),
        span(text=explanation),
    )


def section_separator(name: str) -> Element:
    return div(
        classes=["space-x-2", "px-4", "text-left", "text-sm", "font-semibold", "pt-4"],
        text=name,
    )


# TODO: maybe this would be better as a card, or a modal?
def commands_helper(*, key: str, display_hack: bool = False) -> Element:
    return aside(
        classes=[
            "hidden",
            "sm:block",
            "px-8",
            "max-h-full",
            "text-white",
            "sm:max-w-lg",
            "invisible" if display_hack is True else "",
        ]
    ).insert(
        div(
            classes=[
                "block",
                "rounded-lg",
                "text-center",
                "border",
                "border-gray-600",
                "text-white",
                "bg-base-100",
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
            div(classes=["pb-4", "space-y-1"]).insert(
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
def upload_form(*, context: ViewContext = Injected, id: str = Injected) -> dialog:
    upload_error_placeholder = div(
        id="signin-error", classes=["!m-0", "flex", "justify-center", "pt-4"]
    )
    tags_element = memecry.views.post.tags_component(post_id=0, editable=True).classes(
        ["mr-auto", "my-auto"]
    )

    return dialog(classes=["modal", "modal-bottom", "sm:modal-middle"]).insert(
        div(
            classes=[
                "modal-box",
                "space-y-4",
                "max-w-full",
                "sm:max-w-xl",
            ]
        ).insert(
            form(
                attrs={"method": "dialog"},
            ).insert(
                button(
                    type="submit",
                    classes=[
                        "btn",
                        "btn-xs",
                        "btn-circle",
                        "btn-outline",
                        "ml-auto",
                        "absolute",
                        "right-2",
                        "top-2",
                    ],
                    text="X",
                )
            ),
            div(
                classes=[
                    "font-bold",
                    "text-xl",
                    "text-center",
                ],
                text="Go ahead, take a sip",
            ),
            form(
                classes=["form-control", "space-y-4", "flex"],
                id=f"form-{id}",
            )
            .hx_post(
                context.url_of(memecry.routes.post.upload)(),
                hx_encoding="multipart/form-data",
                hx_target=f"#{upload_error_placeholder.id}",
                hx_swap="innerHTML",
                hx_include=f"#tags-text-{tags_element.id}",
            )
            .insert(
                label(
                    classes=[
                        "input",
                        "input-bordered",
                        "flex",
                        "items-center",
                        "gap-2",
                    ],
                    _for="title",
                ).insert(
                    input(
                        type="text",
                        name="title",
                        placeholder="Title",
                        classes=["grow"],
                    ),
                ),
                input(
                    type="file",
                    name="file",
                    classes=[
                        "file-input",
                        "file-input-bordered",
                        "w-full",
                    ],
                    attrs={"onchange": "loadFile(event)"},
                ),
                div(classes=["flex", "align-center"]).insert(
                    tags_element,
                    button(
                        type="submit",
                        classes=["btn", "btn-primary"],
                        text="Upload",
                    ),
                ),
                img(id="preview_img", src="", alt="", classes=["hidden"]),
                video(id="preview_video", src="", classes=["hidden"], controls=True),
            ),
            upload_error_placeholder,
            # TODO: need to figure out how to reload scripts in the browser
            script(
                js="""
           var loadFile = function(event) {
               var input = event.target;
               var file = input.files[0];
               var type = file.type;
               if (type.startsWith("image")) {
                   var output = document.getElementById('preview_img');
                   output.classList.remove("hidden")
                   output.src = URL.createObjectURL(event.target.files[0]);
                   output.onload = function() {
                       URL.revokeObjectURL(output.src) // free memory
                   }
               } else if (type.startsWith("video")) {
                   var output = document.getElementById('preview_video');
                   output.classList.remove("hidden")
                   output.src = URL.createObjectURL(event.target.files[0]);
                   output.play()
                   output.onload = function() {
                       URL.revokeObjectURL(output.src) // free memory
                   }
               } else {
                   console.error("Unsupported file type")
               }

        };"""
            ),
        ),
    )


@component()
def signin_form(*, context: ViewContext = Injected) -> dialog:
    signin_error_placeholder = div(
        id="signin-error", classes=["!m-0", "flex", "justify-center", "pt-4"]
    )
    return dialog(classes=["modal", "modal-bottom", "sm:modal-middle"]).insert(
        div(classes=["modal-box", "space-y-4", "max-w-full", "sm:max-w-lg"]).insert(
            form(
                attrs={"method": "dialog"},
            ).insert(
                button(
                    type="submit",
                    classes=[
                        "btn",
                        "btn-xs",
                        "btn-circle",
                        "btn-outline",
                        "ml-auto",
                        "absolute",
                        "right-2",
                        "top-2",
                    ],
                    text="X",
                )
            ),
            div(
                classes=[
                    "font-bold",
                    "text-xl",
                    "text-center",
                    "items-center",
                    "justify-center",
                ],
                text="Welcome back",
            ),
            form(classes=["form-control", "space-y-4"])
            .hx_post(
                context.url_of(memecry.routes.auth.signin)(),
                hx_encoding="multipart/form-data",
                hx_target=f"#{signin_error_placeholder.id}",
                hx_swap="innerHTML",
            )
            .insert(
                label(
                    classes=[
                        "input",
                        "input-bordered",
                        "flex",
                        "items-center",
                        "gap-2",
                    ],
                    _for="username",
                ).insert(
                    i(classes=["fa", "fa-user"]),
                    input(
                        type="text",
                        name="username",
                        placeholder="Username",
                        classes=["grow"],
                    ),
                ),
                label(
                    classes=[
                        "input",
                        "input-bordered",
                        "flex",
                        "items-center",
                        "gap-2",
                    ],
                    _for="password",
                ).insert(
                    i(classes=["fa", "fa-lock"]),
                    input(
                        type="password",
                        name="password",
                        placeholder="Password",
                        classes=["grow"],
                    ),
                ),
                button(
                    type="submit",
                    classes=["btn", "btn-primary", "m-auto"],
                ).text("Sign in"),
            ),
            signin_error_placeholder,
        ),
    )


@component()
def signup_form(*, view_context: ViewContext = Injected) -> dialog:
    signup_error_placeholder = div(
        id="signup-error", classes=["!m-0", "flex", "justify-center", "pt-4"]
    )
    return dialog(classes=["modal", "modal-bottom", "sm:modal-middle"]).insert(
        div(classes=["modal-box", "space-y-4", "max-w-full", "sm:max-w-lg"]).insert(
            form(
                attrs={"method": "dialog"},
            ).insert(
                button(
                    type="submit",
                    classes=[
                        "btn",
                        "btn-xs",
                        "btn-circle",
                        "btn-outline",
                        "ml-auto",
                        "absolute",
                        "right-2",
                        "top-2",
                    ],
                    text="X",
                )
            ),
            div(
                classes=[
                    "font-bold",
                    "text-xl",
                    "text-center",
                    "items-center",
                    "justify-center",
                ],
                text="Might as well make an account",
            ),
            form(classes=["form-control", "space-y-4"])
            .hx_post(
                view_context.url_of(memecry.routes.auth.signup)(),
                hx_encoding="multipart/form-data",
                hx_target=f"#{signup_error_placeholder.id}",
            )
            .insert(
                label(
                    classes=[
                        "input",
                        "input-bordered",
                        "flex",
                        "items-center",
                        "gap-2",
                    ],
                    _for="username",
                ).insert(
                    i(classes=["fa", "fa-user"]),
                    input(
                        type="text",
                        name="username",
                        placeholder="Username",
                        classes=["grow"],
                    ),
                ),
                label(
                    classes=[
                        "input",
                        "input-bordered",
                        "flex",
                        "items-center",
                        "gap-2",
                    ],
                    _for="password",
                ).insert(
                    i(classes=["fa", "fa-lock"]),
                    input(
                        type="password",
                        name="password",
                        placeholder="Password",
                        classes=["grow"],
                    ),
                ),
                button(
                    type="submit",
                    classes=["btn", "btn-primary", "m-auto"],
                ).text("Sign up"),
            ),
            signup_error_placeholder,
        ),
    )
