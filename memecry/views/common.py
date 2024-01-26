from relax.html import (
    Tag,
    div,
    path,
    svg,
)

IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
VIDEO_FORMATS = [".mp4", ".webm"]


# TODO: isn'te there a fa icon?
def hamburger_svg() -> svg:
    return svg(
        classes=["h-6", "w-6", "text-gray-500"],
        attrs={
            "x-show": "!showMenu",
            "fill": "none",
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
            "stroke-width": "2",
            "viewBox": "0 0 24 24",
            "stroke": "currentColor",
        },
    ).insert(path(attrs={"d": "M4 6h16M4 12h16M4 18h16"}))


SIMPLE_BUTTON_CLASSES = [
    "border",
    "duration-300",
    "px-3",
    "py-1",
    "rounded-lg",
    "hover:border-gray-400",
    "hover:text-gray-400",
]


def special_button_classes(color: str) -> list[str]:
    return [
        f"bg-{color}-600",
        "font-semibold",
        "px-3",
        "py-1",
        "rounded-lg",
        "text-white",
        f"hover:bg-{color}-700",
        f"hover:text-{color}-700",
    ]


FLEX_ROW_WRAPPER_CLASSES = [
    "flex",
    "flex-row",
    "flex-nowrap",
    "justify-between",
    "items-center",
    "px-4",
    "py-2",
    "md:px-0",
    "space-x-4",
]
FLEX_COL_WRAPPER_CLASSES = [
    "flex",
    "flex-col",
    "items-center",
    "justify-center",
    "justify-items-center",
    "space-y-4",
]


DROPDOWN_CLASSES = [
    "absolute",
    "rounded",
    "shadow",
    "flex-col",
    "w-max",
    "mt-1",
    "border",
    "bg-black",
]

BASIC_FORM_CLASSES = [
    "z-50",
    "bg-gray-800",
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

MODAL_UNDERLAY = div(
    attrs={"name": "underlay"},
    classes=[
        "fixed",
        "inset-0",
        "w-screen",
        "-z-10",
        "bg-black",
        "bg-opacity-50",
    ],
    hyperscript="on click trigger closeModal",
)


def error_element(error: str) -> div:
    return div(classes=["bg-red-700", "p-2", "rounded-md", "w-max"]).text(error)


def response_404() -> Tag:
    return div().text("404 resource not found")
