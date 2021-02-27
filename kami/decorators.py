from functools import wraps
from typing import Callable, Any

from starlette.requests import Request
from starlette.responses import PlainTextResponse, RedirectResponse
from jwt.exceptions import InvalidTokenError

from kami.database import UsersSessions
from kami.jwt import jwt_decode


def jwt_authenticated(func: Callable) -> Callable:
    @wraps(func)
    async def decorator(*args: Any, **kwargs: Any) -> Callable:
        request = get_request(args)
        jwt_token = request.cookies.get("jwt_token", "")

        if not jwt_token:
            return RedirectResponse(request.url_for("home"))

        try:
            jwt_decode(jwt_token)
        except InvalidTokenError:
            try:
                UsersSessions.get(jwt_token=jwt_token).delete_instance()
            except UsersSessions.DoesNotExist:
                pass

            response = RedirectResponse(request.url_for("home"))
            response.delete_cookie("jwt_token")

            return response

        return await func(*args, **kwargs)
    return decorator

def jwt_not_authenticated(func: Callable) -> Callable:
    @wraps(func)
    async def decorator(*args: Any, **kwargs: Any) -> Callable:
        request = get_request(args)

        if request.cookies.get("jwt_token"):
            return RedirectResponse(request.url_for("dashboard"))

        return await func(*args, **kwargs)
    return decorator

def jwt_is_admin(func: Callable) -> Callable:
    @wraps(func)
    async def decorator(*args: Any, **kwargs: Any) -> Callable:
        request = get_request(args)

        if not request.state.is_admin:
            return PlainTextResponse("403 No Permission.", 403)

        return await func(*args, **kwargs)
    return decorator

def get_request(args: tuple) -> Request:
    request = None

    for i in args:
        if isinstance(i, Request):
            request = i

    assert isinstance(request, Request)

    return request
