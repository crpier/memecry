import logging

from src import (
    deps,
    models,
    posting_service,
    schema,
    security,
    user_service,
    config,
    comment_service,
)

import fastapi
import fastapi.security
from fastapi import Body, Depends, HTTPException

from sqlalchemy.orm import Session

app = fastapi.FastAPI()

logger = logging.getLogger()

# Initialize settings at the start,
# so that we don't have to wait for request to see errors (if any)
deps.get_settings()


@app.post("/token")
async def login(
    form_data: fastapi.security.OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(deps.get_session),
    settings: config.Settings = Depends(deps.get_settings),
):
    user = user_service.authenticate_user(
        session, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(
        data={"sub": user.username}, settings=settings
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me")
def get_me(current_user: schema.User = Depends(deps.get_current_user)):
    return current_user


@app.get("/health")
def check_health():
    return {"message": "Everything OK"}


@app.get("/top")
def get_top_posts(
    session: Session = Depends(deps.get_session),
):
    return posting_service.get_top_posts(session)


@app.post("/post")
async def upload_post(
    file: fastapi.UploadFile,
    title: str = Body(),
    current_user: schema.User = Depends(deps.get_current_user),
    settings: config.Settings = Depends(deps.get_settings),
    session: Session = Depends(deps.get_session),
):
    new_post = schema.PostCreate(title=title, user_id=current_user.id)
    await posting_service.upload_post(
        post_data=new_post,
        s=session,
        uploaded_file=file,
        settings=settings,
    )
    return {"status": "success"}


@app.put("/post/{id}/like")
async def like_post(
    id: int,
    current_user: schema.User = Depends(deps.get_current_user),
    session: Session = Depends(deps.get_session),
):
    posting_service.add_reaction(
        session,
        post_id=id,
        user_id=current_user.id,
        reaction_kind=models.ReactionKind.Like,
    )
    return {"status": "success"}


@app.put("/post/{id}/unlike")
async def unlike_post(
    id: int,
    current_user: schema.User = Depends(deps.get_current_user),
    session: Session = Depends(deps.get_session),
):
    posting_service.remove_reaction(
        session,
        post_id=id,
        user_id=current_user.id,
        reaction_kind=models.ReactionKind.Like,
    )
    return {"status": "success"}


@app.put("/post/{id}/dislike")
async def dislike_post(
    id: int,
    current_user: schema.User = Depends(deps.get_current_user),
    session: Session = Depends(deps.get_session),
):
    posting_service.add_reaction(
        session,
        post_id=id,
        user_id=current_user.id,
        reaction_kind=models.ReactionKind.Dislike,
    )
    return {"status": "success"}


@app.put("/post/{id}/undislike")
async def undislike_post(
    id: int,
    current_user: schema.User = Depends(deps.get_current_user),
    session: Session = Depends(deps.get_session),
):
    posting_service.remove_reaction(
        session,
        post_id=id,
        user_id=current_user.id,
        reaction_kind=models.ReactionKind.Dislike,
    )
    return {"status": "success"}


@app.get("/{user_id}/posts")
def get_users_posts(
    user_id: int,
    session: Session = Depends(deps.get_session),
):
    return posting_service.get_posts_by_user(user_id, session)


@app.post("/post/{post_id}/comment")
async def comment_on_post(
    post_id: int,
    attachment: fastapi.UploadFile,
    content: str = Body(),
    current_user: schema.User = Depends(deps.get_current_user),
    session: Session = Depends(deps.get_session),
    settings: config.Settings = Depends(deps.get_settings),
):
    comment_create = schema.CommentCreate(
        content=content, post_id=post_id, user_id=current_user.id
    )
    id = await comment_service.comment_on_post(
        s=session,
        comment_data=comment_create,
        attachment=attachment,
        settings=settings,
    )
    return {"status": "success", "result": id}


@app.post("/comment/{comment_id}/comment")
async def post_comment_reply(
    comment_id: int,
    attachment: fastapi.UploadFile,
    content: str = Body(),
    current_user: schema.User = Depends(deps.get_current_user),
    session: Session = Depends(deps.get_session),
    settings: config.Settings = Depends(deps.get_settings),
):
    comment_create = schema.CommentCreate(
        content=content, parent_id=comment_id, user_id=current_user.id
    )
    id = await comment_service.comment_on_post(
        s=session,
        comment_data=comment_create,
        attachment=attachment,
        settings=settings,
    )
    return {"status": "success", "result": id}


@app.get("/post/{post_id}/comment", response_model=list[schema.Comment])
async def get_comments_on_post(
    post_id: int,
    session: Session = Depends(deps.get_session),
):
    comments = comment_service.get_comments_per_post(
        s=session,
        post_id=post_id,
    )
    return comments
