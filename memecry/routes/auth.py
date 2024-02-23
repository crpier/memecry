from typing import Protocol, cast

from relax.app import AuthScope, HTMLResponse, RelaxRoute
from relax.html import div
from starlette.datastructures import URL
from starlette.responses import Response

import memecry.schema
import memecry.security
import memecry.types
import memecry.user_service
import memecry.views.common
import memecry.views.misc
import memecry.views.post


class SigninSig(Protocol):
    def __call__(self) -> URL:
        ...


# Signin
async def signin(request: memecry.types.Request) -> HTMLResponse | Response:
    async with request.form() as form:
        # lolwtf
        username = cast(str, form["username"])
        password = cast(str, form["password"])
        if await memecry.user_service.authenticate_user(username, password) is None:
            return HTMLResponse(
                memecry.views.common.error_element("Invalid username or password"),
            )
        resp = Response()
        access_token = await memecry.security.create_access_token(
            data={"sub": username}
        )
        resp.set_cookie(key="authorization", value=access_token, httponly=True)
        resp.headers["HX-Refresh"] = "true"
        resp.status_code = 303
        return resp


class SigninFormSig(Protocol):
    def __call__(self) -> URL:
        ...


async def signin_form(request: memecry.types.Request) -> HTMLResponse:
    if request.scope["from_htmx"]:
        return HTMLResponse(memecry.views.misc.signin_form())
    return HTMLResponse(
        memecry.views.misc.page_root(memecry.views.misc.signin_form()),
    )


class SignupFormSig(Protocol):
    def __call__(self) -> URL:
        ...


# Signup
async def signup_form(request: memecry.types.Request) -> HTMLResponse:
    if request.scope["from_htmx"]:
        return HTMLResponse(memecry.views.misc.signup_form(request.url_of(signup)))
    return HTMLResponse(
        memecry.views.misc.page_root(
            memecry.views.misc.signup_form(request.url_of(signup)),
        ),
    )


class SignupSig(Protocol):
    def __call__(self) -> URL:
        ...


async def signup(request: memecry.types.Request) -> HTMLResponse:
    async with request.form() as form:
        # lolwtf
        username = cast(str, form["username"])
        password = cast(str, form["password"])
        user_create = memecry.schema.UserCreate(username=username, password=password)
        new_user_id = await memecry.user_service.create_user(user_create)
        if new_user_id is None:
            return HTMLResponse(
                memecry.views.common.error_element(
                    f'Username "{username}" already exists',
                ),
            )
        access_token = await memecry.security.create_access_token(
            data={"sub": username}
        )
        resp = HTMLResponse(div())
        resp.set_cookie(key="authorization", value=access_token, httponly=True)
        resp.headers["HX-Refresh"] = "true"
        resp.status_code = 303
        return resp


class SignoutSig(Protocol):
    def __call__(self) -> URL:
        ...


# Signout
async def signout(_: memecry.types.Request) -> Response:
    response = Response()
    response.delete_cookie(key="authorization")
    response.headers["HX-Refresh"] = "true"
    response.status_code = 303
    return response


routes = [
    RelaxRoute("/signin", "POST", signin, sig=SigninSig),
    RelaxRoute("/signup", "POST", signup, sig=SignupSig),
    RelaxRoute("/signin-form", "GET", signin_form, sig=SigninFormSig),
    RelaxRoute("/signup-form", "GET", signup_form, sig=SignupFormSig),
    RelaxRoute(
        "/signout",
        "GET",
        signout,
        auth_scopes=[AuthScope.Authenticated],
        sig=SignoutSig,
    ),
]
