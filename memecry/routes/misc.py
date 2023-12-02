from relax.app import HTMLResponse, QueryInt, QueryStr, Router

import memecry.posts_service
import memecry.routes.auth
import memecry.routes.post
import memecry.schema
import memecry.views.common
from memecry.posts_service import (
    get_posts,
    get_posts_by_search_query,
)
from memecry.types import Request

misc_router = Router()


@misc_router.path_function("GET", "/")
async def get_homepage(
    request: Request,
    query: QueryStr | None = None,
    limit: QueryInt = 5,
    offset: QueryInt = 0,
) -> HTMLResponse:
    if query:
        try:
            # TODO: good candidate for using Option type
            parsed_query = memecry.schema.Query(query)
        except ValueError as e:
            return HTMLResponse(memecry.views.common.error_element(str(e)))
        posts = await get_posts_by_search_query(
            parsed_query,
            viewer=request.user if request.user.is_authenticated else None,
        )
    else:
        posts = await get_posts(
            viewer=request.user if request.user.is_authenticated else None,
            limit=limit,
            offset=offset,
        )
    home_view = memecry.views.common.home_view(
        request.url_wrapper(memecry.routes.post.update_tags),
        request.url_wrapper(memecry.routes.post.get_post),
        request.url_wrapper(
            memecry.routes.post.update_searchable_content,
        ),
        posts,
        offset=offset,
        limit=limit,
        keep_scrolling=query is None,
        partial=request.scope["from_htmx"],
    )
    if request.scope["from_htmx"]:
        return HTMLResponse(home_view)
    return HTMLResponse(
        memecry.views.common.page_root(
            [
                memecry.views.common.page_nav(
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
