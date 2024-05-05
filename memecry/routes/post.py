import logging
import time
from dataclasses import dataclass
from typing import (
    cast,
)

from relax.app import (
    AuthScope,
    HTMLResponse,
    PathInt,
    QueryInt,
    QueryStr,
    Router,
)
from relax.html import div, input
from starlette.datastructures import UploadFile
from starlette.responses import RedirectResponse, Response

import memecry.posts_service
import memecry.routes.auth
import memecry.schema
import memecry.views.common
import memecry.views.misc
import memecry.views.post

router = Router()


@router.path_function("GET", "/posts/{post_id}")
async def get_post(request: memecry.schema.Request, post_id: PathInt) -> HTMLResponse:
    post = await memecry.posts_service.get_post_by_id(
        post_id, viewer=request.user if request.user.is_authenticated else None
    )
    if post is None:
        return HTMLResponse(memecry.views.common.error_element("Post not found"))
    if request.scope["from_htmx"]:
        return HTMLResponse(memecry.views.post.post_component(post=post))
    return HTMLResponse(
        memecry.views.misc.page_root(
            [
                memecry.views.misc.page_nav(
                    user=request.user if request.user.is_authenticated else None,
                ),
                memecry.views.misc.commands_helper(key="visible", display_hack=False),
                div(classes=["sm:w-[32rem]"]).insert(
                    memecry.views.post.post_component(post=post)
                ),
                memecry.views.misc.commands_helper(display_hack=True, key="hidden"),
            ],
        ),
    )


@router.path_function("GET", "/random")
async def random_post(
    request: memecry.schema.Request,
) -> RedirectResponse | HTMLResponse:
    random_post_id = await memecry.posts_service.get_random_post_id(
        viewer=request.user if request.user.is_authenticated else None
    )
    if random_post_id is None:
        return HTMLResponse(
            memecry.views.common.error_element("Could not find random post")
        )
    redirect_url = f"{request.url_of(get_post, post_id=random_post_id)}"
    return RedirectResponse(url=redirect_url)


@dataclass
class TagForm:
    tag: str
    tags: str = "no-tags"


@router.path_function(
    "PUT", "/posts/{post_id}/tags", auth_scopes=[AuthScope.Authenticated]
)
async def update_tags(
    request: memecry.schema.Request, post_id: PathInt
) -> HTMLResponse:
    async with request.parse_form(TagForm) as form:
        if post_id != 0:
            try:
                await memecry.posts_service.toggle_post_tag(
                    post_id, form.tag, request.user.id
                )
            except PermissionError:
                return HTMLResponse(
                    memecry.views.common.error_element("Permission denied"),
                    status_code=403,
                )
        else:
            old_tags = form.tags.split(", ")

            if form.tag in old_tags:
                old_tags.remove(form.tag)
                if old_tags == []:
                    old_tags = ["no tags"]
            else:
                if old_tags == ["no tags"]:
                    old_tags = []
                old_tags.append(form.tag)

        return HTMLResponse(input(value=form.tags, name="lol", type="text"))


@router.path_function(
    "PUT",
    "/posts/{post_id}/searchable-content",
    auth_scopes=[AuthScope.Authenticated],
)
async def update_searchable_content(
    request: memecry.schema.Request, post_id: PathInt
) -> Response:
    async with request.form() as form:
        new_content = cast(str, form[f"content-input-{post_id}"])
        await memecry.posts_service.update_post_searchable_content(
            post_id,
            new_content,
            user_id=request.user.id,
        )
    return Response("success")


@router.path_function(
    "PUT",
    "/posts/{post_id}/title",
    auth_scopes=[AuthScope.Authenticated],
)
async def update_title(request: memecry.schema.Request, post_id: PathInt) -> Response:
    async with request.form() as form:
        new_title = cast(str, form[f"title-{post_id}"])
        await memecry.posts_service.update_post_title(
            post_id, new_title, user_id=request.user.id
        )
    return Response("success")


@dataclass
class UploadForm:
    title: str
    file: UploadFile
    tags: str = "no-tags"
    searchable_content: str = ""


@router.path_function("POST", "/upload", auth_scopes=[AuthScope.Authenticated])
async def upload(request: memecry.schema.Request) -> Response:
    async with request.parse_form(UploadForm) as form_data:
        post_data = memecry.schema.PostCreate(
            title=form_data.title,
            tags=form_data.tags,
            searchable_content=form_data.searchable_content,
            user_id=request.user.id,
        )
        new_post_id = await memecry.posts_service.upload_post(
            post_data=post_data,
            uploaded_file=form_data.file,
        )

    resp = Response()
    resp.headers["HX-Redirect"] = f"/posts/{new_post_id}"
    resp.status_code = 201
    return resp


@router.path_function("GET", "/")
async def get_homepage(
    request: memecry.schema.Request,
    limit: QueryInt = 5,
    offset: QueryInt = 0,
) -> HTMLResponse:
    posts = await memecry.posts_service.get_posts(
        viewer=request.user if request.user.is_authenticated else None,
        limit=limit,
        offset=offset,
    )
    home_view = memecry.views.post.home_view(
        posts,
        offset=offset,
        limit=limit,
        keep_scrolling=True,
        partial=request.scope["from_htmx"],
    )
    if request.scope["from_htmx"]:
        return HTMLResponse(home_view)
    return HTMLResponse(
        memecry.views.misc.page_root(
            [
                memecry.views.misc.page_nav(
                    user=request.user if request.user.is_authenticated else None,
                ),
                memecry.views.misc.commands_helper(key="visibible", display_hack=False),
                home_view,
                memecry.views.misc.commands_helper(key="hidden", display_hack=True),
            ],
        ),
    )


@router.path_function("GET", "/search")
async def search_posts(
    request: memecry.schema.Request, query: QueryStr
) -> HTMLResponse | Response:
    logger = logging.getLogger()
    start_parse_query = time.time()
    try:
        parsed_query = memecry.schema.Query(query)
    except ValueError as e:
        return HTMLResponse(memecry.views.common.error_element(str(e)))
    logger.debug("Took %.2f seconds to parse query", time.time() - start_parse_query)

    posts = await memecry.posts_service.get_posts_by_search_query(
        parsed_query,
        viewer=request.user if request.user.is_authenticated else None,
        offset=0,
        limit=0,
    )
    start_build_home_view = time.time()
    home_view = memecry.views.post.home_view(
        posts,
        offset=0,
        limit=-1,
        keep_scrolling=False,
        partial=request.scope["from_htmx"],
    )
    logger.debug(
        "Took %.2f seconds to build home view", time.time() - start_build_home_view
    )
    return HTMLResponse(
        memecry.views.misc.page_root(
            [
                memecry.views.misc.page_nav(
                    user=request.user if request.user.is_authenticated else None,
                ),
                home_view,
            ],
        ),
    )


@router.path_function("DELETE", "/posts/{post_id}")
async def delete_post(_: memecry.schema.Request, post_id: PathInt) -> Response:
    await memecry.posts_service.delete_post(post_id)
    return Response("success")
