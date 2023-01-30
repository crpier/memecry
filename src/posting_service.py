import logging
from pathlib import Path

import aiofiles
import fastapi
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from src import models, config, schema

logger = logging.getLogger()


def get_top_posts(s: Session) -> list[models.Post]:
    logger.info(s)
    return list(s.scalars(select(models.Post).where(models.Post.top == True)).all())


def get_post(post_id: int, s: Session) -> schema.Post:
    with s:
        logger.info(f"Looking for post {post_id}")
        res = s.execute(select(models.Post).where(models.Post.id == post_id)).one()
        return schema.Post(**res[0].__dict__)


async def upload_post(
    post_data: schema.PostCreate,
    s: Session,
    uploaded_file: fastapi.UploadFile,
    settings: config.Settings,
):
    with s:
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


def add_reaction(
    s: Session, user_id: int, post_id: int, reaction_kind: models.ReactionKind
):
    with s:
        res = s.execute(
            select(models.Reaction).where(
                models.Reaction.post_id == post_id, models.Reaction.user_id == user_id
            )
        ).one_or_none()

        if res:
            if res[0].kind == reaction_kind.value:
                logger.debug("The same reaction was given to the same post.")
                raise ValueError(f"Already has a {reaction_kind.name} on {post_id=}")
            else:
                logger.debug("Old reaction will be replaced")
                s.delete(res[0])
                s.flush()

        new_reaction = models.Reaction(
            user_id=user_id, post_id=post_id, kind=reaction_kind.value
        )
        s.add(new_reaction)

        reacted_post: models.Post = s.execute(
            select(models.Post).where(models.Post.id == post_id)
        ).one()[0]

        reacted_post.add_reaction(reaction_kind)
        if res is None:
            logger.debug("No previous reaction")
        else:
            logger.debug("The new reaction is different from the old one")
            reacted_post.remove_other_reaction(reaction_kind)
        s.commit()


def remove_reaction(
    s: Session, user_id: int, post_id: int, reaction_kind: models.ReactionKind
):
    with s:
        res = s.execute(
            delete(models.Reaction).where(
                models.Reaction.post_id == post_id, models.Reaction.user_id == user_id
            )
        )
        assert res.rowcount > 0, f"Cannot unlike {post_id=}: there was no like before"  # type: ignore
        res = s.execute(
            select(models.Post).where(models.Post.id == post_id)
        ).one_or_none()
        assert res, f"{post_id=} cannot be liked: it does not exist"
        rated_post: models.Post = res[0]
        rated_post.remove_reaction(reaction_kind)
        s.add(rated_post)
        s.commit()


def dislike_post(
    s: Session,
    user_id: int,
    post_id: int,
):
    with s:
        new_like = models.Reaction(user_id=user_id, post_id=post_id)
        # Will errrrror out if already liked this post
        s.add(new_like)
        res = s.execute(
            select(models.Post).where(models.Post.id == post_id)
        ).one_or_none()
        assert res, f"{post_id=} cannot be liked: it does not exist"
        rated_post = res[0]
        rated_post.likes += 1
        s.add(rated_post)
        s.commit()


def undislike_post(
    s: Session,
    user_id: int,
    post_id: int,
):
    with s:
        res = s.execute(
            delete(models.Reaction).where(
                models.Reaction.post_id == post_id, models.Reaction.user_id == user_id
            )
        )
        assert res.rowcount > 0, f"Cannot unlike {post_id=}: there was no like before"  # type: ignore
        res = s.execute(
            select(models.Post).where(models.Post.id == post_id)
        ).one_or_none()
        assert res, f"{post_id=} cannot be liked: it does not exist"
        rated_post = res[0]
        rated_post.likes -= 1
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
