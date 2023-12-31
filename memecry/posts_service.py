from pathlib import Path

import aiofiles
from loguru import logger
from relax.injection import Injected, injectable
from sqlalchemy import delete, not_, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import load_only
from starlette.datastructures import UploadFile

import memecry.schema
from memecry.config import Config
from memecry.model import Post


@injectable
async def upload_post(
    post_data: memecry.schema.PostCreate,
    uploaded_file: UploadFile,
    *,
    asession: async_sessionmaker[AsyncSession] = Injected,
    config: Config = Injected,
) -> int:
    async with asession() as session:
        new_post = Post(**post_data.__dict__)
        # TODO: surely there's a smarter way to do this
        new_post.source = "sentinel"
        session.add(new_post)
        await session.commit()
        logger.info("New post has id: {}", new_post.id)
        if not uploaded_file.filename:
            msg = f"File {uploaded_file.filename} does not exist"
            raise AssertionError(msg)
        dest = (config.MEDIA_UPLOAD_STORAGE / uploaded_file.filename).with_stem(
            str(new_post.id),
        )
        async with aiofiles.open(dest, "wb") as f:
            await f.write(await uploaded_file.read())

        new_post.source = str(Path("/media") / str(dest.name))
        session.add(new_post)
        conn = await session.connection()
        await conn.exec_driver_sql(
            "INSERT INTO posts_data (rowid, title, content) VALUES (?, ?, ?)",
            (new_post.id, new_post.title, new_post.searchable_content),
        )
        await session.commit()
    return new_post.id


@injectable
async def get_posts(
    limit: int = 10,
    offset: int = 0,
    viewer: memecry.schema.UserRead | None = None,
    *,
    asession: async_sessionmaker[AsyncSession] = Injected,
    config: Config = Injected,
) -> list[memecry.schema.PostRead]:
    async with asession() as session:
        query = (
            select(Post).order_by(Post.created_at.desc()).limit(limit).offset(offset)
        )
        if not viewer:
            for tag in config.RESTRICTED_TAGS:
                query = query.where(Post.tags.not_like(f"%{tag}%"))
        result = await session.execute(query)
        post_reads = [
            memecry.schema.PostRead.from_model(post) for post in result.scalars().all()
        ]
        if viewer:
            for post in post_reads:
                if viewer.id == post.user_id:
                    post.editable = True
        return post_reads


@injectable
async def get_posts_by_search_query(  # noqa: PLR0913, C901
    query: memecry.schema.Query,
    # TODO: limit should have default value of None instead
    # TODO: offset and limit should always come together
    limit: int = 0,
    offset: int = 0,
    viewer: memecry.schema.UserRead | None = None,
    *,
    asession: async_sessionmaker[AsyncSession] = Injected,
    config: Config = Injected,
) -> list[memecry.schema.PostRead]:
    async with asession() as session:
        db_query = select(Post).order_by(Post.created_at.desc())
        if limit:
            db_query = db_query.limit(limit).offset(offset)

        # TODO: more consistent way to work with tags
        for tag in query.tags["included"]:
            db_query = db_query.where(Post.tags.contains(tag))

        for tag in query.tags["excluded"]:
            db_query = db_query.where(not_(Post.tags.contains(tag)))

        if not viewer:
            for tag in config.RESTRICTED_TAGS:
                db_query = db_query.where(Post.tags.not_like(f"%{tag}%"))

        if query.content:
            conn = await session.connection()
            if limit:
                result = await conn.exec_driver_sql(
                    "SELECT rowid FROM posts_data WHERE posts_data "
                    "MATCH ? LIMIT ? OFFSET ?",
                    (query.content, limit, offset),
                )
            else:
                result = await conn.exec_driver_sql(
                    "SELECT rowid FROM posts_data WHERE posts_data MATCH ?",
                    (query.content,),
                )
            post_ids: list[int] = [res[0] for res in result.fetchall()]
            db_query = db_query.where(Post.id.in_(post_ids))

        res = await session.execute(db_query)
        post_reads = [
            memecry.schema.PostRead.from_model(post) for post in res.scalars().all()
        ]
        if viewer:
            for post in post_reads:
                if viewer.id == post.user_id:
                    post.editable = True
        return post_reads


@injectable
async def get_post_by_id(
    post_id: int,
    viewer: memecry.schema.UserRead | None = None,
    *,
    asession: async_sessionmaker[AsyncSession] = Injected,
) -> memecry.schema.PostRead | None:
    async with asession() as session:
        query = select(Post).where(Post.id == post_id)
        result = await session.execute(query)
        post = result.scalars().one_or_none()
        if not post:
            return None
        return memecry.schema.PostRead.from_model(
            post,
            editable=bool(viewer and viewer.id == post.user_id),
        )


@injectable
async def toggle_post_tag(
    post_id: int,
    tag: str,
    user_id: int,
    *,
    asession: async_sessionmaker[AsyncSession] = Injected,
) -> str:
    async with asession() as session:
        get_old_tags_query = (
            select(Post)
            .where(Post.id == post_id)
            .options(load_only(Post.tags, Post.user_id))
        )
        result = await session.execute(get_old_tags_query)
        post_in_db = result.scalars().one()
        if post_in_db.user_id != user_id:
            raise PermissionError
        old_tags = post_in_db.tags.split(", ")

        if tag in old_tags:
            old_tags.remove(tag)
            if old_tags == []:
                old_tags = ["no-tags"]
        else:
            if old_tags == ["no-tags"]:
                old_tags = []
            old_tags.append(tag)

        new_tags = ", ".join(old_tags)

        query = update(Post).where(Post.id == post_id).values(tags=new_tags)
        await session.execute(query)
        await session.commit()
        return new_tags


@injectable
async def update_post_searchable_content(
    post_id: int,
    new_content: str,
    user_id: int,
    *,
    asession: async_sessionmaker[AsyncSession] = Injected,
) -> str:
    async with asession() as session:
        result = await session.execute(
            select(Post)
            .where(Post.id == post_id)
            .options(load_only(Post.searchable_content, Post.user_id)),
        )
        post_in_db = result.scalars().one()
        if post_in_db.user_id != user_id:
            raise PermissionError
        post_in_db.searchable_content = new_content

        conn = await session.connection()
        await conn.exec_driver_sql(
            "UPDATE posts_data SET content = ? WHERE rowid = ?",
            (new_content, post_id),
        )

        await session.commit()
        return new_content


@injectable
async def update_post_title(
    post_id: int,
    new_title: str,
    user_id: int,
    *,
    asession: async_sessionmaker[AsyncSession] = Injected,
) -> str:
    async with asession() as session:
        result = await session.execute(
            select(Post)
            .where(Post.id == post_id)
            .options(load_only(Post.title, Post.user_id)),
        )
        post_in_db = result.scalars().one()
        if post_in_db.user_id != user_id:
            raise PermissionError
        post_in_db.title = new_title

        conn = await session.connection()
        await conn.exec_driver_sql(
            "UPDATE posts_data SET title = ? WHERE rowid = ?",
            (new_title, post_id),
        )

        await session.commit()
        return new_title


@injectable
async def delete_post(
    post_id: int,
    *,
    asession: async_sessionmaker[AsyncSession] = Injected,
) -> None:
    async with asession() as session:
        # TODO: also remove the media file
        # TODO: a soft delete
        query = delete(Post).where(Post.id == post_id)
        await session.execute(query)

        conn = await session.connection()
        await conn.exec_driver_sql(
            "DELETE FROM posts_data where rowid = ?",
            (post_id,),
        )

        await session.commit()
