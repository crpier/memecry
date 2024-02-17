from relax.app import HTMLResponse, QueryInt, QueryStr, Router
from starlette.responses import Response

import memecry.posts_service
import memecry.routes.auth
import memecry.routes.post
import memecry.schema
import memecry.types
import memecry.views.common
import memecry.views.misc
import memecry.views.post

misc_router = Router()


@misc_router.path_function("GET", "/")
async def get_homepage(
    request: memecry.types.Request,
    limit: QueryInt = 5,
    offset: QueryInt = 0,
) -> HTMLResponse:
    posts = await memecry.posts_service.get_posts(
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


@misc_router.path_function("GET", "/search")
async def search_posts(
    request: memecry.types.Request, query: QueryStr
) -> HTMLResponse | Response:
    try:
        # TODO: good candidate for using Option type
        parsed_query = memecry.schema.Query(query)
    except ValueError as e:
        return HTMLResponse(memecry.views.common.error_element(str(e)))

    if request.scope["from_htmx"]:
        resp = Response()
        resp.headers[
            "HX-Redirect"
            # TODO:relax should handle query params too
        ] = f"{request.url_of(search_posts)}?query={query}"  # type: ignore
        resp.status_code = 201
        return resp

    posts = await memecry.posts_service.get_posts_by_search_query(
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
