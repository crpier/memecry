import logging
from collections import defaultdict

from typing import Callable
import aiofiles
from sqlmodel import Session, select, null

from src import models, config, schema

import logging

from fastapi import UploadFile
import aiofiles

from src import config, schema, models

logger = logging.getLogger()


async def comment_on_post(
    session: Callable[[], Session],
    comment_data: schema.CommentCreate,
    attachment: UploadFile | None,
    settings: config.Settings,
) -> models.Comment:
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
        if attachment:
            dest = (
                settings.UPLOAD_STORAGE / "comments" / attachment.filename
            ).with_stem(str(new_comment.id))
            logger.debug("Uploading content to %s", dest)
            async with aiofiles.open(dest, "wb") as f:
                await f.write(await attachment.read())
            new_comment.attachment_source = attachment_source = str(dest)
            s.add(new_comment)
            s.commit()
        return new_comment


def get_comments_per_post(
    session: Callable[[], Session], post_id: int
) -> list[models.Comment]:
    with session() as s:
        results = s.exec(
            select(models.Comment).where(models.Comment.post_id == post_id)
        ).all()
        return results


def get_children_comment_tree(
    session: Callable[[], Session], parent_id: int, all_comments: list[models.Comment]
) -> dict[models.Comment, dict]:
    tree = {}
    direct_children_ids = [
        comment.id for comment in all_comments if comment.parent_id == parent_id
    ]
    for child_id in direct_children_ids:
        tree[child_id] = get_children_comment_tree(
            session=session, parent_id=child_id, all_comments=all_comments  # type: ignore
        )
    return tree


def get_comment_tree(
    session: Callable[[], Session], post_id: int
) -> tuple[dict[int, models.Comment], dict]:
    tree = {}
    with session() as s:
        all_comments = s.exec(
            select(models.Comment).where(models.Comment.post_id == post_id)
        ).all()
        root_comments_ids = [
            comment.id for comment in all_comments if comment.parent_id is None
        ]
        for comment_id in root_comments_ids:
            tree[comment_id] = get_children_comment_tree(session=session, parent_id=comment_id, all_comments=all_comments)  # type: ignore
        comments_dict = {comment.id: comment for comment in all_comments}
        return comments_dict, tree
