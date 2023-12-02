from typing import cast

from relax.app import AuthScope, HTMLResponse, PathInt, Router
from relax.html import div
from starlette.datastructures import UploadFile
from starlette.responses import Response

import memecry.posts_service
import memecry.routes.auth
import memecry.schema
import memecry.views.common
import memecry.views.misc
import memecry.views.post
from memecry.types import Request

post_router = Router()


@post_router.path_function("GET", "/posts/{post_id}")
async def get_post(request: Request, post_id: PathInt) -> HTMLResponse:
    _ = request, post_id
    # TODO: lol
    return HTMLResponse(div().text("lol"))


@post_router.path_function(
    "PUT",
    "/posts/{post_id}/tags",
    auth_scopes=[AuthScope.Authenticated],
)
# TODO: at runtime, post_id is actually an string
async def update_tags(request: Request, post_id: PathInt) -> HTMLResponse:
    async with request.form() as form:
        new_tag = cast(str, form["tag"])
        old_tags_in_form = cast(str, form.get("tags", "no tags"))
        if post_id != 0:
            try:
                updated_tags = await memecry.posts_service.toggle_post_tag(
                    post_id, new_tag, request.user.id
                )
            except PermissionError:
                return HTMLResponse(div().text("Permission denied"), status_code=403)
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
                post_update_tags_url=request.url_wrapper(update_tags),
                post_id=post_id,
                post_tags=updated_tags,
                editable=True,
                hidden_dropdown=False,
            ),
        )


@post_router.path_function(
    "PUT",
    "/posts/{post_id}/searchable-content",
    auth_scopes=[AuthScope.Authenticated],
)
async def update_searchable_content(request: Request, post_id: PathInt) -> Response:
    async with request.form() as form:
        new_content = cast(str, form[f"content-input-{post_id}"])
        await memecry.posts_service.update_post_searchable_content(
            post_id,
            new_content,
            user_id=request.user.id,
        )
    return Response("success")


@post_router.path_function(
    "PUT",
    "/posts/{post_id}/title",
    auth_scopes=[AuthScope.Authenticated],
)
async def update_title(request: Request, post_id: PathInt) -> Response:
    async with request.form() as form:
        new_title = cast(str, form[f"title-{post_id}"])
        await memecry.posts_service.update_post_title(
            post_id, new_title, user_id=request.user.id
        )
    return Response("success")


@post_router.path_function(
    "DELETE", "/posts/{post_id}", auth_scopes=[AuthScope.Authenticated]
)
async def post_delete(_: Request, post_id: PathInt) -> Response:
    await memecry.posts_service.delete_post(post_id)
    return Response("success")


@post_router.path_function("GET", "/upload-form", auth_scopes=[AuthScope.Authenticated])
async def upload_form(request: Request) -> HTMLResponse:
    if request.scope["from_htmx"]:
        return HTMLResponse(
            memecry.views.misc.upload_form(
                request.url_of(upload),
                # TODO: encode somewhere the post_id=0 magic spell
                request.url_wrapper(update_tags),
            ),
        )
    return HTMLResponse(
        memecry.views.misc.page_root(
            [
                memecry.views.misc.upload_form(
                    request.url_of(upload),
                    request.url_wrapper(update_tags),
                ),
            ],
        ),
    )


@post_router.path_function("POST", "/upload", auth_scopes=[AuthScope.Authenticated])
async def upload(request: Request) -> Response:
    async with request.form() as form:
        title = cast(str, form["title"])
        tags = cast(str, form["tags"])
        file = cast(UploadFile, form["file"])
        try:
            searchable_content = cast(str, form["searchable-content"])
        except KeyError:
            searchable_content = ""

        post_data = memecry.schema.PostCreate(
            title=title,
            user_id=request.user.id,
            tags=tags,
            searchable_content=searchable_content,
        )
        new_post_id = await memecry.posts_service.upload_post(
            post_data=post_data, uploaded_file=file
        )
    resp = Response()
    resp.headers["HX-Redirect"] = f"/posts/{new_post_id}"
    resp.status_code = 201
    return resp
