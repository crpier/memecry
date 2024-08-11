import datetime
from unittest.mock import MagicMock

import zoneinfo
from relax.app import ViewContext
from relax.injection import add_injectable
from starlette.datastructures import URL

from memecry.config import Config
from memecry.routes.post import (
    delete_post,
    get_post,
    update_searchable_content,
    update_tags,
)
from memecry.schema import PostRead
from memecry.views.post import home_view

mock_app = MagicMock(return_value="")
context = ViewContext()
context._app = mock_app  # noqa: SLF001

add_injectable(ViewContext, context)
context.add_path_function(delete_post)
context.add_path_function(update_searchable_content)
context.add_path_function(get_post)
context.add_path_function(update_tags)

config = Config()
add_injectable(Config, config)

POST_COUNT = 1000


def get_test_post() -> PostRead:
    return PostRead(
        id=4,
        created_at=datetime.datetime(
            2024, 4, 10, 16, 30, 52, tzinfo=zoneinfo.ZoneInfo(key="UTC")
        ),
        title="xzcvzxcv",
        source="sentinel",
        user_id=1,
        author_name="cristi",
        tags="animals",
        searchable_content="",
        created_since="4 weeks ago",
        score=0,
        editable=True,
        autoplayable=True,
    )


posts = [get_test_post() for _ in range(POST_COUNT)]


def lol():
    return home_view(URL(""), posts)


# start = time.monotonic()
# lol()
# end = time.monotonic()
# print(f"Time taken: {(end - start):.2f}s")


# cProfile.run("lol()", sort="tottime")
