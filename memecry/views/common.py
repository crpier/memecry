from typing import Literal

from relax.html import (
    Tag,
    div,
)

IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
VIDEO_FORMATS = [".mp4", ".webm"]


SIMPLE_BUTTON_CLASSES = [
    "md:border",
    "md:rounded-lg",
    "duration-300",
    "px-1",
    "text-sm",
    "md:text-base",
    "md:px-3",
    "md:py-1",
    "md:hover:border-gray-400",
    "md:hover:text-gray-400",
]


# TODO: could I have a type for tailwind color?
def special_button_classes(color: Literal["red", "green"]) -> list[str]:
    # make sure we write the full class name as a string
    # so that tailwindcss cli picks it up
    if color == "red":
        bg_color = "bg-red-600"
    elif color == "green":
        bg_color = "bg-green-600"
    return [
        bg_color,
        "px-3",
        "py-1",
        "text-sm",
        "md:text-base",
        "md:font-semibold",
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
    "space-y-8",
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
    "md:border",
    "md:border-gray-600",
    "md:p-4",
    "md:rounded-lg",
    "space-y-1",
    "w-full",
]

INPUT_CLASSES = [
    "text-white",
    "text-lg",
    "md:text-2xl",
    "font-bold",
    "mb-4",
    "px-2",
    "bg-black",
]

MODAL_UNDERLAY = div(
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
