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

import memecry.routes.auth
import memecry.routes.misc
import memecry.routes.post
from memecry import security, user_service
from memecry.bootstrap import bootstrap
from memecry.schema import UserRead


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
        if (username := cast(str, payload.get("sub"))) is None:
            return None

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


app.routes.extend(memecry.routes.auth.auth_router.routes)
app.routes.extend(memecry.routes.post.post_router.routes)
app.routes.extend(memecry.routes.misc.misc_router.routes)
