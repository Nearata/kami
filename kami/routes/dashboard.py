from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.templating import _TemplateResponse

from kami.decorators import jwt_authenticated
from kami.templating import templates


class Dashboard(HTTPEndpoint):
    @jwt_authenticated
    async def get(self, request: Request) -> _TemplateResponse:
        return templates.TemplateResponse("dashboard.html", {"request": request})
