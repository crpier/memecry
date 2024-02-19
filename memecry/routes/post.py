from typing import (
    Protocol,
    cast,
)

from relax.app import AuthScope, HTMLResponse, PathInt, RelaxRoute
from relax.html import div
from starlette.datastructures import URL, UploadFile
from starlette.responses import Response

import memecry.posts_service
import memecry.routes.auth
import memecry.schema
import memecry.types
import memecry.views.common
import memecry.views.misc
import memecry.views.post


async def get_post(request: memecry.types.Request, post_id: PathInt) -> HTMLResponse:
    _ = request, post_id
    # TODO: lol
    return HTMLResponse(div().text("lol"))


class UpdateTags(Protocol):
    def __call__(self, post_id: int) -> URL:
        ...


async def update_tags(request: memecry.types.Request, post_id: PathInt) -> HTMLResponse:
    async with request.form() as form:
        new_tag = cast(str, form["tag"])
        old_tags_in_form = cast(str, form.get("tags", "no-tags"))
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


class UpdateSearchableContent(Protocol):
    def __call__(self, post_id: int) -> URL:
        ...


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


async def update_title(request: memecry.types.Request, post_id: PathInt) -> Response:
    async with request.form() as form:
        new_title = cast(str, form[f"title-{post_id}"])
        await memecry.posts_service.update_post_title(
            post_id, new_title, user_id=request.user.id
        )
    return Response("success")


class DeletePost(Protocol):
    def __call__(self, post_id: int) -> URL:
        ...


async def delete_post(_: memecry.types.Request, post_id: PathInt) -> Response:
    await memecry.posts_service.delete_post(post_id)
    return Response("success")


async def upload_form(request: memecry.types.Request) -> HTMLResponse:
    if request.scope["from_htmx"]:
        return HTMLResponse(
            memecry.views.misc.upload_form(
                request.url_of(upload),
                # TODO: encode somewhere the post_id=0 magic spell
            ),
        )
    return HTMLResponse(
        memecry.views.misc.page_root(
            [
                memecry.views.misc.upload_form(
                    request.url_of(upload),
                ),
            ],
        ),
    )


# TODO: the form should be unwrapped in the relax lib
async def upload(request: memecry.types.Request) -> Response:
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


routes = [
    RelaxRoute(
        "/upload",
        "POST",
        upload,
        auth_scopes=[AuthScope.Authenticated],
    ),
    RelaxRoute(
        "/posts/{post_id}/tags",
        "PUT",
        update_tags,
        auth_scopes=[AuthScope.Authenticated],
        sig=UpdateTags,
    ),
    RelaxRoute(
        "/posts/{post_id}",
        "DELETE",
        delete_post,
        sig=DeletePost,
        auth_scopes=[AuthScope.Authenticated],
    ),
    RelaxRoute("/posts/{post_id}", "GET", get_post),
    RelaxRoute(
        "/posts/{post_id}/searchable-content",
        "PUT",
        update_searchable_content,
        sig=UpdateSearchableContent,
        auth_scopes=[AuthScope.Authenticated],
    ),
    RelaxRoute(
        "/posts/{post_id}/title",
        "PUT",
        update_title,
        auth_scopes=[AuthScope.Authenticated],
    ),
    RelaxRoute(
        "/upload-form", "GET", upload_form, auth_scopes=[AuthScope.Authenticated]
    ),
]
