import logging
import sys
import tempfile
from pathlib import Path

import fastapi
import fastapi.security
from fastapi import Depends, HTTPException

from src import db, deps, posting_service, schema, security, user_service

app = fastapi.FastAPI()

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

UPLOAD_STORAGE = Path(tempfile.mkdtemp())
logger.info("Uploading files to %s", UPLOAD_STORAGE)

ADMIN_ID = user_service.add_admin_user(db.session)
logger.info("First admin has id=%s", ADMIN_ID)

ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "admin": False,
    },
    "alice": {
        "username": "alice",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "admin": True,
    },
}


@app.post("/token")
async def login(form_data: fastapi.security.OAuth2PasswordRequestForm = Depends()):
    user = user_service.authenticate_user(
        db.session, form_data.username, form_data.password
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
def get_top_posts():
    return posting_service.get_top_posts(db.session)


@app.post("/post")
async def upload_post(title: str, file: fastapi.UploadFile):
    res = await posting_service.upload_post(
        db.session, title, file, content_dest=UPLOAD_STORAGE, user_id=ADMIN_ID
    )
    logger.info(res)
    return res


@app.get("/{user_id}/posts")
def get_users_posts(user_id: int):
    return posting_service.get_posts_by_user(user_id, db.session)
