import sqlite3
import subprocess

import alembic.command
import alembic.config
from loguru import logger
from relax.app import ViewContext, update_js_constants
from relax.injection import add_injectable
from sqlalchemy.engine import create_engine
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


def bootstrap() -> tuple[memecry.config.Config, ViewContext]:
    config = memecry.config.Config()
    add_injectable(memecry.config.Config, config)

    view_context = ViewContext()
    add_injectable(ViewContext, view_context)

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
    engine_sync = create_engine(dsn)

    async_session = async_sessionmaker(engine, expire_on_commit=False)
    add_injectable(async_sessionmaker[AsyncSession], async_session)

    if config.ENV == "prod":
        with engine_sync.begin() as conn:
            memecry.model.Base.metadata.create_all(conn)
        run_migrations("./memecry/alembic_migrations", dsn)

    update_js_constants(config)

    subprocess.Popen(["tailwindcss", "-o", "static/css/tailwind.css"])
    return config, view_context
