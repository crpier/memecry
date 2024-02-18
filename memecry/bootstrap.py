import sqlite3
from pathlib import Path

import alembic.command
import alembic.config
from loguru import logger
from relax.app import App, ViewContext
from relax.injection import _COMPONENT_NAMES, add_injectable
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlite_fts4 import register_functions

import memecry.config
import memecry.model


@logger.catch
def run_migrations(script_location: str, dsn: str) -> None:
    logger.info("Running DB migrations in {}", script_location)
    alembic_cfg = alembic.config.Config("alembic.ini")
    alembic_cfg.set_main_option("script_location", script_location)
    alembic_cfg.set_main_option("sqlalchemy.url", dsn)
    logger.info(
        "Running alembic upgrade from {}",
        alembic_cfg.get_section_option("alembic", "here"),
    )
    alembic.command.upgrade(alembic_cfg, "head")


@logger.catch
async def bootstrap(app: App) -> memecry.config.Config:
    config = memecry.config.Config()
    add_injectable(memecry.config.Config, config)

    add_injectable(ViewContext, app.view_context)

    # ensure media folder exists
    config.MEDIA_UPLOAD_STORAGE.mkdir(parents=True, exist_ok=True)
    # we need a bit of an sync piece on startup lel
    db = sqlite3.connect(config.DB_FILE)

    register_functions(db)
    c = db.cursor()
    c.execute(
        "CREATE VIRTUAL TABLE IF NOT EXISTS posts_data USING fts4(title, content)",
    )

    dsn = f"sqlite+aiosqlite:///{config.DB_FILE}"
    engine = create_async_engine(dsn)

    async_session = async_sessionmaker(engine, expire_on_commit=False)
    add_injectable(async_sessionmaker[AsyncSession], async_session)

    if config.ENV == "prod":
        run_migrations("./memecry/alembic", dsn)
        async with engine.begin() as conn:
            # TODO: have a migration to create tables and stuff instead?
            await conn.run_sync(memecry.model.Base.metadata.create_all)

    # TODO: get this from app
    js_constants_fn = Path("static/js/constants.js")
    with js_constants_fn.open("w") as f:
        f.write("export const CONSTANTS = {\n")
        for name in _COMPONENT_NAMES:
            f.write(f'   {name.upper().replace("-", "_")}_CLASS: "{name}",\n')
        f.write("}")
    return config
