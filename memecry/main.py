from starlette.authentication import AuthCredentials, AuthenticationBackend
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import HTTPConnection
from starlette.responses import HTMLResponse

from memecry.views import common as common_views
from memecry.altair import App, AuthScope, QueryInt, PathInt, Request


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
        auth = conn.cookies["authorization"]
        scheme, credentials = auth.split()
        if scheme.lower() != "basic":
            return
        username, _, password = credentials.partition(":")
        if username != "" and password != "":
            return AuthCredentials([AuthScope.Authenticated]), SimpleUser(username)


app = App(middleware=[Middleware(AuthenticationMiddleware, backend=BasicAuthBackend)])
Request = Request[SimpleUser]


@app.get("/posts/{post_id}")
def get_post(request: Request, *, post_id: PathInt):
    # TODO:
    username = "anon"
    if request.scope["from_htmx"]:
        return HTMLResponse(common_views.post_view(post_id).render())
    return HTMLResponse(
        common_views.page_root(
            [common_views.page_nav(username), common_views.post_view(post_id)]
        ).render()
    )


@app.get("/", auth_scopes=[AuthScope.Authenticated])
def get_homepage(
    request: Request,
):
    reveal_type(request.user)
    if request.user.is_authenticated:
        username = request.user.display_name
    else:
        username = "anon"
    print(request.cookies)
    post_url_func = app.url_wrapper(get_post)
    resp = HTMLResponse(
        common_views.page_root(
            [
                common_views.page_nav(username),
                common_views.home_view(get_post_url=post_url_func),
            ]
        ).render()
    )
    return resp
