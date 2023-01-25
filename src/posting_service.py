import logging
from pathlib import Path

import aiofiles
import fastapi
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from src import models, config, schema

logger = logging.getLogger()


def get_top_posts(s: Session) -> list[models.Post]:
    logger.info(s)
    return list(s.scalars(select(models.Post).where(models.Post.top == True)).all())


async def upload_post(
    post_data: schema.PostCreate,
    s: Session,
    uploaded_file: fastapi.UploadFile,
    settings: config.Settings,
):
    with s:
        logger.info(s)
        # all posts by super admin are top posts huehuehuehue
        if post_data.user_id == settings.SUPER_ADMIN_ID:
            post_data.top = True
        new_post = models.Post(**post_data.__dict__)
        s.add(new_post)
        s.commit()
        # TODO Putting all files in one folder is probably a bad idea long term
        dest = (settings.UPLOAD_STORAGE / uploaded_file.filename).with_stem(
            str(new_post.id)
        )
        logger.debug("Uploading content to %s", dest)
        async with aiofiles.open(dest, "wb") as f:
            await f.write(await uploaded_file.read())
        s.execute(
            update(models.Post)
            .where(models.Post.id == new_post.id)
            .values(source=str(dest))
        )
        s.commit()


def like_post(
    s: Session,
    user_id: int,
    post_id: int,
    settings: config.Settings,
):
    with s:
        res = s.execute(
            select(models.Post).where(models.Post.id == post_id)
        ).one_or_none()
        assert res
        rated_post = res[0]
        rated_post.likes += 1
        s.add(rated_post)
        s.commit()


def get_posts_by_user(user_id: int, s: Session) -> list[models.Post]:
    logger.info(s)
    with s:
        res = s.execute(select(models.Post).where(models.Post.user_id == user_id)).all()
        if res is None:
            return []
        else:
            return [post[0] for post in res]
