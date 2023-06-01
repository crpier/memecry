import logging

import fastapi
import fastapi.security
import fastapi.staticfiles
import fastapi.templating
from fastapi import (
    BackgroundTasks,
    Body,
    Depends,
    FastAPI,
    Form,
    HTTPException,
    Request,
    Response,
)
from fastapi.responses import HTMLResponse
from pydantic import EmailStr

import src.views.posts
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
from src.views import common as common_views
from src.views import posts as posts_views

app = FastAPI()

logger = logging.getLogger()

# Initialize settings at the start,
# so that we don't have to wait for request to see errors (if any)
deps.get_db_session()

#### HTML endpoints ####
app.mount("/static", fastapi.staticfiles.StaticFiles(directory="static"), name="static")
app.mount(
    "/media",
    fastapi.staticfiles.StaticFiles(directory=deps.get_settings().MEDIA_UPLOAD_STORAGE),
    name="media",
)


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
    post = posting_service.get_post_by_id(session=session, post_id=post_id)
    return HTMLResponse(posts_views.post_view(post=post, user=user, partial_html=False))


@app.get("/signup-form")
def get_signup_form():
    return HTMLResponse(common_views.signup_form())


@app.post("/signup")
async def create_new_user(
    response: Response,
    password: str = Form(),
    username: str = Form(),
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
    file: fastapi.UploadFile | None = None,
    # TODO: we should allow comments with no text, but an attachment
    content: str = Body(),
    user: schema.User = Depends(deps.get_current_user),
    session=Depends(deps.get_db_session),
    settings: config.Settings = Depends(deps.get_settings),
):
    # TODO: the function should expect a CommentCreate object in formdata,
    # and perform the validation logic when instantiating
    comment_create = schema.CommentCreate(
        content=content, post_id=post_id, user_id=user.id
    )
    await comment_service.post_comment(
        session=session,
        comment_data=comment_create,
        attachment=file,
        settings=settings,
    )
    comments_dict, ids_tree = comment_service.get_comment_tree(
        post_id=post_id, session=session
    )
    for comment in comments_dict.values():
        comment = comment_service.prepare_comment_for_viewing(
            session=session, comment=comment, user=user
        )
    return HTMLResponse(
        posts_views.comment_tree_view(
            comments_dict=comments_dict,  # type: ignore
            ids_tree=ids_tree,
            post_id=post_id,
        )
    )


@app.post("/comment/{comment_id}/comment")
async def reply_to_comment(
    comment_id: int,
    file: fastapi.UploadFile | None = None,
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
        attachment=file,
        settings=settings,
    )
    # return render_comments(post_id=post_id, user=current_user, session=session)
    return await get_comments_on_post(
        post_id=post_id, user=current_user, session=session
    )


@app.get("/comment/{comment_id}/{post_id}/form")
def open_comment_form(comment_id: int, post_id: int):
    post_url = f"/comment/{comment_id}/comment"
    return HTMLResponse(
        posts_views.new_comment_form_view(post_url=post_url, post_id=post_id)
    )


@app.get("/post/{post_id}/comments")
async def get_comments_on_post(
    post_id: int,
    user: schema.User = Depends(deps.get_current_user_optional),
    session=Depends(deps.get_db_session),
):
    comments_dict, ids_tree = comment_service.get_comment_tree(
        post_id=post_id, session=session
    )
    # TODO: this should be done in the service
    for comment in comments_dict.values():
        comment = comment_service.prepare_comment_for_viewing(
            session=session, comment=comment, user=user
        )
    return HTMLResponse(
        posts_views.comment_tree_view(
            comments_dict=comments_dict,  # type: ignore
            ids_tree=ids_tree,
            post_id=post_id,
        )
    )


#### REST endpoints for html ####
@app.put("/post/{post_id}/like")
async def like_post(
    post_id: int,
    current_user: schema.User = Depends(deps.get_current_user),
    session=Depends(deps.get_db_session),
):
    posting_service.add_reaction(
        session,
        post_id=post_id,
        user_id=current_user.id,
        reaction_kind=models.ReactionKind.Like,
    )
    post = posting_service.get_post_by_id(
        session=session, post_id=post_id, viewer=current_user
    )
    return HTMLResponse(
        posts_views.post_view(post=post, user=current_user, partial_html=True)
    )


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
    comments_dict, ids_tree = comment_service.get_comment_tree(
        post_id=post_id, session=session
    )
    # TODO: this should be done in the service
    for comment in comments_dict.values():
        comment = comment_service.prepare_comment_for_viewing(
            session=session, comment=comment, user=current_user
        )
    return HTMLResponse(
        posts_views.comment_tree_view(
            comments_dict=comments_dict,  # type: ignore
            ids_tree=ids_tree,
            post_id=post_id,
        )
    )


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
    comments_dict, ids_tree = comment_service.get_comment_tree(
        post_id=post_id, session=session
    )
    # TODO: this should be done in the service
    for comment in comments_dict.values():
        comment = comment_service.prepare_comment_for_viewing(
            session=session, comment=comment, user=current_user
        )
    return HTMLResponse(
        posts_views.comment_tree_view(
            comments_dict=comments_dict,  # type: ignore
            ids_tree=ids_tree,
            post_id=post_id,
        )
    )


@app.put("/post/{post_id}/dislike")
async def dislike_post(
    post_id: int,
    current_user: schema.User = Depends(deps.get_current_user),
    session=Depends(deps.get_db_session),
):
    posting_service.add_reaction(
        session,
        post_id=post_id,
        user_id=current_user.id,
        reaction_kind=models.ReactionKind.Dislike,
    )
    post = posting_service.get_post_by_id(
        session=session, post_id=post_id, viewer=current_user
    )
    return HTMLResponse(
        posts_views.post_view(post=post, user=current_user, partial_html=True)
    )


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


@app.post("/logout")
def log_out(response: Response):
    response.delete_cookie(key="Authorization")
    response.headers["HX-Refresh"] = "true"
    response.status_code = 303
    return response


@app.get("/upload-form")
def open_upload_form():
    return HTMLResponse(common_views.post_upload_form())


@app.get("/login-form")
def open_login_form():
    return HTMLResponse(common_views.login_form())


@app.post("/upload")
async def upload_post(
    response: Response,
    file: fastapi.UploadFile,
    background_tasks: BackgroundTasks,
    title: str = Form(),
    settings: config.Settings = Depends(deps.get_settings),
    session=Depends(deps.get_db_session),
    current_user: schema.User = Depends(deps.get_current_user),
):
    new_post = schema.PostCreate(title=title, user_id=current_user.id)
    logger.info("Uploading post with file %s", file.filename)
    try:
        new_post_id = await posting_service.upload_post(
            post_data=new_post,
            session=session,
            uploaded_file=file,
            settings=settings,
        )
        logger.info("Finished uploading post %s", new_post_id)

        background_tasks.add_task(
            posting_service.index_post,
            session=session,
            post_id=new_post_id,
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


@app.get("/search-form")
def redirect_to_search(
    response: Response,
    query: str,
):
    response.status_code = 303
    response.headers["HX-Redirect"] = f"/search?query={query}"
    return response


@app.get("/search")
def search(
    query: str,
    session=Depends(deps.get_db_session),
    user: schema.User = Depends(deps.get_current_user_optional),
):
    posts = posting_service.search_through_posts(
        query=query, session=session, user=user
    )
    return HTMLResponse(
        src.views.posts.posts_view(
            posts=posts,
            user=user,
            partial_html=False,
        )
    )


@app.get("/")
def get_index(
    offset: int = 0,
    limit: int = 0,
    partial_html: bool = False,
    settings: config.Settings = Depends(deps.get_settings),
    session=Depends(deps.get_db_session),
    optional_current_user: schema.User | None = Depends(deps.get_current_user_optional),
):
    if limit == 0:
        limit = settings.DEFAULT_POSTS_PER_PAGE
    posts = posting_service.get_posts(
        session=session, limit=limit, offset=offset, viewer=optional_current_user
    )
    if len(posts) == limit:
        scroll_continue_url = f"/?offset={limit+offset}&partial_html=true"
    else:
        scroll_continue_url = None
    return HTMLResponse(
        src.views.posts.posts_view(
            posts=posts,
            user=optional_current_user,
            partial_html=partial_html,
            scroll_continue_url=scroll_continue_url,
        )
    )
