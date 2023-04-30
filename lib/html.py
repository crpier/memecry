from functools import partial, wraps
import bs4
from typing import Callable, cast, NewType

from html import escape

CleanHTML = NewType("CleanHTML", str)


class HTML:
    def __matmul__(self, a: str) -> CleanHTML:
        a = a.strip()
        if a.startswith("<html") or a.lower().startswith("<!doctype"):
            return cast(CleanHTML, bs4.BeautifulSoup(a, "html.parser").prettify())
        else:
            result = bs4.BeautifulSoup(a, "html.parser")
            return cast(CleanHTML, result.contents[0].prettify())  # type: ignore


html = HTML()


def component(wrapped_func):
    @wraps(wrapped_func)
    def wrapper(*args, **kwargs) -> CleanHTML:
        for arg in args:
            if callable(arg):
                continue
            arg = escape(arg, quote=True)
        for key, kwarg in kwargs.items():
            if callable(kwarg):
                continue
            kwargs[key] = escape(kwarg, quote=True)
        return wrapped_func(*args, **kwargs)

    return wrapper


@component
def example_component(child: Callable[[], CleanHTML], name="world"):
    return (
        html
        @ f"""
          <div class="p-8">
              Hello {name}!
              <a class="p-4 bg-black" src="example.com">click here for rewards!</a>
              <div class="wrapper">{child()}</div>
          </div>
        """
    )
