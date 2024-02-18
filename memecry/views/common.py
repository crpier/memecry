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
    "md:border",
    "md:rounded-lg",
    "duration-300",
    "px-1",
    "md:px-3",
    "md:py-1",
    "md:hover:border-gray-400",
    "md:hover:text-gray-400",
]


# TODO: could I have a type for tailwind color?
def special_button_classes(color: str) -> list[str]:
    return [
        f"bg-{color}-600",
        "md:font-semibold",
        "px-3",
        "py-1",
        "rounded-md",
        "md:rounded-lg",
        "text-white",
        f"md:hover:bg-{color}-700",
        f"md:hover:text-{color}-700",
    ]


DANGER_SPECIAL_BUTTON_CLASSES = special_button_classes("red")
ATTENTION_SPECIAL_BUTTON_CLASSES = special_button_classes("green")

FLEX_ROW_WRAPPER_CLASSES = [
    "flex",
    "flex-row",
    "flex-nowrap",
    "justify-between",
    "items-center",
    "px-1",
    "md:px-2",
    "md:py-2",
    "md:space-x-2",
]
FLEX_COL_WRAPPER_CLASSES = [
    "flex",
    "flex-col",
    "flex-nowrap",
    "items-center",
    "justify-center",
    "justify-items-center",
    "space-y-1",
    "md:space-y-4",
]


DROPDOWN_CLASSES = [
    "absolute",
    "rounded-md",
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

FLEX_ELEMENT_WRAPPER_CLASSES = [
    "md:border-2",
    "md:border-gray-500",
    "md:p-4",
    "md:rounded-lg",
    "space-y-1",
    "w-full",
]

INPUT_CLASSES = [
    "text-white",
    "text-2xl",
    "font-bold",
    "mb-4",
    "px-2",
    "bg-black",
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
