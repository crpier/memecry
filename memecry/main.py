from typing import cast
import contextlib
from jose import ExpiredSignatureError
import jose.jwt

from starlette.authentication import AuthCredentials, AuthenticationBackend
from starlette.datastructures import UploadFile
from starlette.middleware import Middleware
from starlette.routing import Mount
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import HTTPConnection
from starlette.responses import HTMLResponse, Response
from starlette.exceptions import HTTPException
from starlette.staticfiles import StaticFiles
from memecry.posts_service import (
    get_post_by_id,
    toggle_post_tag,
    upload_post,
    get_posts,
)
from memecry.schema import PostCreate, UserCreate, UserRead

from memecry.views import common as common_views
from yahgl_py.app import App, AuthScope, PathInt, Request
import memecry.user_service as user_service
from memecry.depends import bootstrap
import memecry.security as security


from starlette.authentication import (
    AuthCredentials,
)


class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(
        self,
        conn: HTTPConnection,
    ) -> tuple[AuthCredentials, UserRead] | None:
        if "authorization" not in conn.cookies:
            return
        token = conn.cookies["authorization"]
        try:
            payload = jose.jwt.decode(token, "abcd", algorithms=["HS256"])
        except ExpiredSignatureError:
            return None
        if payload.get("sub") is None:
            return None
        username: str = cast(str, payload.get("sub"))
        if user := await user_service.get_user_by_username(username):
            return AuthCredentials([AuthScope.Authenticated]), UserRead.model_validate(
                user
            )


@contextlib.asynccontextmanager
async def lifespan(_: App):
    await bootstrap()
    yield


app = App(
    middleware=[Middleware(AuthenticationMiddleware, backend=BasicAuthBackend())],
    lifespan=lifespan,
)
Request = Request[UserRead]

app.routes.append(
    Mount("/media", app=StaticFiles(directory="testdata/media"), name="media")
)


@app.get("/posts/{post_id}")
async def get_post(request: Request, *, post_id: PathInt):
    post = await get_post_by_id(post_id)
    if not post:
        return HTMLResponse(common_views.response_404().render())
    if request.scope["from_htmx"]:
        return HTMLResponse(
            common_views.posts_wrapper(
                common_views.post_component(app.url_wrapper(update_tags), post)
            ).render()
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
                    common_views.post_component(app.url_wrapper(update_tags), post)
                ),
            ]
        ).render()
    )


@app.put("/posts/{post_id}/tags")
async def update_tags(request: Request, *, post_id: PathInt):
    body = await request.body()
    new_tag = body.decode().split("=", 1)[1]
    print(new_tag)
    updated_tags = await toggle_post_tag(post_id, new_tag)
    return HTMLResponse(
        common_views.tags_component(
            app.url_wrapper(update_tags), post_id, updated_tags, hidden_dropdown=False
        ).render()
    )


@app.get("/")
async def get_homepage(
    request: Request,
):
    posts = await get_posts()
    resp = HTMLResponse(
        common_views.page_root(
            [
                common_views.page_nav(
                    signup_url=app.url_wrapper(signup_form),
                    signin_url=app.url_wrapper(signin_form),
                    signout_url=app.url_wrapper(signout),
                    upload_form_url=app.url_wrapper(upload_form),
                    user=request.user if request.user.is_authenticated else None,
                ),
                common_views.home_view(app.url_wrapper(update_tags), posts),
            ]
        ).render()
    )
    return resp


@app.get("/upload-form")
async def upload_form(request: Request):
    if request.scope["from_htmx"]:
        return HTMLResponse(
            common_views.upload_form(
                app.url_wrapper(upload), app.url_wrapper(update_tags)
            ).render()
        )
    return HTMLResponse(
        common_views.page_root(
            [
                common_views.upload_form(
                    app.url_wrapper(upload), app.url_wrapper(update_tags)
                )
            ]
        ).render()
    )


@app.post("/upload", auth_scopes=[AuthScope.Authenticated])
async def upload(request: Request):
    async with request.form() as form:
        title = cast(str, form["title"])
        tags = cast(str, form["tags"])
        file = cast(UploadFile, form["file"])

        post_data = PostCreate(
            title=title,
            user_id=request.user.id,
            tags=tags,
        )
        new_post_id = await upload_post(post_data=post_data, uploaded_file=file)
        print(new_post_id)
    # TODO: redirect to new post
    return Response(f"new post has id = {new_post_id=}")


@app.get("/signup-form")
async def signup_form(request: Request):
    if request.scope["from_htmx"]:
        return HTMLResponse(common_views.signup_form(app.url_wrapper(signup)).render())
    return HTMLResponse(
        common_views.page_root(
            [common_views.signup_form(app.url_wrapper(signup))]
        ).render()
    )


@app.get("/signin-form")
async def signin_form(request: Request):
    if request.scope["from_htmx"]:
        return HTMLResponse(common_views.signin_form(app.url_wrapper(signin)).render())
    return HTMLResponse(
        common_views.page_root(
            common_views.signin_form(app.url_wrapper(signin))
        ).render()
    )


@app.post("/signup")
async def signup(request: Request):
    async with request.form() as form:
        # lolwtf
        username = cast(str, form["username"])
        password = cast(str, form["password"])
        user_create = UserCreate(username=username, password=password)
        new_user_id = await user_service.create_user(user_create)
        if new_user_id is None:
            raise HTTPException(400, "Username already taken")
        access_token = security.create_access_token(data={"sub": username})
        resp = HTMLResponse()
        resp.set_cookie(key="authorization", value=access_token, httponly=True)
        resp.headers["HX-Refresh"] = "true"
        resp.status_code = 303
        return resp


@app.post("/signin")
async def signin(request: Request):
    async with request.form() as form:
        # lolwtf
        username = cast(str, form["username"])
        password = cast(str, form["password"])
        if await user_service.authenticate_user(username, password) is None:
            raise HTTPException(
                401, "Invalid username or password", {"WWW-Authenticate": "Bearer"}
            )
        resp = Response()
        access_token = security.create_access_token(data={"sub": username})
        resp.set_cookie(key="authorization", value=access_token, httponly=True)
        resp.headers["HX-Refresh"] = "true"
        resp.status_code = 303
        return resp


@app.get("/signout")
async def signout(_: Request):
    response = Response()
    response.delete_cookie(key="authorization")
    response.headers["HX-Refresh"] = "true"
    response.status_code = 303
    return response
