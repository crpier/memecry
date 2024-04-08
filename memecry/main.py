import asyncio
import contextlib
import os
from typing import AsyncIterator, cast

import uvicorn
from jose import ExpiredSignatureError
from relax.app import (
    App,
    AuthScope,
    hot_replace_templates,
    run_async,
    websocket_endpoint,
)
from relax.injection import add_injectable
from starlette.authentication import AuthCredentials, AuthenticationBackend
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import HTTPConnection
from starlette.routing import Mount, WebSocketRoute
from starlette.staticfiles import StaticFiles
from uvicorn.supervisors.watchfilesreload import WatchFilesReload

import memecry.bootstrap
import memecry.routes.auth
import memecry.routes.post
import memecry.schema
import memecry.security
import memecry.user_service
from memecry.config import Config


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
    config = app.config
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
    if config.ENV == "dev":
        update_task = asyncio.create_task(hot_replace_templates(config.TEMPLATES_DIR))
    yield
    if config.ENV == "dev":
        update_task.cancel()  # type: ignore


def app_factory() -> App:
    app = App[Config](
        middleware=[Middleware(AuthenticationMiddleware, backend=BasicAuthBackend())],
        lifespan=lifespan,
    )

    run_async(memecry.bootstrap.bootstrap(app))
    app.add_router(memecry.routes.auth.router)
    app.add_router(memecry.routes.post.router)
    if app.config.ENV == "dev":
        app.routes.append(WebSocketRoute("/ws", endpoint=websocket_endpoint))

    return app


def start_app(app_path: str, port: int = 8000, log_level: str = "info") -> None:
    config_args = {
        "app": app_path,
        "port": port,
        "log_level": log_level,
        "factory": True,
    }
    server_config = uvicorn.Config(**config_args)  # type: ignore

    server = uvicorn.Server(server_config)

    import dotenv

    dotenv.load_dotenv()
    templates_dir = os.environ.get("TEMPLATES_DIR")
    if templates_dir is None:
        msg = "TEMPLATES_DIR not set"
        raise ValueError(msg)

    reload_config = uvicorn.Config(
        **config_args,  # type: ignore
        reload=True,
        reload_excludes=[templates_dir + "/*"],
    )
    sock = reload_config.bind_socket()
    reloader = WatchFilesReload(reload_config, target=server.run, sockets=[sock])
    add_injectable(WatchFilesReload, reloader)
    reloader.run()


if __name__ == "__main__":
    start_app(app_path="memecry.main:app_factory", port=8000, log_level="info")
