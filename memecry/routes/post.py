from dataclasses import dataclass
from typing import (
    Annotated,
    cast,
)

from relax.app import (
    AuthScope,
    FormData,
    HTMLResponse,
    PathInt,
    QueryInt,
    QueryStr,
    Router,
)
from relax.html import div
from starlette.datastructures import UploadFile
from starlette.responses import RedirectResponse, Response

import memecry.posts_service
import memecry.routes.auth
import memecry.schema
import memecry.types
import memecry.views.common
import memecry.views.misc
import memecry.views.post

router = Router()


@router.path_function("GET", "/posts/{post_id}")
async def get_post(request: memecry.types.Request, post_id: PathInt) -> HTMLResponse:
    post = await memecry.posts_service.get_post_by_id(
        post_id, viewer=request.user if request.user.is_authenticated else None
    )
    if post is None:
        return HTMLResponse(memecry.views.common.error_element("Post not found"))
    # TODO: honestly, I think I'd prefer request.from_htmx
    if request.scope["from_htmx"]:
        return HTMLResponse(memecry.views.post.post_component(post=post))
    return HTMLResponse(
        memecry.views.misc.page_root(
            [
                memecry.views.misc.page_nav(
                    user=request.user if request.user.is_authenticated else None,
                ),
                memecry.views.misc.commands_helper(key="visible", display_hack=False),
                div(classes=["md:w-[32rem]"]).insert(
                    memecry.views.post.post_component(post=post)
                ),
                memecry.views.misc.commands_helper(display_hack=True, key="hidden"),
            ],
        ),
    )


@router.path_function("GET", "/random")
async def random_post(
    request: memecry.types.Request,
) -> RedirectResponse | HTMLResponse:
    random_post_id = await memecry.posts_service.get_random_post_id(
        # TODO: find a nicer way to give the user
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
    request: memecry.types.Request,
    post_id: PathInt,
    form_data: FormData[TagForm],
) -> HTMLResponse:
    new_tag = form_data.tag
    old_tags_in_form = form_data.tags
    if post_id != 0:
        try:
            updated_tags = await memecry.posts_service.toggle_post_tag(
                post_id, new_tag, request.user.id
            )
        except PermissionError:
            return HTMLResponse(
                memecry.views.common.error_element("Permission denied"),
                status_code=403,
            )
    else:
        old_tags = old_tags_in_form.split(", ")

        if new_tag in old_tags:
            old_tags.remove(new_tag)
            if old_tags == []:
                old_tags = ["no tags"]
        else:
            if old_tags == ["no tags"]:
                old_tags = []
            old_tags.append(new_tag)

        updated_tags = ", ".join(old_tags)

    return HTMLResponse(
        memecry.views.post.tags_component(
            post_id=post_id,
            post_tags=updated_tags,
            editable=True,
            hidden_dropdown=False,
        ),
    )


@router.path_function(
    "PUT",
    "/posts/{post_id}/searchable-content",
    auth_scopes=[AuthScope.Authenticated],
)
# TODO: maybe better to have a single update endpoint?
async def update_searchable_content(
    request: memecry.types.Request, post_id: PathInt
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
async def update_title(request: memecry.types.Request, post_id: PathInt) -> Response:
    async with request.form() as form:
        new_title = cast(str, form[f"title-{post_id}"])
        await memecry.posts_service.update_post_title(
            post_id, new_title, user_id=request.user.id
        )
    return Response("success")


@router.path_function(
    "GET",
    "/upload-form",
    auth_scopes=[AuthScope.Authenticated],
)
async def upload_form(request: memecry.types.Request) -> HTMLResponse:
    if request.scope["from_htmx"]:
        return HTMLResponse(
            memecry.views.misc.upload_form(),
        )
    return HTMLResponse(
        memecry.views.misc.page_root(
            [
                memecry.views.misc.upload_form(),
            ],
        ),
    )


@dataclass
class UploadForm:
    title: str
    tags: str
    file: UploadFile
    searchable_content: str = ""


@router.path_function("POST", "/upload", auth_scopes=[AuthScope.Authenticated])
# TODO: the form should be unwrapped in the relax lib
async def upload(
    request: memecry.types.Request, form_data: Annotated[UploadForm, "form_data"]
) -> Response:
    post_data = memecry.schema.PostCreate(
        title=form_data.title,
        tags=form_data.tags,
        searchable_content=form_data.searchable_content,
        user_id=request.user.id,
    )
    new_post_id = await memecry.posts_service.upload_post(
        # TODO: why is the file in file.file???
        post_data=post_data,
        uploaded_file=form_data.file.file,  # type: ignore
    )
    resp = Response()
    resp.headers["HX-Redirect"] = f"/posts/{new_post_id}"
    resp.status_code = 201
    return resp


@router.path_function("GET", "/")
async def get_homepage(
    request: memecry.types.Request,
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
    request: memecry.types.Request, query: QueryStr
) -> HTMLResponse | Response:
    try:
        parsed_query = memecry.schema.Query(query)
    except ValueError as e:
        return HTMLResponse(memecry.views.common.error_element(str(e)))

    posts = await memecry.posts_service.get_posts_by_search_query(
        parsed_query,
        viewer=request.user if request.user.is_authenticated else None,
        offset=0,
        limit=0,
    )
    home_view = memecry.views.post.home_view(
        posts,
        offset=0,
        limit=-1,
        keep_scrolling=False,
        partial=request.scope["from_htmx"],
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
async def delete_post(_: memecry.types.Request, post_id: PathInt) -> Response:
    await memecry.posts_service.delete_post(post_id)
    return Response("success")
