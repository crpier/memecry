from starlette.routing import Route, Router
from starlette.responses import HTMLResponse
from starlette.requests import Request

from memecry.views import common as common_views

def homepage(request: Request):
    return HTMLResponse(common_views.page_root(common_views.page_nav()).render())


app = Router(
    routes=[
        Route("/", homepage),
    ]
)
