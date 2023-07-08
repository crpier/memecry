from yahgl_py.main import div, button, svg, path, p, img, span


def post_view():
    post = div(
        classes=[
            "max-w-[580px]",
            "mt-4",
            "mx-auto",
            "bg-white",
            "rounded-lg",
            "overflow-hidden",
        ]
    ).insert(
        p(
            classes=[
                "text-xl",
                "text-center",
                "px-4",
                "py-2",
                "bg-gray-200",
            ]
        ).text("Funny Meme Title"),
        img(
            src="https://via.placeholder.com/100x167",
            alt="funny meme I hope",
            classes=["w-full"],
        ),
        div(classes=["p-4"]).insert(
            div(
                classes=[
                    "flex",
                    "items-center",
                    "text-gray-600",
                    "text-sm",
                    "mb-2",
                    "space-x-2",
                ]
            ).insert(
                span().text("Score: 100"),
                span().text("Posted 1 hour ago"),
                span().text("Comments: 50"),
            ),
            div(classes=["flex", "items-center", "mb-4", "space-x-2"]).insert(
                button(
                    classes=[
                        "bg-indigo-500",
                        "hover:bg-indigo-600",
                        "text-white",
                        "font-semibold",
                        "py-2",
                        "px-4",
                        "rounded-md",
                    ]
                ).insert(
                    svg(
                        classes=["h-5", "w-5", "fill-current"],
                        attrs={"viewbox": "0 0 20 20"},
                    ).insert(
                        path(
                            attrs={
                                "d": "M10 18l-8-8h5V2h6v8h5l-8 8zm-8-6l8-8 8 8h-5v6H7v-6H2z"
                            }
                        )
                    )
                ),
                button(
                    classes=[
                        "bg-indigo-500",
                        "hover:bg-indigo-600",
                        "text-white",
                        "font-semibold",
                        "py-2",
                        "px-4",
                        "rounded-md",
                    ]
                ).insert(
                    svg(
                        classes=["h-5", "w-5", "fill-current"],
                        attrs={"viewbox": "0 0 20 20"},
                    ).insert(
                        path(
                            attrs={
                                "d": "M10 2L2 8h3v10h10V8h3L10 2zm1 14h-2v-2h2v2zm0-4h-2V6h2v6z"
                            }
                        )
                    )
                ),
                button(
                    classes=[
                        "bg-indigo-500",
                        "hover:bg-indigo-600",
                        "text-white",
                        "font-semibold",
                        "py-2",
                        "px-4",
                        "rounded-md",
                    ]
                ).insert(
                    svg(
                        classes=["h-5", "w-5", "fill-current"],
                        attrs={"viewbox": "0 0 20 20"},
                    ).insert(
                        path(
                            attrs={
                                "d": "M2 5h16v2H2V5zm0 4h12v2H2v-2zm0 4h16v2H2v-2zm0 4h12v2H2v-2z"
                            }
                        )
                    )
                ),
            ),
        ),
    )

    return div().insert(post, post, post)
