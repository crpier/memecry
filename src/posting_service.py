import logging
from pathlib import Path

import aiofiles
import fastapi
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from src import models, config

logger = logging.getLogger()


def get_top_posts(s: Session) -> list[models.Post]:
    logger.info(s)
    return list(s.scalars(select(models.Post).where(models.Post.top == True)).all())


async def upload_post(
        s: Session, title: str, file: fastapi.UploadFile, content_dest: Path, user_id: int, settings: config.Settings
):
    with s:
        logger.info(s)
        new_post = models.Post(title=title, user_id=user_id)
        # all posts by super admin are top posts huehuehuehue
        if user_id == settings.SUPER_ADMIN_ID:
            new_post.top = True # type: ignore
        s.add(new_post)
        s.commit()
        dest = (content_dest / file.filename).with_stem(str(new_post.id))
        logger.debug("Uploading content to %s", dest)
        async with aiofiles.open(dest, "wb") as f:
            await f.write(await file.read())
        s.execute(
            update(models.Post)
            .where(models.Post.id == new_post.id)
            .values(source=str(dest))
        )
        s.commit()


def get_posts_by_user(user_id: int, s: Session) -> list[models.Post]:
    logger.info(s)
    with s:
        res = s.execute(select(models.Post).where(models.Post.user_id == user_id)).all()
        if res is None:
            return []
        else:
            return [post[0] for post in res]
