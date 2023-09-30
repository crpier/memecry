from typing import cast
import contextlib
from jose import ExpiredSignatureError
import jose.jwt

from starlette.authentication import AuthCredentials, AuthenticationBackend
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import HTTPConnection
from starlette.responses import HTMLResponse, Response
from starlette.exceptions import HTTPException
from memecry.schema import UserCreate

from memecry.views import common as common_views
from yahgl_py.app import App, AuthScope, PathInt, Request
import memecry.user_service as user_service
from memecry.depends import bootstrap
import memecry.security as security


from starlette.authentication import (
    SimpleUser,
    AuthCredentials,
)


class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(
        self,
        conn: HTTPConnection,
    ) -> tuple[AuthCredentials, SimpleUser] | None:
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
            return AuthCredentials([AuthScope.Authenticated]), SimpleUser(user.username)


@contextlib.asynccontextmanager
async def lifespan(_: App):
    await bootstrap()
    yield


app = App(
    middleware=[Middleware(AuthenticationMiddleware, backend=BasicAuthBackend())],
    lifespan=lifespan,
)
Request = Request[SimpleUser]


@app.get("/posts/{post_id}")
async def get_post(request: Request, *, post_id: PathInt):
    username = "anon"
    if request.scope["from_htmx"]:
        return HTMLResponse(
            common_views.posts_wrapper(common_views.post_partial_view(post_id)).render()
        )
    return HTMLResponse(
        common_views.page_root(
            [
                common_views.page_nav(
                    app.url_wrapper(signup_form), app.url_wrapper(signup_form), username
                ),
                common_views.posts_wrapper(common_views.post_partial_view(post_id)),
            ]
        ).render()
    )


@app.get("/")
async def get_homepage(
    request: Request,
):
    if request.user.is_authenticated:
        username = request.user.display_name
    else:
        username = "anon"
    resp = HTMLResponse(
        common_views.page_root(
            [
                common_views.page_nav(
                    app.url_wrapper(signup_form), app.url_wrapper(signup_form), username
                ),
                common_views.home_view(1),
            ]
        ).render()
    )
    return resp


@app.get("/signup-form")
async def signup_form(request: Request):
    if request.scope["from_htmx"]:
        return HTMLResponse(common_views.signup_form(app.url_wrapper(signup)).render())
    return HTMLResponse(
        common_views.page_root(
            [common_views.signup_form(app.url_wrapper(signup))]
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
async def signout(request: Request):
    response = Response()
    response.delete_cookie(key="authorization")
    response.headers["HX-Refresh"] = "true"
    response.status_code = 303
    return response
