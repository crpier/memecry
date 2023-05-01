import logging
from types import new_class
from typing import Callable

import aiofiles
from fastapi import UploadFile
from sqlmodel import Session, select
import babel.dates
from datetime import datetime
from sqlalchemy.orm import selectinload

from src import config, models, schema

logger = logging.getLogger()


async def post_comment(
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
        new_comment.post.comment_count += 1
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
            new_comment.attachment_source = str(dest)
            s.add(new_comment)
            s.commit()
        return new_comment.post_id  # type: ignore


def get_comments_per_post(
    session: Callable[[], Session], post_id: int
) -> list[schema.Comment]:
    with session() as s:
        results = s.exec(
            select(models.Comment)
            .where(models.Comment.post_id == post_id)
            .order_by(models.Comment.created_at.desc())  # type: ignore
        ).all()
        return [schema.Comment.from_orm(comment) for comment in results]


def get_children_comment_tree(
    session: Callable[[], Session], parent_id: int, all_comments: list[schema.Comment]
) -> dict[schema.Comment, dict]:
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
    now = datetime.utcnow()
    with session() as s:
        all_comments = s.exec(
            select(models.Comment)
            .options(selectinload(models.Comment.user))
            .where(models.Comment.post_id == post_id)
            .order_by(models.Comment.created_at.desc())  # type: ignore
        ).all()
        for comment in all_comments:
            comment.created_at = babel.dates.format_timedelta(  # type: ignore
                comment.created_at - now, add_direction=True, locale="en_US"
            )
        root_comments_ids = [
            comment.id for comment in all_comments if comment.parent_id is None
        ]
        for comment_id in root_comments_ids:
            tree[comment_id] = get_children_comment_tree(session=session, parent_id=comment_id, all_comments=all_comments)  # type: ignore
        comments_dict = {comment.id: comment for comment in all_comments}
        return comments_dict, tree  # type: ignore


def add_reaction(
    session: Callable[[], Session],
    reaction_kind: models.ReactionKind,
    comment_id: int,
    user_id: int,
) -> int:
    # TODO: instead of re-liking/re-disliking, I should undo the reaction
    with session() as s:
        res = s.exec(
            select(models.Reaction).where(
                models.Reaction.comment_id == comment_id,
                models.Reaction.user_id == user_id,
            )
        ).one_or_none()
        if res:
            logger.debug("Old reaction will be replaced")
            s.delete(res)
            if res.kind == models.ReactionKind.Like.value:
                res.comment.likes -= 1
            else:
                res.comment.dislikes -= 1
            s.flush()

        new_reaction = models.Reaction(
            user_id=user_id, comment_id=comment_id, kind=reaction_kind
        )
        s.add(new_reaction)
        s.flush()
        new_reaction.post_id = new_reaction.comment.post_id
        if new_reaction.kind == models.ReactionKind.Like.value:
            new_reaction.comment.likes += 1
        else:
            new_reaction.comment.dislikes += 1
        updated_post_id = new_reaction.post_id
        assert updated_post_id
        s.commit()
        return updated_post_id
