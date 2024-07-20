from jose import ExpiredSignatureError
from relax.app import (
    App,
    AuthScope,
    websocket_endpoint,
)
from relax.server import start_app
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    UnauthenticatedUser,
)
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import HTTPConnection
from starlette.requests import Request as BaseRequest
from starlette.responses import Response
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from starlette.types import Scope

import memecry.bootstrap
import memecry.config
import memecry.posts_service
import memecry.routes.auth
import memecry.routes.misc
import memecry.routes.post
import memecry.schema
import memecry.security
import memecry.user_service


class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(
        self,
        conn: HTTPConnection,
    ) -> tuple[AuthCredentials, memecry.schema.UserRead] | None:
        if "authorization" not in conn.cookies:
            return None
        token = conn.cookies["authorization"]
        try:
            payload = await memecry.security.decode_token(token)
        except ExpiredSignatureError:
            return None
        if (username := payload.get("sub")) is None:
            return None

        if user := await memecry.user_service.get_user_by_username(username):
            return AuthCredentials(
                [AuthScope.Authenticated]
            ), memecry.schema.UserRead.model_validate(
                user,
            )
        return None


class AuthRequiredMiddlerware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: BaseRequest, call_next: RequestResponseEndpoint
    ) -> Response:
        if not request.user.is_authenticated:
            return Response("Not authenticated", status_code=403)
        return await call_next(request)


class RestrictedAccessStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope: Scope) -> Response:
        if isinstance(scope["user"], UnauthenticatedUser):
            authenticated_viewer = False
        else:
            authenticated_viewer = True
        post = await memecry.posts_service.get_post_by_media_path(
            path="/media/" + path, authenticated_viewer=authenticated_viewer
        )
        if post is not None:
            return await super().get_response(path, scope)
        return Response("Not found", status_code=404)


def app_factory() -> App:
    config, view_context = memecry.bootstrap.bootstrap()
    middleware = Middleware(AuthenticationMiddleware, backend=BasicAuthBackend())
    app = App(
        middleware=[middleware],
        config=config,
        view_context=view_context,
    )

    app.add_router(memecry.routes.auth.router)
    app.add_router(memecry.routes.post.router)
    app.add_router(memecry.routes.misc.router)
    app.add_websocket_route("/ws", websocket_endpoint, name="ws")
    app.routes.append(
        Mount(
            "/media",
            app=RestrictedAccessStaticFiles(directory=config.MEDIA_UPLOAD_STORAGE),
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

    if config.ENV == "DEV":
        app.listen_to_template_changes()
    return app


# This runs in a different process
if __name__ == "__main__":
    config = memecry.config.Config()
    start_app(
        app_path="memecry.main:app_factory",
        config=config,
        reload=config.ENV == "DEV",
        host="0.0.0.0",  # noqa: S104
    )
