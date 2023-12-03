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


def error_element(error: str) -> div:
    return div(classes=["bg-red-700", "p-2", "rounded-md", "w-max"]).text(error)


def response_404() -> Tag:
    return div().text("404 resource not found")
