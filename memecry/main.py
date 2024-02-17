import contextlib
from typing import AsyncIterator, cast

from jose import ExpiredSignatureError
from relax.app import App, AuthScope
from starlette.authentication import AuthCredentials, AuthenticationBackend
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import HTTPConnection
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

import memecry.bootstrap
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
            payload = await memecry.security.decode_payload(token)
        except ExpiredSignatureError:
            return None
        if (username := cast(str, payload.get("sub"))) is None:
            return None

        if user := await memecry.user_service.get_user_by_username(username):
            return AuthCredentials(
                [AuthScope.Authenticated]
            ), memecry.schema.UserRead.model_validate(
                user,
            )
        return None


@contextlib.asynccontextmanager
async def lifespan(app: App) -> AsyncIterator[None]:
    config = await memecry.bootstrap.bootstrap(app)
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


# TODO: try making routes a simple list again
app.add_routes(memecry.routes.auth.routes)
app.add_routes(memecry.routes.misc.routes)
app.add_routes(memecry.routes.post.routes)
