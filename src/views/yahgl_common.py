from yahgl_py.main import (
    InputType,
    Tag,
    body,
    div,
    a,
    head,
    html,
    input,
    button,
    form,
    label,
    link,
    meta,
    script,
    title,
)

from src import schema


def open_login_form():
    return div(classes=["flex", "items-center", "justify-center", "h-screen"]).insert(
        button(
            classes=[
                "bg-blue-500",
                "hover:bg-blue-700",
                "text-white",
                "font-bold",
                "py-2",
                "px-4",
                "rounded",
                "focus:outline-none",
                "focus:shadow-outline",
            ],
            attrs={"onclick": "toggleModal()"},
        ).text("Open Login Form")
    )


def login_form():
    return div(
        classes=[
            "top-0",
            "left-0",
            "w-full",
            "h-full",
            "bg-transparent",
        ],
    ).insert(
        div(classes=["flex", "items-center", "justify-center", "h-screen"]).insert(
            div(
                classes=[
                    "bg-gray-800",
                    "rounded-lg",
                    "shadow-md",
                    "px-8",
                    "pt-6",
                    "pb-8",
                ]
            ).insert(
                div(classes=["flex", "justify-between", "items-center", "mb-4"]).insert(
                    div(classes=["text-white", "text-4xl", "text-center"]).text(
                        "Login"
                    ),
                    button(
                        classes=["text-white", "text-2xl", "focus:outline-none"],
                        attrs={"onclick": "closeLoginModal()"},
                    ).text("×"),
                ),
                form().insert(
                    div(classes=["mb-4"]).insert(
                        label(
                            _for="username",
                            classes=[
                                "block",
                                "text-white",
                                "text-sm",
                                "font-bold",
                                "mb-2",
                            ],
                        ).text("Username"),
                        input(
                            type=InputType.text,
                            name="TODO-name-me",
                            classes=[
                                "shadow",
                                "appearance-none",
                                "border",
                                "rounded",
                                "w-full",
                                "py-2",
                                "px-3",
                                "text-gray-700",
                                "leading-tight",
                                "focus:outline-none",
                                "focus:shadow-outline",
                            ],
                            attrs={
                                "id": "username",
                                "placeholder": "Enter your username",
                            },
                        ),
                    ),
                    div(classes=["mb-6"]).insert(
                        label(
                            _for="password",
                            classes=[
                                "block",
                                "text-white",
                                "text-sm",
                                "font-bold",
                                "mb-2",
                            ],
                        ).text("Password"),
                        input(
                            type=InputType.password,
                            name="TODO-name-me",
                            classes=[
                                "shadow",
                                "appearance-none",
                                "border",
                                "border-red-500",
                                "rounded",
                                "w-full",
                                "py-2",
                                "px-3",
                                "text-gray-700",
                                "leading-tight",
                                "focus:outline-none",
                                "focus:shadow-outline",
                            ],
                            attrs={
                                "id": "password",
                                "placeholder": "******************",
                            },
                        ),
                    ),
                    div(classes=["flex", "items-center", "justify-between"]).insert(
                        button(
                            classes=[
                                "bg-blue-500",
                                "hover:bg-blue-700",
                                "text-white",
                                "font-bold",
                                "py-2",
                                "px-4",
                                "rounded",
                                "focus:outline-none",
                                "focus:shadow-outline",
                            ],
                            attrs={"type": "button", "onclick": "toggleLoginModal()"},
                        ).text("Sign In"),
                        a(
                            href="#",
                            classes=[
                                "inline-block",
                                "align-baseline",
                                "font-bold",
                                "text-sm",
                                "text-blue-500",
                                "hover:text-blue-800",
                            ],
                        ).text("Forgot Password?"),
                    ),
                    script(
                        js="""
function closeLoginModal() {
    var container = document.getElementById("login-modal")
    setTimeout(function () {
        container.innerHTML = ""
    }, 50)
}
    }"""
                    ),
                ),
            )
        )
    )


def signup_form():
    return div(
        classes=["z-50", "top-0", "left-0", "w-full", "h-full"],
        attrs={"id": "signup-modal"},
    ).insert(
        div(classes=["flex", "items-center", "justify-center", "h-screen"]).insert(
            div(
                classes=[
                    "bg-gray-800",
                    "rounded-lg",
                    "shadow-md",
                    "px-8",
                    "pt-6",
                    "pb-8",
                ]
            ).insert(
                div(classes=["flex", "justify-between", "items-center", "mb-4"]).insert(
                    div(classes=["text-white", "text-4xl", "text-center"]).text(
                        "Signup"
                    ),
                    button(
                        classes=["text-white", "text-2xl", "focus:outline-none"],
                        attrs={"onclick": "closeSignupModal()"},
                    ).text("×"),
                ),
                form().insert(
                    div(classes=["mb-4"]).insert(
                        label(
                            _for="username",
                            classes=[
                                "block",
                                "text-white",
                                "text-sm",
                                "font-bold",
                                "mb-2",
                            ],
                        ).text("Username"),
                        input(
                            type=InputType.text,
                            name="TODO-name-me",
                            classes=[
                                "shadow",
                                "appearance-none",
                                "border",
                                "rounded",
                                "w-full",
                                "py-2",
                                "px-3",
                                "text-gray-700",
                                "leading-tight",
                                "focus:outline-none",
                                "focus:shadow-outline",
                            ],
                            attrs={
                                "id": "username",
                                "placeholder": "Enter your username",
                            },
                        ),
                    ),
                    div(classes=["mb-4"]).insert(
                        label(
                            _for="email",
                            classes=[
                                "block",
                                "text-white",
                                "text-sm",
                                "font-bold",
                                "mb-2",
                            ],
                        ).text("Email"),
                        input(
                            type=InputType.email,
                            name="TODO-name-me",
                            classes=[
                                "shadow",
                                "appearance-none",
                                "border",
                                "rounded",
                                "w-full",
                                "py-2",
                                "px-3",
                                "text-gray-700",
                                "leading-tight",
                                "focus:outline-none",
                                "focus:shadow-outline",
                            ],
                            attrs={
                                "id": "email",
                                "placeholder": "Enter your email",
                            },
                        ),
                    ),
                    div(classes=["mb-6"]).insert(
                        label(
                            _for="password",
                            classes=[
                                "block",
                                "text-white",
                                "text-sm",
                                "font-bold",
                                "mb-2",
                            ],
                        ).text("Password"),
                        input(
                            type=InputType.password,
                            name="TODO-name-me",
                            classes=[
                                "shadow",
                                "appearance-none",
                                "border",
                                "border-red-500",
                                "rounded",
                                "w-full",
                                "py-2",
                                "px-3",
                                "text-gray-700",
                                "leading-tight",
                                "focus:outline-none",
                                "focus:shadow-outline",
                            ],
                            attrs={
                                "id": "password",
                                "placeholder": "******************",
                            },
                        ),
                    ),
                    div(classes=["flex", "items-center", "justify-between"]).insert(
                        button(
                            classes=[
                                "bg-blue-500",
                                "hover:bg-blue-700",
                                "text-white",
                                "font-bold",
                                "py-2",
                                "px-4",
                                "rounded",
                                "focus:outline-none",
                                "focus:shadow-outline",
                            ],
                            attrs={
                                "type": "button",
                                "onclick": "toggleModal('signup-modal')",
                            },
                        ).text("Sign Up"),
                        a(
                            href="#",
                            classes=[
                                "inline-block",
                                "align-baseline",
                                "font-bold",
                                "text-sm",
                                "text-blue-500",
                                "hover:text-blue-800",
                            ],
                        ).text("Terms of Service"),
                    ),
                    script(
                        js="""
function closeSignupModal() {
    var container = document.getElementById("signup-modal")
    setTimeout(function () {
        container.innerHTML = ""
    }, 50)
}
    }"""
                    ),
                ),
            )
        )
    )


def page_head():
    return head().insert(
        title("Memecry"),
        meta(charset="UTF-8"),
        meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        link(
            href="https://unpkg.com/tailwindcss@^2/dist/tailwind.min.css",
            rel="stylesheet",
        ),
        link(
            href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css",
            rel="stylesheet",
        ),
        script(src="/static/js/htmx.min.js?v=1.5.0"),
        script(src="/static/js/close_modals.js"),
        link(href="/static/css/global.css", rel="stylesheet"),
    )


def page_nav(user: schema.User | None) -> Tag:
    ...


def page_root(user: schema.User | None, child: Tag | None = None):
    return html(lang="en").insert(
        page_head(),
        body().insert(
            page_nav(user),
            child,
        ),
    )
