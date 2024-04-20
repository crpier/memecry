from relax.app import ViewContext
from relax.html import Element, button, div, form, h2, input, label, span
from relax.injection import Injected, component

import memecry.routes.misc
import memecry.schema


def checkbox_option(text: str, name: str, *, checked: bool) -> Element:
    attrs = {"checked": checked} if checked else {}
    return label(
        classes=[
            "label",
            "cursor-pointer",
            "flex",
            "justify-between",
            "w-full",
        ]
    ).insert(
        span(classes=["label-text", "font-semibold"], text=text),
        input(
            name=name,
            classes=["checkbox", "checkbox-primary"],
            type="checkbox",
            attrs=attrs,
        ),
    )


@component()
def preferences_page(
    user: memecry.schema.UserRead, *, context: ViewContext = Injected
) -> Element:
    return div(
        classes=[
            "card",
            "m-auto",
            "bg-base-100",
            "shadow-xl",
            "p-4",
            "w-[32rem]",
        ]
    ).insert(
        div(classes=["card-body"]).insert(
            h2(classes=["card-title"], text="Preferences")
        ),
        form(classes=["form-control", "w-full"])
        .insert(
            checkbox_option(
                "Autoplay videos on desktop",
                name="desktop_autoplay",
                checked=user.desktop_autoplay,
            ),
            checkbox_option(
                "Autoplay videos on mobile",
                name="mobile_autoplay",
                checked=user.mobile_autoplay,
            ),
            button(
                type="submit",
                classes=["btn", "w-max", "m-auto", "mt-8"],
                text="Save",
            ),
        )
        .hx_put(
            context.url_of(memecry.routes.misc.update_user)(user_id=user.id),
        ),
    )
