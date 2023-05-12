import logging
from datetime import datetime
from typing import Callable
from pathlib import Path

import aiofiles
import babel.dates
from fastapi import UploadFile
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

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

        new_comment = models.Comment(**comment_data.__dict__)
        s.add(new_comment)
        s.commit()
        new_comment.post.comment_count += 1
        s.commit()
        # TODO Putting all files in one folder is probably a bad idea long term
        # TODO: "comments" is a magic string
        if attachment:
            dest = (
                Path("media") / "comments" / attachment.filename
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
            session=session,
            parent_id=child_id,
            all_comments=all_comments,
        )
    return tree  # type: ignore


def get_comment_tree(
    session: Callable[[], Session], post_id: int
) -> tuple[dict[int, schema.Comment], dict]:
    tree = {}
    datetime.utcnow()
    with session().no_autoflush as s:
        all_comments = s.exec(
            select(models.Comment)
            .options(selectinload(models.Comment.user))
            .where(models.Comment.post_id == post_id)
            .order_by(models.Comment.created_at.asc())  # type: ignore
        ).all()
        root_comments_ids = [
            comment.id for comment in all_comments if comment.parent_id is None
        ]
        for comment_id in root_comments_ids:
            tree[comment_id] = get_children_comment_tree(
                session=session,
                parent_id=comment_id,  # type: ignore
                all_comments=all_comments,  # type: ignore
            )
        comments_dict = {
            comment.id: schema.Comment.from_orm(comment) for comment in all_comments
        }
        return comments_dict, tree  # type: ignore


def prepare_comment_for_viewing(
    session: Callable[[], Session], comment: schema.Comment, user: schema.User | None
) -> schema.Comment:
    assert type(comment.created_at) == datetime
    comment.created_at = babel.dates.format_timedelta(  # type: ignore
        comment.created_at - datetime.utcnow(),
        add_direction=True,
        locale="en_US",
    )
    if user:
        with session() as s:
            reaction = s.exec(
                select(models.Reaction).where(
                    models.Reaction.comment_id == comment.id,
                    models.Reaction.user_id == user.id,
                )
            ).one_or_none()
            if reaction:
                if reaction.kind == models.ReactionKind.Like.value:
                    comment.liked = True
                elif reaction.kind == models.ReactionKind.Dislike.value:
                    comment.disliked = True
    return comment


def add_reaction(
    session: Callable[[], Session],
    reaction_kind: models.ReactionKind,
    comment_id: int,
    user_id: int,
) -> int:
    # TODO: instead of re-liking/re-disliking, I should undo the reaction
    with session() as s:
        old_reaction = s.exec(
            select(models.Reaction).where(
                models.Reaction.comment_id == comment_id,
                models.Reaction.user_id == user_id,
            )
        ).one_or_none()
        if old_reaction:
            logger.debug("Old reaction will be replaced")
            s.delete(old_reaction)
            if (
                old_reaction_kind := old_reaction.kind
            ) == models.ReactionKind.Like.value:
                old_reaction.comment.likes -= 1
            else:
                old_reaction.comment.dislikes -= 1
            s.flush()
            if old_reaction_kind == reaction_kind:
                logger.debug("The new reaction is the same as the old one, removing")
                s.commit()
                assert old_reaction.post_id
                return old_reaction.post_id

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
