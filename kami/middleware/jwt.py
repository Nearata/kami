from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from kami.jwt import jwt_decode


class JwtMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        jwt_token = request.cookies.get("jwt_token", "")
        request.state.is_admin = False

        if jwt_token:
            jwt_decoded = jwt_decode(jwt_token)
            request.state.is_admin = jwt_decoded.get("is_admin", False)

        return await call_next(request)
