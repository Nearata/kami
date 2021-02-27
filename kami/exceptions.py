from starlette.requests import Request
from starlette.exceptions import HTTPException
from starlette.templating import _TemplateResponse

from kami.templating import templates


async def not_found(request: Request, exc: HTTPException) -> _TemplateResponse:
    return templates.TemplateResponse("exceptions/404.html", {"request": request}, exc.status_code)
