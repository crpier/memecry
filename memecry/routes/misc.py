from relax.app import HTMLResponse, QueryInt, QueryStr, Router

import memecry.posts_service
import memecry.routes.auth
import memecry.routes.post
import memecry.schema
import memecry.views.common
import memecry.views.misc
import memecry.views.post
from memecry.posts_service import (
    get_posts,
    get_posts_by_search_query,
)
from memecry.types import Request

misc_router = Router()


@misc_router.path_function("GET", "/search")
async def search_posts(request: Request, query: QueryStr) -> HTMLResponse:
    if request.scope["from_htmx"]:
        return HTMLResponse(memecry.views.common.error_element("Page not implemented"))
    try:
        # TODO: good candidate for using Option type
        parsed_query = memecry.schema.Query(query)
    except ValueError as e:
        return HTMLResponse(memecry.views.common.error_element(str(e)))
    posts = await get_posts_by_search_query(
        parsed_query,
        viewer=request.user if request.user.is_authenticated else None,
        offset=0,
        limit=0,
    )
    home_view = memecry.views.misc.home_view(
        request.url_wrapper(memecry.routes.post.update_tags),
        request.url_wrapper(memecry.routes.post.get_post),
        request.url_wrapper(
            memecry.routes.post.update_searchable_content,
        ),
        posts,
        offset=0,
        limit=-1,
        keep_scrolling=False,
        partial=request.scope["from_htmx"],
    )
    return HTMLResponse(
        memecry.views.misc.page_root(
            [
                memecry.views.misc.page_nav(
                    signup_url=request.url_of(memecry.routes.auth.signup_form),
                    signin_url=request.url_of(memecry.routes.auth.signin_form),
                    signout_url=request.url_of(memecry.routes.auth.signout),
                    upload_form_url=request.url_of(memecry.routes.post.upload_form),
                    user=request.user if request.user.is_authenticated else None,
                ),
                home_view,
            ],
        ),
    )


@misc_router.path_function("GET", "/")
async def get_homepage(
    request: Request,
    limit: QueryInt = 5,
    offset: QueryInt = 0,
) -> HTMLResponse:
    posts = await get_posts(
        viewer=request.user if request.user.is_authenticated else None,
        limit=limit,
        offset=offset,
    )
    home_view = memecry.views.misc.home_view(
        request.url_wrapper(memecry.routes.post.update_tags),
        request.url_wrapper(memecry.routes.post.get_post),
        request.url_wrapper(
            memecry.routes.post.update_searchable_content,
        ),
        posts,
        offset=offset,
        limit=limit,
        keep_scrolling=True,
        partial=request.scope["from_htmx"],
    )
    if request.scope["from_htmx"]:
        return HTMLResponse(home_view)
    return HTMLResponse(
        memecry.views.misc.page_root(
            [
                memecry.views.misc.page_nav(
                    signup_url=request.url_of(memecry.routes.auth.signup_form),
                    signin_url=request.url_of(memecry.routes.auth.signin_form),
                    signout_url=request.url_of(memecry.routes.auth.signout),
                    upload_form_url=request.url_of(memecry.routes.post.upload_form),
                    user=request.user if request.user.is_authenticated else None,
                ),
                home_view,
            ],
        ),
    )
