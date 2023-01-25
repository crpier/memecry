from sqlalchemy.orm import Session
import logging

import fastapi
import fastapi.security
from fastapi import Body, Depends, HTTPException

from src import deps, posting_service, schema, security, user_service, config


app = fastapi.FastAPI()

logger = logging.getLogger()

# Initialize settings at the start,
# so that we don't have to wait for request to see errors (if any)
deps.get_settings()


@app.post("/token")
async def login(
    form_data: fastapi.security.OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(deps.get_session),
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
    access_token = security.create_access_token(data={"sub": user.username})
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
    settings: config.Settings = Depends(deps.get_settings),
    session: Session = Depends(deps.get_session),
):
    res = await posting_service.upload_post(
        session,
        title,
        file,
        content_dest=settings.UPLOAD_STORAGE,
        user_id=settings.SUPER_ADMIN_ID,
        settings=settings,
    )
    logger.info(res)
    return {"status": "success"}


@app.get("/{user_id}/posts")
def get_users_posts(
    user_id: int,
    session: Session = Depends(deps.get_session),
):
    return posting_service.get_posts_by_user(user_id, session)
