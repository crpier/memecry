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
    if user_id != request.user.id:
        return HTMLResponse(
            error_element("You can only update your own user"), status_code=403
        )

    async with request.parse_form(memecry.schema.UserUpdate) as user_update:
        await memecry.user_service.update_user(user_id, user_update)
    return Response()
