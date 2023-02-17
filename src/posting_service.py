import logging
from typing import Callable

import aiofiles
import fastapi
from sqlmodel import Session, col, delete, select

from src import config, models, schema

logger = logging.getLogger()


# TODO: one function for posts, with a param
def get_top_posts(
    session: Callable[[], Session], limit=5, offset=0
) -> list[schema.Post]:
    with session() as s:
        posts = s.exec(
            select(models.Post)
            .where(col(models.Post.top) == True)
            .offset(offset)
            .limit(limit)
        ).all()
        return [schema.Post.from_orm(post) for post in posts]


def get_newest_posts(
    session: Callable[[], Session], limit=5, offset=0
) -> list[schema.Post]:
    with session() as s:
        posts = s.exec(select(models.Post).offset(offset).limit(limit)).all()
        return [schema.Post.from_orm(post) for post in posts]


def get_post(post_id: int, session: Callable[[], Session]) -> schema.Post:
    with session() as s:
        logger.info(f"Looking for post {post_id}")
        res = s.exec(select(models.Post).where(models.Post.id == post_id)).one()
        return schema.Post.from_orm(res)


async def upload_post(
    post_data: schema.PostCreate,
    session: Callable[[], Session],
    uploaded_file: fastapi.UploadFile,
    settings: config.Settings,
) -> int:
    with session() as s:
        # all posts by super admin are top posts huehuehuehue
        if post_data.user_id == settings.SUPER_ADMIN_ID:
            post_data.top = True
        # TODO: some tests that guarantee compatibility between models and schemas
        # for example, to guarantee that a valid models.Post can be created from a valid schema.PostCreate
        # also the reverse: models.Post -> schema.Post
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
        new_post.source = "/" + str(dest)
        new_post_id = new_post.id
        if not new_post_id:
            raise ValueError("We created a post with no id??")
        s.add(new_post)
        s.commit()
        return new_post_id


def add_reaction(
    session: Callable[[], Session],
    user_id: int,
    post_id: int,
    reaction_kind: models.ReactionKind,
) -> None:
    with session() as s:
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
    session: Callable[[], Session],
    user_id: int,
    post_id: int,
    reaction_kind: models.ReactionKind,
) -> None:
    with session() as s:
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
    session: Callable[[], Session],
    user_id: int,
    post_id: int,
) -> None:
    with session() as s:
        new_like = models.Reaction(user_id=user_id, post_id=post_id)  # type: ignore
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
    session: Callable[[], Session],
    user_id: int,
    post_id: int,
) -> None:
    with session() as s:
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


def get_posts_by_user(
    username: str, session: Callable[[], Session]
) -> list[schema.Post]:
    with session() as s:
        owner = s.exec(
            select(models.User).where(models.User.username == username)
        ).one_or_none()
        if not owner or not owner.id:
            return []
        res = s.execute(
            select(models.Post).where(models.Post.user_id == owner.id)
        ).all()
        if res is None:
            return []
        else:
            return [schema.Post.from_orm(post[0]) for post in res]


def get_user_reaction_on_post(
    user_id: int, post_id: int, session: Callable[[], Session]
) -> models.ReactionKind | None:
    with session() as s:
        res = s.exec(
            select(models.Reaction).where(
                models.Reaction.user_id == user_id, models.Reaction.post_id == post_id
            )
        ).one_or_none()
        return res.kind if res else None
