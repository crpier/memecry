from typing import cast

from relax.app import AuthScope, HTMLResponse, Router
from relax.html import div
from starlette.responses import Response

import memecry.schema
from memecry import security, user_service
from memecry.types import Request
from memecry.views import common as common_views

auth_router = Router()


# Signin
@auth_router.path_function("POST", "/signin")
async def signin(request: Request) -> HTMLResponse | Response:
    async with request.form() as form:
        # lolwtf
        username = cast(str, form["username"])
        password = cast(str, form["password"])
        if await user_service.authenticate_user(username, password) is None:
            return HTMLResponse(
                common_views.error_element("Invalid username or password"),
            )
        resp = Response()
        access_token = await security.create_access_token(data={"sub": username})
        resp.set_cookie(key="authorization", value=access_token, httponly=True)
        resp.headers["HX-Refresh"] = "true"
        resp.status_code = 303
        return resp


@auth_router.path_function("GET", "/signin-form")
async def signin_form(request: Request) -> HTMLResponse:
    if request.scope["from_htmx"]:
        return HTMLResponse(common_views.signin_form(request.url_of(signin)))
    return HTMLResponse(
        common_views.page_root(common_views.signin_form(request.url_of(signin))),
    )


# Signup
@auth_router.path_function("GET", "/signup-form")
async def signup_form(request: Request) -> HTMLResponse:
    if request.scope["from_htmx"]:
        return HTMLResponse(common_views.signup_form(request.url_of(signup)))
    return HTMLResponse(
        common_views.page_root(
            common_views.signup_form(request.url_of(signup)),
        ),
    )


@auth_router.path_function("POST", "/signup")
async def signup(request: Request) -> HTMLResponse:
    async with request.form() as form:
        # lolwtf
        username = cast(str, form["username"])
        password = cast(str, form["password"])
        user_create = memecry.schema.UserCreate(username=username, password=password)
        new_user_id = await user_service.create_user(user_create)
        if new_user_id is None:
            return HTMLResponse(
                common_views.error_element(
                    f'Username "{username}" already exists',
                ),
            )
        access_token = await security.create_access_token(data={"sub": username})
        resp = HTMLResponse(div())
        resp.set_cookie(key="authorization", value=access_token, httponly=True)
        resp.headers["HX-Refresh"] = "true"
        resp.status_code = 303
        return resp


# Signout
@auth_router.path_function("GET", "/signout", auth_scopes=[AuthScope.Authenticated])
async def signout(_: Request) -> Response:
    response = Response()
    response.delete_cookie(key="authorization")
    response.headers["HX-Refresh"] = "true"
    response.status_code = 303
    return response
