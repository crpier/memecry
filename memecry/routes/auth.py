from dataclasses import dataclass
from typing import cast

from relax.app import AuthScope, HTMLResponse, Router
from relax.html import div
from relax.injection import Injected
from starlette.responses import Response

import memecry.config
import memecry.schema
import memecry.security
import memecry.user_service
import memecry.views.common
import memecry.views.misc
import memecry.views.post

router = Router()


# Signin
@router.path_function("POST", "/signin")
async def signin(request: memecry.schema.Request) -> HTMLResponse | Response:
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


@router.path_function("GET", "/signin-form")
async def signin_form(request: memecry.schema.Request) -> HTMLResponse:
    if request.scope["from_htmx"]:
        return HTMLResponse(memecry.views.misc.signin_form())
    return HTMLResponse(
        memecry.views.misc.page_root(memecry.views.misc.signin_form()),
    )


@router.path_function("GET", "/signup-form")
async def signup_form(request: memecry.schema.Request) -> HTMLResponse:
    if request.scope["from_htmx"]:
        return HTMLResponse(memecry.views.misc.signup_form(request.url_of(signup)))  # type: ignore
    return HTMLResponse(
        memecry.views.misc.page_root(
            memecry.views.misc.signup_form(request.url_of(signup)),  # type: ignore
        ),
    )


@dataclass
class SignupForm:
    username: str
    password: str


@router.path_function("POST", "/signup")
async def signup(
    request: memecry.schema.Request,
    *,
    config: memecry.config.Config = Injected,
) -> HTMLResponse:
    if not config.ALLOW_SIGNUPS:
        return HTMLResponse(
            memecry.views.common.error_element(
                "Signups not allowed",
            ),
        )
    async with request.parse_form(SignupForm) as form_data:
        user_create = memecry.schema.UserCreate(
            username=form_data.username, password=form_data.password
        )
        new_user_id = await memecry.user_service.create_user(user_create)
        if new_user_id is None:
            return HTMLResponse(
                memecry.views.common.error_element(
                    f'Username "{form_data.username}" already exists',
                ),
            )
        access_token = await memecry.security.create_access_token(
            data={"sub": form_data.username}
        )
    resp = HTMLResponse(div())
    resp.set_cookie(key="authorization", value=access_token, httponly=True)
    resp.headers["HX-Refresh"] = "true"
    resp.status_code = 303
    return resp


# Signout
@router.path_function(
    "GET",
    "/signout",
    auth_scopes=[AuthScope.Authenticated],
)
async def signout(_: memecry.schema.Request) -> Response:
    response = Response()
    response.delete_cookie(key="authorization")
    response.headers["HX-Refresh"] = "true"
    response.status_code = 303
    return response
