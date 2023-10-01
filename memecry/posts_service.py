from pathlib import Path

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, load_only
from starlette.datastructures import UploadFile
from yahgl_py.injection import Injected, injectable
import aiofiles

from memecry.model import User, Post
from memecry.schema import PostCreate, PostRead, UserRead

MEDIA_UPLOAD_STORAGE = Path("./testdata/media")


@injectable
async def upload_post(
    post_data: PostCreate,
    uploaded_file: UploadFile,
    *,
    asession: async_sessionmaker[AsyncSession] = Injected,
) -> int:
    async with asession() as session:
        new_post = Post(**post_data.__dict__)
        # TODO: surely there's a smarter way to do this
        new_post.source = "sentinel"
        session.add(new_post)
        await session.commit()
        print(f"New post has id: {new_post.id}")
        assert uploaded_file.filename
        dest = (MEDIA_UPLOAD_STORAGE / uploaded_file.filename).with_stem(
            str(new_post.id)
        )
        async with aiofiles.open(dest, "wb") as f:
            await f.write(await uploaded_file.read())

        new_post.source = str(Path("/media") / str(dest.name))
        session.add(new_post)
        await session.commit()
    return new_post.id


@injectable
async def get_posts(
    limit=5,
    offset=0,
    viewer: UserRead | None = None,
    *,
    asession: async_sessionmaker[AsyncSession] = Injected,
):
    async with asession() as session:
        query = (
            select(Post).order_by(Post.created_at.desc()).limit(limit).offset(offset)
        )
        result = await session.execute(query)
        return [PostRead.model_validate(post) for post in result.scalars().all()]


@injectable
async def get_post_by_id(
    post_id: int,
    viewer: UserRead | None = None,
    *,
    asession: async_sessionmaker[AsyncSession] = Injected,
) -> PostRead | None:
    async with asession() as session:
        query = select(Post).where(Post.id == post_id)
        result = await session.execute(query)
        post = result.scalars().one_or_none()
        if post:
            return PostRead.model_validate(post)
        else:
            return None


@injectable
async def toggle_post_tag(
    post_id: int,
    tag: str,
    *,
    asession: async_sessionmaker[AsyncSession] = Injected,
):
    async with asession() as session:
        get_old_tags_query = select(Post).where(Post.id == post_id).options(
            load_only(Post.tags)
        )
        result = await session.execute(get_old_tags_query)
        old_tags = result.scalars().one()
        old_tags = old_tags.tags.split(", ")

        if tag in old_tags:
            old_tags.remove(tag)
            if old_tags == []:
                old_tags = ["no tags"]
        else:
            if old_tags == ["no tags"]:
                old_tags = []
            old_tags.append(tag)

        new_tags = ", ".join(old_tags)

        query = update(Post).where(Post.id == post_id).values(tags=new_tags)
        await session.execute(query)
        await session.commit()
        return new_tags
