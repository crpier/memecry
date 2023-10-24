import contextlib
from typing import AsyncIterator, TypeAlias, cast

from jose import ExpiredSignatureError
from relax.app import App, AuthScope, PathInt, QueryStr
from relax.app import Request as BaseRequest
from starlette.authentication import AuthCredentials, AuthenticationBackend
from starlette.datastructures import UploadFile
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import HTTPConnection
from starlette.responses import HTMLResponse, Response
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from memecry import security, user_service
from memecry.bootstrap import bootstrap
from memecry.posts_service import (
    delete_post,
    get_post_by_id,
    get_posts,
    get_posts_by_search_query,
    toggle_post_tag,
    update_post_searchable_content,
    update_post_title,
    upload_post,
)
from memecry.schema import PostCreate, UserCreate, UserRead
from memecry.views import common as common_views


class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(
        self,
        conn: HTTPConnection,
    ) -> tuple[AuthCredentials, UserRead] | None:
        if "authorization" not in conn.cookies:
            return None
        token = conn.cookies["authorization"]
        try:
            payload = await security.decode_payload(token)
        except ExpiredSignatureError:
            return None
        if payload.get("sub") is None:
            return None
        username: str = cast(str, payload.get("sub"))
        if user := await user_service.get_user_by_username(username):
            return AuthCredentials([AuthScope.Authenticated]), UserRead.model_validate(
                user,
            )
        return None


@contextlib.asynccontextmanager
async def lifespan(app: App) -> AsyncIterator[None]:
    config = await bootstrap()
    app.routes.append(
        Mount(
            "/media",
            app=StaticFiles(directory=config.MEDIA_UPLOAD_STORAGE),
            name="media",
        ),
    )
    app.routes.append(
        Mount(
            "/static",
            app=StaticFiles(directory="static"),
            name="static",
        ),
    )
    app.routes.append(
        Mount(
            "/",
            app=StaticFiles(directory="static/favicon"),
            name="favicon",
        ),
    )
    yield


app = App(
    middleware=[Middleware(AuthenticationMiddleware, backend=BasicAuthBackend())],
    lifespan=lifespan,
)
Request: TypeAlias = BaseRequest[UserRead]


@app.get("/posts/{post_id}")
async def get_post(request: Request, *, post_id: PathInt) -> HTMLResponse:
    post = await get_post_by_id(
        post_id,
        viewer=request.user if request.user.is_authenticated else None,
    )
    if not post:
        return HTMLResponse(common_views.response_404().render())
    if request.scope["from_htmx"]:
        return HTMLResponse(
            common_views.posts_wrapper(
                common_views.post_component(
                    post_update_tags_url=app.url_wrapper(update_tags),
                    post_url=app.url_wrapper(get_post),
                    update_searchable_content_url=app.url_wrapper(
                        update_searchable_content,
                    ),
                    post=post,
                ),
            ).render(),
        )
    return HTMLResponse(
        common_views.page_root(
            [
                common_views.page_nav(
                    signup_url=app.url_wrapper(signup_form),
                    signin_url=app.url_wrapper(signin_form),
                    signout_url=app.url_wrapper(signout),
                    upload_form_url=app.url_wrapper(upload_form),
                    user=request.user if request.user.is_authenticated else None,
                ),
                common_views.posts_wrapper(
                    common_views.post_component(
                        post_update_tags_url=app.url_wrapper(update_tags),
                        post_url=app.url_wrapper(get_post),
                        update_searchable_content_url=app.url_wrapper(
                            update_searchable_content,
                        ),
                        post=post,
                    ),
                ),
            ],
        ).render(),
    )


@app.put("/posts/{post_id}/tags", auth_scopes=[AuthScope.Authenticated])
# FIXME: at runtime, post_id is actually an string
async def update_tags(request: Request, *, post_id: PathInt) -> Response | HTMLResponse:
    async with request.form() as form:
        new_tag = cast(str, form["tag"])
        old_tags_in_form = cast(str, form.get("tags", "no tags"))
        if int(post_id) != 0:
            try:
                updated_tags = await toggle_post_tag(post_id, new_tag, request.user.id)
            except PermissionError:
                return Response("permission denied", status_code=403)
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
            common_views.tags_component(
                app.url_wrapper(update_tags),
                post_id,
                updated_tags,
                editable=True,
                hidden_dropdown=False,
            ).render(),
        )


@app.put("/posts/{post_id}/searchable-content", auth_scopes=[AuthScope.Authenticated])
async def update_searchable_content(request: Request, *, post_id: PathInt) -> Response:
    async with request.form() as form:
        new_content = cast(str, form[f"content-input-{post_id}"])
        await update_post_searchable_content(
            post_id,
            new_content,
            user_id=request.user.id,
        )
    return Response("success")


@app.put("/posts/{post_id}/title", auth_scopes=[AuthScope.Authenticated])
async def update_title(request: Request, *, post_id: PathInt) -> Response:
    async with request.form() as form:
        new_title = cast(str, form[f"title-{post_id}"])
        await update_post_title(post_id, new_title, user_id=request.user.id)
    return Response("success")


@app.delete("/posts/{post_id}", auth_scopes=[AuthScope.Authenticated])
async def post_delete(_: Request, *, post_id: PathInt) -> Response:
    await delete_post(post_id)
    return Response("success")


@app.get("/")
async def get_homepage(request: Request, query: QueryStr | None = None) -> HTMLResponse:
    if query:
        posts = await get_posts_by_search_query(
            query,
            viewer=request.user if request.user.is_authenticated else None,
        )
    else:
        posts = await get_posts(
            viewer=request.user if request.user.is_authenticated else None,
        )
    return HTMLResponse(
        common_views.page_root(
            [
                common_views.page_nav(
                    signup_url=app.url_wrapper(signup_form),
                    signin_url=app.url_wrapper(signin_form),
                    signout_url=app.url_wrapper(signout),
                    upload_form_url=app.url_wrapper(upload_form),
                    user=request.user if request.user.is_authenticated else None,
                ),
                common_views.home_view(
                    app.url_wrapper(update_tags),
                    app.url_wrapper(get_post),
                    app.url_wrapper(
                        update_searchable_content,
                    ),
                    posts,
                ),
            ],
        ).render(),
    )


@app.get("/upload-form", auth_scopes=[AuthScope.Authenticated])
async def upload_form(request: Request) -> HTMLResponse:
    if request.scope["from_htmx"]:
        return HTMLResponse(
            common_views.upload_form(
                app.url_wrapper(upload),
                app.url_wrapper(update_tags),
            ).render(),
        )
    return HTMLResponse(
        common_views.page_root(
            [
                common_views.upload_form(
                    app.url_wrapper(upload),
                    app.url_wrapper(update_tags),
                ),
            ],
        ).render(),
    )


@app.post("/upload", auth_scopes=[AuthScope.Authenticated])
async def upload(request: Request) -> Response:
    async with request.form() as form:
        title = cast(str, form["title"])
        tags = cast(str, form["tags"])
        file = cast(UploadFile, form["file"])
        try:
            searchable_content = cast(str, form["searchable-content"])
        except KeyError:
            searchable_content = ""

        post_data = PostCreate(
            title=title,
            user_id=request.user.id,
            tags=tags,
            searchable_content=searchable_content,
        )
        new_post_id = await upload_post(post_data=post_data, uploaded_file=file)
    resp = Response()
    resp.headers["HX-Redirect"] = f"/posts/{new_post_id}"
    resp.status_code = 201
    return resp


@app.get("/signup-form")
async def signup_form(request: Request) -> HTMLResponse:
    if request.scope["from_htmx"]:
        return HTMLResponse(common_views.signup_form(app.url_wrapper(signup)).render())
    return HTMLResponse(
        common_views.page_root(
            [common_views.signup_form(app.url_wrapper(signup))],
        ).render(),
    )


@app.get("/signin-form")
async def signin_form(request: Request) -> HTMLResponse:
    if request.scope["from_htmx"]:
        return HTMLResponse(common_views.signin_form(app.url_wrapper(signin)).render())
    return HTMLResponse(
        common_views.page_root(
            common_views.signin_form(app.url_wrapper(signin)),
        ).render(),
    )


@app.post("/signup")
async def signup(request: Request) -> HTMLResponse:
    async with request.form() as form:
        # lolwtf
        username = cast(str, form["username"])
        password = cast(str, form["password"])
        user_create = UserCreate(username=username, password=password)
        new_user_id = await user_service.create_user(user_create)
        if new_user_id is None:
            return HTMLResponse(
                common_views.error_element(
                    f'Username "{username}" already exists',
                ).render(),
            )
        access_token = await security.create_access_token(data={"sub": username})
        resp = HTMLResponse()
        resp.set_cookie(key="authorization", value=access_token, httponly=True)
        resp.headers["HX-Refresh"] = "true"
        resp.status_code = 303
        return resp


@app.post("/signin")
async def signin(request: Request) -> HTMLResponse | Response:
    async with request.form() as form:
        # lolwtf
        username = cast(str, form["username"])
        password = cast(str, form["password"])
        if await user_service.authenticate_user(username, password) is None:
            return HTMLResponse(
                common_views.error_element("Invalid username or password").render(),
            )
        resp = Response()
        access_token = await security.create_access_token(data={"sub": username})
        resp.set_cookie(key="authorization", value=access_token, httponly=True)
        resp.headers["HX-Refresh"] = "true"
        resp.status_code = 303
        return resp


@app.get("/signout", auth_scopes=[AuthScope.Authenticated])
async def signout(_: Request) -> Response:
    response = Response()
    response.delete_cookie(key="authorization")
    response.headers["HX-Refresh"] = "true"
    response.status_code = 303
    return response
