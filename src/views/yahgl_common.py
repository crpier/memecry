from yahgl_py.main import (
    InputType,
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
    input,
    label,
    link,
    meta,
    nav,
    p,
    path,
    script,
    svg,
    title,
)

from src import schema


def alert_button(text: str):
    return button(
        classes=[
            "px-3",
            "py-1",
            "rounded-md",
            "text-sm",
            "text-white",
            "bg-blue-500",
            "hover:bg-blue-700",
        ],
    ).text(text)


def login_form():
    return div(
        classes=[
            "z-10",
            "top-0",
            "left-0",
            "w-full",
            "h-full",
            "fixed",
            "bg-black",
            "bg-opacity-75",
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
                    ).text("X"),
                ),
                form(
                    attrs={
                        "hx-encoding": "multipart/form-data",
                        "hx-post": "/token",
                    }
                ).insert(
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
                            name="username",
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
                            name="password",
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
                            attrs={"type": "submit", "onclick": "toggleLoginModal()"},
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
        classes=[
            "z-10",
            "top-0",
            "left-0",
            "w-full",
            "h-full",
            "fixed",
            "bg-black",
            "bg-opacity-75",
        ],
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
                    ).text("X"),
                ),
                form(
                    attrs={
                        "hx-encoding": "multipart/form-data",
                        "hx-post": "/signup",
                    }
                ).insert(
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
                            name="username",
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
                            name="email",
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
                            name="password",
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
                                "type": "submit",
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
        meta(name="viewport", content="width=device-width, initial-scale=1"),
        # TODO: use pytailwindcss instead?
        script(src="https://cdn.tailwindcss.com"),
        link(
            href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css",
            rel="stylesheet",
        ),
        script(src="/static/js/htmx.min.js?v=1.5.0"),
        script(src="/static/js/close_modals.js"),
        link(href="/static/css/global.css", rel="stylesheet"),
    )


def page_nav(user: schema.User | None) -> Tag:
    return nav(
        classes=[
            "bg-gray-800",
            "mx-auto",
            "px-4",
            "py-1",
            "sm:px-6",
            "lg:px-8",
            "flex",
            "justify-between",
            "items-center",
        ]
    ).insert(
        div(classes=["flex", "items-center"]).insert(
            a(
                href="#",
                classes=["flex-shrink-0", "text-white", "font-bold", "text-lg"],
            ).text("Memecry"),
            div(classes=["hidden", "md:ml-6", "md:flex", "md:space-x-4"]).insert(
                div(classes=["relative"]).insert(
                    div(
                        classes=[
                            "absolute",
                            "inset-y-0",
                            "left-0",
                            "pl-3",
                            "flex",
                            "items-center",
                            "pointer-events-none",
                        ]
                    ).insert(i(classes=["fa", "fa-search", "text-gray-400"])),
                    input(
                        type=InputType.text,
                        name="TODO-name-me",
                        classes=[
                            "bg-gray-700",
                            "text-white",
                            "rounded-md",
                            "py-1",
                            "pl-10",
                            "pr-4",
                            "focus:outline-none",
                            "focus:bg-gray-600",
                            "focus:text-white",
                            "placeholder-gray-400",
                        ],
                        attrs={"placeholder": "Search"},
                    ),
                )
            ),
        ),
        div(classes=["flex", "items-center"]).insert(
            alert_button("Upload"),
            div(classes=["mx-3"]).insert(
                button(
                    classes=[
                        "flex",
                        "text-sm",
                        "rounded-full",
                        "focus:outline-none",
                        "focus:ring-2",
                        "focus:ring-offset-2",
                        "focus:ring-offset-gray-800",
                        "focus:ring-gray",
                        "hover:ring-2",
                        "hover:ring-offset-2",
                        "hover:ring-offset-gray-800",
                        "hover:ring-gray",
                    ]
                ).insert(
                    img(
                        alt="profile pciture",
                        src="https://avatars.githubusercontent.com/u/31815875?v=4",
                        classes=["h-8", "w-8", "rounded-full"],
                    )
                )
            ),
            a(
                href="#",
                classes=[
                    "text-gray-300",
                    "hover:bg-gray-700",
                    "hover:text-white",
                    "px-3",
                    "py-2",
                    "rounded-md",
                    "text-sm",
                    "font-medium",
                ],
            ).text("Logout"),
        ),
    )


def page_root(user: schema.User | None, child: Tag | None = None):
    return html(lang="en").insert(
        page_head(),
        body().insert(
            page_nav(user),
            child,
        ),
    )


def post_upload_form():
    return div(
        classes=[
            "modal",
            "fixed",
            "inset-0",
            "flex",
            "items-center",
            "justify-center",
        ]
    ).insert(
        div(
            classes=[
                "modal-content",
                "bg-gray-800",
                "text-white",
                "rounded-lg",
                "px-8",
                "py-6",
            ]
        ).insert(
            button(
                classes=[
                    "absolute",
                    "right-2",
                    "top-2",
                    "text-white",
                    "hover:text-gray-300",
                    "focus:outline-none",
                ],
                attrs={"id": "close-btn"},
            ).insert(
                svg(
                    classes=["h-6", "w-6"],
                    attrs={"fill": "currentColor", "viewbox": "0 0 20 20"},
                ).insert(
                    path(
                        attrs={
                            "d": "M6.35 6.34l1.41-1.41 3.54 3.54 3.54-3.54 1.41 1.41-3.54 3.54 3.54 3.54-1.41 1.41-3.54-3.54-3.54 3.54-1.41-1.41 3.54-3.54L6.35 6.34z"
                        }
                    )
                )
            ),
            p(classes=["text-2xl", "font-bold", "mb-4"]).text("Upload Image"),
            form(classes=["modal-form"]).insert(
                div(classes=["mb-4"]).insert(
                    label(
                        _for="title",
                        classes=["block", "text-gray-300", "font-bold", "mb-2"],
                    ).text("Title"),
                    input(
                        type=InputType.text,
                        name="TODO-name-me",
                        classes=[
                            "w-full",
                            "rounded-md",
                            "bg-gray-700",
                            "text-white",
                            "py-2",
                            "px-3",
                            "focus:outline-none",
                            "focus:ring-2",
                            "focus:ring-indigo-500",
                            "focus:border-transparent",
                        ],
                        attrs={"id": "title", "placeholder": "Enter title"},
                    ),
                ),
                div(classes=["mb-4"]).insert(
                    label(
                        _for="image",
                        classes=["block", "text-gray-300", "font-bold", "mb-2"],
                    ).text("Image"),
                    input(
                        type=InputType.file,
                        name="TODO-name-me",
                        classes=["w-full"],
                        attrs={"id": "image", "accept": "image/*"},
                    ),
                    div(classes=["mt-2"], attrs={"id": "image-preview"}),
                ),
                button(
                    classes=[
                        "bg-indigo-500",
                        "text-white",
                        "font-semibold",
                        "py-2",
                        "px-4",
                        "rounded-md",
                        "focus:outline-none",
                    ],
                    attrs={"type": "submit"},
                ).text("Upload"),
            ),
            script(
                js="""
    const modal = document.querySelector('.modal');
    const modalForm = document.querySelector('.modal-form');
    const imagePreview = document.getElementById('image-preview');

    function handleImageUpload(event) {
      const file = event.target.files[0];
      const reader = new FileReader();

      reader.onload = function (event) {
        const imageUrl = event.target.result;
        imagePreview.innerHTML = `<img src="${imageUrl}" alt="Preview" class="w-full h-auto">`;
      };

      reader.readAsDataURL(file);
    }

    modalForm.addEventListener('submit', function (event) {
      event.preventDefault();
      // Handle form submission here
    });

    document.getElementById('image').addEventListener('change', handleImageUpload);
"""
            ),
        )
    )
