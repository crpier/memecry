from loguru import logger
from relax.app import (
    AuthScope,
    HTMLResponse,
    PathInt,
    Router,
)
from starlette.responses import Response

import memecry.schema
import memecry.user_service
import memecry.views.misc
import memecry.views.user
from memecry.views.common import error_element

router = Router()


@router.path_function("GET", "/preferences", auth_scopes=[AuthScope.Authenticated])
async def preferences_page(request: memecry.schema.Request) -> HTMLResponse:
    if request.scope["from_htmx"]:
        msg = "Request on this endpoint from htmx is not supported"
        return HTMLResponse(error_element(msg))
    preferences = memecry.views.user.preferences_page(user=request.user)
    response = memecry.views.misc.page_root(
        [
            memecry.views.misc.page_nav(
                user=request.user if request.user.is_authenticated else None,
            ),
            preferences,
        ],
    )
    return HTMLResponse(response)


@router.path_function("PUT", "/user/{user_id}", auth_scopes=[AuthScope.Authenticated])
async def update_user(request: memecry.schema.Request, user_id: PathInt) -> Response:
    logger.debug("Update requested for user {}", user_id)
    if user_id != request.user.id:
        return HTMLResponse(error_element("You can only update your own user"))

    async with request.parse_form(memecry.schema.UserUpdate) as user_update:
        await memecry.user_service.update_user(user_id, user_update)
    logger.debug("User {} updated", user_id)
    return Response(headers={"HX-Refresh": "true"})
