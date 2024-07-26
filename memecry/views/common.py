from relax.html import (
    Tag,
    div,
    i,
    span,
)

IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
VIDEO_FORMATS = [".mp4", ".webm"]


SIMPLE_BUTTON_CLASSES = ["btn", "btn-sm", "md:btn-md"]


NEUTRAL_BUTTON_CLASSES = [*SIMPLE_BUTTON_CLASSES, "btn-neutral"]
PRIMARY_BUTTON_CLASSES = [*SIMPLE_BUTTON_CLASSES, "btn-primary"]
SECONDARY_BUTTON_CLASSES = [*SIMPLE_BUTTON_CLASSES, "btn-secondary"]
ACCENT_BUTTON_CLASSES = [*SIMPLE_BUTTON_CLASSES, "btn-accent"]
GHOST_BUTTON_CLASSES = [*SIMPLE_BUTTON_CLASSES, "btn-ghost"]
LINK_BUTTON_CLASSES = [*SIMPLE_BUTTON_CLASSES, "btn-link"]

FLEX_ROW_WRAPPER_CLASSES = [
    "flex",
    "flex-row",
    "flex-nowrap",
    "justify-between",
    "items-center",
    "px-1",
    "sm:px-2",
    "sm:py-2",
    "sm:space-x-2",
]
FLEX_COL_WRAPPER_CLASSES = [
    "flex",
    "flex-col",
    "flex-nowrap",
    "items-center",
    "justify-center",
    "justify-items-center",
    "space-y-8",
]


DROPDOWN_CLASSES = [
    "absolute",
    "rounded-md",
    "shadow",
    "flex-col",
    "w-max",
    "mt-1",
    "border",
]

BASIC_FORM_CLASSES = [
    "border",
    "border-gray-100",
    "rounded-md",
    "flex",
    "flex-col",
    "space-y-4",
    "items-start",
    "w-max",
    "p-4",
]

INPUT_CLASSES = [
    "text-white",
    "text-lg",
    "sm:text-2xl",
    "font-bold",
    "mb-4",
    "px-2",
]

MODAL_UNDERLAY = div(
    classes=[
        "fixed",
        "inset-0",
        "w-screen",
        "-z-10",
    ],
    hyperscript="on click trigger closeModal",
)


def error_element(error: str) -> div:
    return div(
        attrs={"role": "alert"},
        classes=["alert", "alert-error", "flex", "justify-center"],
    ).insert(i(classes=["fa", "fa-warning"]), span(text=error))


def response_404() -> Tag:
    return div().text("404 resource not found")
