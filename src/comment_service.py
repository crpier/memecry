import logging
from pathlib import Path

from typing import Callable
import aiofiles
import fastapi
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from src import models, config, schema

import logging

from fastapi import UploadFile
from sqlalchemy.orm import Session
import aiofiles

from src import config, schema, models

logger = logging.getLogger()


async def comment_on_post(
    session: Callable[[], Session],
    comment_data: schema.CommentCreate,
    attachment: UploadFile | None,
    settings: config.Settings,
) -> int:
    with session() as s:
        # this is a reply
        if comment_data.post_id is None:
            res = s.execute(
                select(models.Comment).where(
                    models.Comment.id == comment_data.parent_id
                )
            ).one()
            parent_comment: models.Comment = res[0]
            comment_data.post_id = int(str(parent_comment.post_id))

        logger.info(s)
        new_comment = models.Comment(**comment_data.__dict__)
        s.add(new_comment)
        s.commit()
        # TODO Putting all files in one folder is probably a bad idea long term
        # TODO: "comments" is a magic string
        new_id = new_comment.id
        if attachment:
            dest = (settings.UPLOAD_STORAGE / "comments" / attachment.filename).with_stem(
                str(new_id)
            )
            logger.debug("Uploading content to %s", dest)
            async with aiofiles.open(dest, "wb") as f:
                await f.write(await attachment.read())
            s.execute(
                update(models.Comment)
                .where(models.Comment.id == new_comment.id)
                .values(attachment_source=str(dest))
            )
        s.commit()
        return int(str(new_id))


def get_comments_per_post(
    session: Callable[[], Session], post_id: int
) -> list[models.Comment]:
    with session() as s:
        results = s.execute(
            select(models.Comment).where(models.Comment.post_id == post_id)
        ).all()
        result: models.Comment
        return [result[0] for result in results]
