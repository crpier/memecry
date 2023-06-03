import logging
from pathlib import Path
from typing import Callable

import aiofiles
import fastapi
from sqlalchemy.sql.expression import null
from sqlmodel import Session, select

from src import config, models, schema
from src.index_service import get_text_from_image

logger = logging.getLogger()


def get_posts(
    session: Callable[[], Session], limit=5, offset=0, viewer: schema.User | None = None
) -> list[schema.Post]:
    with session() as s:
        res = s.exec(select(models.Post).offset(offset).limit(limit)).all()
        if viewer:
            return [
                schema.Post.from_model(
                    post,
                    # TODO: we might want to do a single query for all reactions
                    get_user_reaction_on_post(
                        user_id=viewer.id,
                        post_id=post.id,  # type: ignore
                        session=session,
                    ),
                    editable=viewer.id == post.user_id,
                )
                for post in res
            ]
        else:
            return [schema.Post.from_model(post) for post in res]


def get_posts_by_user(
    owner_id: str, session: Callable[[], Session], viewer: schema.User | None = None
) -> list[schema.Post]:
    with session() as s:
        res = s.exec(select(models.Post).where(models.Post.user_id == owner_id)).all()
        if res is None:
            return []
        else:
            if viewer:
                return [
                    schema.Post.from_model(
                        post,
                        # TODO: we might want to do a single query for all reactions
                        get_user_reaction_on_post(
                            user_id=viewer.id,
                            post_id=post.id,  # type: ignore
                            session=session,
                        ),
                        editable=viewer.id == post.user_id,
                    )
                    for post in res
                ]
            else:
                return [schema.Post.from_model(post) for post in res]


def get_post_by_id(
    session: Callable[[], Session], post_id: int, viewer: schema.User | None = None
) -> schema.Post:
    with session() as s:
        res = s.exec(select(models.Post).where(models.Post.id == post_id)).one()
        assert res.id
        if viewer:
            reaction = get_user_reaction_on_post(
                user_id=viewer.id, post_id=res.id, session=session
            )
            editable = viewer.id == res.user_id
        else:
            reaction = None
            editable = False
        return schema.Post.from_model(
            post_in_db=res, reaction=reaction, editable=editable
        )


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
            logger.info("New post by super admin, setting top to True")
        # TODO: some tests that guarantee compatibility between models and schemas
        # for example, to guarantee that a valid models.Post,
        # can be created from a valid schema.PostCreate
        # also the reverse: models.Post -> schema.Post
        new_post = models.Post(**post_data.__dict__)
        s.add(new_post)
        s.commit()
        logger.info("New post has ID %s", new_post.id)
        # TODO: Putting all files in one folder is probably a bad idea long term
        # TODO: Maybe conversion from URI path to filesystem path
        # should be done in the schema
        dest = (settings.MEDIA_UPLOAD_STORAGE / uploaded_file.filename).with_stem(
            str(new_post.id)
        )
        try:
            logger.debug("Uploading post content to %s", dest)
            async with aiofiles.open(dest, "wb") as f:
                await f.write(await uploaded_file.read())
            new_post.source = "/media/" + str(dest.name)
            new_post_id = new_post.id
            if not new_post_id:
                raise ValueError("We created a post with no id??")
            s.add(new_post)
            s.commit()
            return new_post_id
        except Exception as e:
            logger.error("Error while uploading post: %s", e)
            s.rollback()
            s.delete(new_post)
            s.commit()
            dest.unlink()
            raise e


def index_post(
    session: Callable[[], Session], post_id: int, settings: config.Settings
) -> None:
    logger.info("Index post %s", post_id)
    with session() as s:
        new_post = s.exec(select(models.Post).where(models.Post.id == post_id)).one()
        logger.info("Post to index source: %s", new_post.source)
        assert new_post.source
        # we need to do this because the source path is absolute
        dest = settings.MEDIA_UPLOAD_STORAGE / Path(new_post.source).name
        new_post.content = get_text_from_image(Path(dest), debug=True)
        logger.info("Post %s indexed content: %s", new_post.id, new_post.content)
        conn = s.connection()
        # TODO: get table name from config
        conn.exec_driver_sql(
            "INSERT INTO posts_data (rowid, title, content) VALUES (?, ?, ?)",
            (new_post.id, new_post.title, new_post.content),  # type: ignore
        )
        s.commit()
        logger.info("Post %s indexed", new_post.id)


def edit_post(
    session: Callable[[], Session],
    post_id: int,
    post_data: schema.PostEdit,
    editor: schema.User,
):
    with session() as s:
        post = s.exec(select(models.Post).where(models.Post.id == post_id)).one()
        if editor.id != post.user_id:
            raise fastapi.HTTPException(
                status_code=403, detail="You can only edit your own posts"
            )
        # TODO: some tests that guarantee compatibility between models and schemas
        for key, val in post_data.dict().items():
            post.__setattr__(key, val)
        print(post.title)
        s.add(post)
        print(post.title)
        conn = s.connection()
        # TODO: get table name from config
        conn.exec_driver_sql(
            "UPDATE posts_data set title=? where rowid=?",
            (post_data.title, post_id),  # type: ignore
        )
        print(post.title)
        s.commit()
        print(post.title)


def add_reaction(
    session: Callable[[], Session],
    user_id: int,
    post_id: int,
    reaction_kind: models.ReactionKind,
) -> None:
    with session() as s:
        old_reaction = s.exec(
            select(models.Reaction).where(
                models.Reaction.post_id == post_id,
                models.Reaction.user_id == user_id,
                models.Reaction.comment_id == null(),
            )
        ).one_or_none()

        if old_reaction:
            logger.debug("Old reaction will be removed")
            s.delete(old_reaction)
            if (
                old_reaction_kind := old_reaction.kind
            ) == models.ReactionKind.Like.value:
                old_reaction.post.likes -= 1
                old_reaction.post.score -= 1
            else:
                old_reaction.post.dislikes -= 1
                old_reaction.post.score += 1
            s.flush()
            if old_reaction_kind == reaction_kind:
                logger.debug("The new reaction is the same as the old one, removing")
                s.commit()
                return None

        new_reaction = models.Reaction(
            user_id=user_id, post_id=post_id, kind=reaction_kind
        )
        s.add(new_reaction)

        reacted_post: models.Post = s.execute(
            select(models.Post).where(models.Post.id == post_id)
        ).one()[0]

        reacted_post.add_reaction(reaction_kind)
        if old_reaction is None:
            logger.debug("No previous reaction")
        else:
            logger.debug("The new reaction is different from the old one")
            reacted_post.remove_other_reaction(reaction_kind)
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


def get_user_reaction_on_post(
    user_id: int, post_id: int, session: Callable[[], Session]
) -> models.ReactionKind | None:
    with session() as s:
        res = s.exec(
            select(models.Reaction).where(
                models.Reaction.user_id == user_id,
                models.Reaction.post_id == post_id,
                models.Reaction.comment_id == null(),
            )
        ).one_or_none()
        return res.kind if res else None


def search_through_posts(
    query: str, session: Callable[[], Session], user: schema.User | None = None
) -> list[schema.Post]:
    with session() as s:
        conn = s.connection()
        # TODO: get table name from config
        res = conn.exec_driver_sql(
            "SELECT rowid FROM posts_data " "WHERE posts_data MATCH ?",
            (query,),  # type: ignore
        )
        post_ids: list[int] = [result[0] for result in res.fetchall()]
        return [
            get_post_by_id(session=session, post_id=post_id, viewer=user)
            for post_id in post_ids
        ]
