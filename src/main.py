import logging

import fastapi
from fastapi.responses import HTMLResponse
import fastapi.security
import fastapi.staticfiles
import fastapi.templating
from fastapi import Body, Depends, FastAPI, Form, HTTPException, Request, Response
from pydantic import EmailStr
from simple_html.render import render
from simple_html.nodes import FlatGroup
from src.views import common

from src import (
    comment_service,
    config,
    deps,
    models,
    posting_service,
    schema,
    security,
    user_service,
)
from viewrender import (
    render_comments,
    render_login,
    render_new_comment_form,
    render_post,
    render_post_upload,
    get_posts_html,
    render_signup,
    render_search_results,
)

app = FastAPI()

logger = logging.getLogger()

# Initialize settings at the start,
# so that we don't have to wait for request to see errors (if any)
deps.get_db_session()

#### HTML endpoints ####
app.mount("/static", fastapi.staticfiles.StaticFiles(directory="static"), name="static")
app.mount("/media", fastapi.staticfiles.StaticFiles(directory="media"), name="static")


### Login stuff ###
### Misc ###
@app.get("/health")
def check_health():
    return {"message": "Everything OK"}


### Users ###
@app.get("/me")
def get_me(_: schema.User = Depends(deps.get_current_user)):
    return {"status": "NOT IMPLEMENTED"}


@app.get("/post/{post_id}")
def get_post(
    post_id: int,
    user: schema.User = Depends(deps.get_current_user_optional),
    session=Depends(deps.get_db_session),
):
    return render_post(
        post_id=post_id,
        user=user,
        session=session,
        partial=False,
    )


@app.get("/signup-form")
def get_signup_form():
    return render_signup()


@app.post("/signup")
async def create_new_user(
    response: Response,
    password: str = Form(),
    username: str = Form(),
    # Maybe make email optional only for dev?
    email: EmailStr | None = Form(),
    session=Depends(deps.get_db_session),
    settings=Depends(deps.get_settings),
):
    user_service.add_user(
        username=username, password=password, email=email, session=session
    )
    access_token = security.create_access_token(
        data={"sub": username}, settings=settings
    )
    response.set_cookie(key="Authorization", value=access_token, httponly=True)
    # response.headers["HX-Redirect"] = "/"
    response.headers["HX-Refresh"] = "true"
    response.status_code = 303
    return response


@app.get("/users/{username}/posts")
def get_users_posts(
    username: str,
    session=Depends(deps.get_db_session),
):
    return posting_service.get_posts_by_user(username, session)


### Comments ###
@app.post("/post/{post_id}/comment")
async def comment_on_post(
    post_id: int,
    file: fastapi.UploadFile,
    content: str = Body(),
    current_user: schema.User = Depends(deps.get_current_user),
    session=Depends(deps.get_db_session),
    settings: config.Settings = Depends(deps.get_settings),
):
    comment_create = schema.CommentCreate(
        content=content, post_id=post_id, user_id=current_user.id
    )
    await comment_service.post_comment(
        session=session,
        comment_data=comment_create,
        attachment=file,
        settings=settings,
    )
    return render_comments(post_id=post_id, user=current_user, session=session)


@app.post("/comment/{comment_id}/comment")
async def post_comment_reply(
    comment_id: int,
    attachment: fastapi.UploadFile | None = None,
    content: str = Body(),
    current_user: schema.User = Depends(deps.get_current_user),
    session=Depends(deps.get_db_session),
    settings: config.Settings = Depends(deps.get_settings),
):
    comment_create = schema.CommentCreate(
        content=content, parent_id=comment_id, user_id=current_user.id
    )
    post_id = await comment_service.post_comment(
        session=session,
        comment_data=comment_create,
        attachment=attachment,
        settings=settings,
    )
    return render_comments(post_id=post_id, user=current_user, session=session)


@app.get("/comment/{comment_id}/{post_id}/form")
def open_comment_form(comment_id: int, post_id: int):
    return render_new_comment_form(comment_id=comment_id, post_id=post_id)


@app.get("/post/{post_id}/comments")
async def get_comments_on_post(
    post_id: int,
    user: schema.User = Depends(deps.get_current_user_optional),
    session=Depends(deps.get_db_session),
):
    return render_comments(post_id=post_id, session=session, user=user)


#### REST endpoints for html ####
@app.put("/post/{id}/like")
async def like_post(
    id: int,
    current_user: schema.User = Depends(deps.get_current_user),
    session=Depends(deps.get_db_session),
):
    posting_service.add_reaction(
        session,
        post_id=id,
        user_id=current_user.id,
        reaction_kind=models.ReactionKind.Like,
    )
    return render_post(post_id=id, session=session, user=current_user)


@app.put("/comment/{id}/like")
async def like_comment(
    id: int,
    current_user: schema.User = Depends(deps.get_current_user),
    session=Depends(deps.get_db_session),
):
    post_id = comment_service.add_reaction(
        session,
        comment_id=id,
        user_id=current_user.id,
        reaction_kind=models.ReactionKind.Like,
    )
    return render_comments(post_id=post_id, user=current_user, session=session)


@app.put("/comment/{id}/dislike")
async def dislike_comment(
    id: int,
    current_user: schema.User = Depends(deps.get_current_user),
    session=Depends(deps.get_db_session),
):
    post_id = comment_service.add_reaction(
        session,
        comment_id=id,
        user_id=current_user.id,
        reaction_kind=models.ReactionKind.Dislike,
    )
    return render_comments(post_id=post_id, user=current_user, session=session)


@app.put("/post/{id}/dislike")
async def dislike_post(
    id: int,
    current_user: schema.User = Depends(deps.get_current_user),
    session=Depends(deps.get_db_session),
):
    posting_service.add_reaction(
        session,
        post_id=id,
        user_id=current_user.id,
        reaction_kind=models.ReactionKind.Dislike,
    )
    return render_post(post_id=id, session=session, user=current_user)


@app.middleware("http")
async def create_auth_header(request: Request, call_next):
    """
    Check if there are cookies set for authorization. If so, construct the
    Authorization header and modify the request (unless the header already
    exists!)
    """
    if "Authorization" not in request.headers and "Authorization" in request.cookies:
        access_token = request.cookies["Authorization"]

        request.headers.__dict__["_list"].append(
            (
                "authorization".encode(),
                f"Bearer {access_token}".encode(),
            )
        )
    elif (
        "Authorization" not in request.headers
        and "Authorization" not in request.cookies
    ):
        request.headers.__dict__["_list"].append(
            (
                "authorization".encode(),
                # TODO: fixme
                "Bearer 12345".encode(),
            )
        )

    response = await call_next(request)
    return response


@app.post("/token")
async def login(
    response: Response,
    form_data: fastapi.security.OAuth2PasswordRequestForm = Depends(),
    session=Depends(deps.get_db_session),
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
    response.set_cookie(key="Authorization", value=access_token, httponly=True)
    response.headers["HX-Refresh"] = "true"
    response.status_code = 303
    return response


@app.get("/upload-form")
def open_upload_form():
    return render_post_upload()


@app.get("/login-form")
def open_login_form():
    return render_login()


@app.post("/upload")
async def upload_post(
    response: Response,
    file: fastapi.UploadFile,
    title: str = Form(),
    settings: config.Settings = Depends(deps.get_settings),
    session=Depends(deps.get_db_session),
    current_user: schema.User = Depends(deps.get_current_user),
):
    new_post = schema.PostCreate(title=title, user_id=current_user.id)
    try:
        new_post_id = await posting_service.upload_post(
            post_data=new_post,
            session=session,
            uploaded_file=file,
            settings=settings,
        )
        response.status_code = 303
        response.headers["HX-Redirect"] = f"/post/{new_post_id}"
        return response
    except Exception:
        # TODO: move this html to a template
        return HTMLResponse(
            "<div class='bg-red-800 w-max py-1 px-2 rounded'>Something went wrong</div>"
        )


@app.post("/logout")
def log_out(response: Response):
    response.delete_cookie(key="Authorization")
    response.headers["HX-Refresh"] = "true"
    response.status_code = 303
    return response


@app.get("/posts")
def get_posts(
    offset: int = 0,
    limit: int = 0,
    settings: config.Settings = Depends(deps.get_settings),
    session=Depends(deps.get_db_session),
    optional_current_user: schema.User | None = Depends(deps.get_current_user_optional),
):
    if limit == 0:
        limit = settings.DEFAULT_POSTS_PER_PAGE
    elements = get_posts_html(
        session=session, user=optional_current_user, limit=limit, offset=offset
    )
    return HTMLResponse(render(FlatGroup(*elements)))


@app.get("/search")
def search(
    query: str,
    session=Depends(deps.get_db_session),
    user: schema.User = Depends(deps.get_current_user_optional),
):
    elements = render_search_results(query=query, user=user, session=session)
    return HTMLResponse(
        render(common.page_root(user=user, partial=FlatGroup(*elements)))
    )


@app.get("/")
def get_index(
    offset: int = 0,
    limit: int = 0,
    settings: config.Settings = Depends(deps.get_settings),
    session=Depends(deps.get_db_session),
    optional_current_user: schema.User | None = Depends(deps.get_current_user_optional),
):
    if limit == 0:
        limit = settings.DEFAULT_POSTS_PER_PAGE
    elements = get_posts_html(
        session=session, user=optional_current_user, limit=limit, offset=offset
    )

    return HTMLResponse(
        render(
            common.page_root(user=optional_current_user, partial=FlatGroup(*elements))
        )
    )
