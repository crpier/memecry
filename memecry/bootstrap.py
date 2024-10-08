import logging
import shlex
import sqlite3
import subprocess
from logging import Logger, basicConfig, getLogger

import alembic.command
import alembic.config
from relax.app import update_js_constants
from relax.injection import add_injectable
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlite_fts4 import register_functions

import memecry.config
import memecry.model


def run_migrations(script_location: str, dsn: str, logger: Logger) -> None:
    logger.debug("Running DB migrations in %s", script_location)
    alembic_cfg = alembic.config.Config("alembic.ini")
    alembic_cfg.set_main_option("script_location", script_location)
    alembic_cfg.set_main_option("sqlalchemy.url", dsn)
    logger.debug(
        "Running alembic upgrade from %s",
        alembic_cfg.get_section_option("alembic", "here"),
    )
    alembic.command.upgrade(alembic_cfg, "head")


def bootstrap() -> memecry.config.Config:
    config = memecry.config.Config()
    add_injectable(memecry.config.Config, config)

    basicConfig(
        level=logging.WARNING if config.ENV == "PROD" else logging.DEBUG, force=True
    )
    logger = getLogger("memecry")
    add_injectable(Logger, logger)
    getLogger("aiosqlite").setLevel("WARNING")

    # ensure media folder exists
    config.MEDIA_UPLOAD_STORAGE.mkdir(parents=True, exist_ok=True)

    # create search table
    db = sqlite3.connect(config.DB_FILE)
    register_functions(db)
    c = db.cursor()
    c.execute(
        "CREATE VIRTUAL TABLE IF NOT EXISTS posts_data USING fts4(title, content)",
    )

    async_engine = create_async_engine(f"sqlite+aiosqlite:///{config.DB_FILE}")
    sync_engine = create_engine(f"sqlite:///{config.DB_FILE}")

    async_session = async_sessionmaker(async_engine, expire_on_commit=False)
    add_injectable(async_sessionmaker[AsyncSession], async_session)

    if config.ENV == "PROD":
        run_migrations(
            "./memecry/alembic_migrations", f"sqlite:///{config.DB_FILE}", logger=logger
        )
        subprocess.Popen(shlex.split("tailwindcss-extra -o static/css/tailwind.css"))  # noqa: S603
    elif config.ENV == "DEV":
        with sync_engine.begin() as conn:
            memecry.model.Base.metadata.create_all(conn)

    update_js_constants(config)
    return config
