from secrets import token_hex
from typing import Union

from starlette.endpoints import HTTPEndpoint
from starlette.responses import RedirectResponse
from starlette.requests import Request
from starlette.templating import _TemplateResponse
from httpx import AsyncClient

from kami.database import Users, UsersSessions
from kami.decorators import jwt_not_authenticated, jwt_authenticated
from kami.templating import templates
from kami.config import CAPTCHA, CAPTCHA_SECRET, CAPTCHA_SITE_KEY
from kami.jwt import jwt_encode
from kami.utils import verify_password


class Login(HTTPEndpoint):
    def __auth_response(self, request: Request, extra: dict = None, status_code: int = 200) -> _TemplateResponse:
        context = {
            "request": request,
            "captcha": CAPTCHA,
            "captcha_sitekey": CAPTCHA_SITE_KEY
        }

        if extra:
            context.update(extra)

        return templates.TemplateResponse("auth_login.html", context, status_code)

    @jwt_not_authenticated
    async def get(self, request: Request) -> _TemplateResponse:
        return self.__auth_response(request)

    @jwt_not_authenticated
    async def post(self, request: Request) -> Union[_TemplateResponse, RedirectResponse]:
        data = await request.form()

        username = data.get("name", "")
        password = data.get("password", "")
        captcha_response = data.get("h-captcha-response", "")

        errors = []

        if not username:
            errors.append("The field name is mandatory.")

        if not password:
            errors.append("The field password is mandatory.")

        if (CAPTCHA and not captcha_response):
            errors.append("The captcha is mandatory.")

        if errors:
            return self.__auth_response(request, {"errors": errors})

        user = Users.get_or_none(username=username)

        if not user:
            errors.append("Username or password not valid.")
        else:
            if not verify_password(password, user.password):
                errors.append("Username or password not valid.")

        if CAPTCHA:
            async with AsyncClient() as client:
                response = await client.post("https://hcaptcha.com/siteverify", data={
                    "response": captcha_response,
                    "secret": CAPTCHA_SECRET,
                    "sitekey": CAPTCHA_SITE_KEY
                })

                if not response.json()["success"]:
                    errors.append("Captcha not valid.")

        if errors:
            return self.__auth_response(request, {"errors": errors}, 401)

        sessions_count = len(UsersSessions.select().where(UsersSessions.user_id==user.id))
        sessions_count += 1

        jwt_token = jwt_encode({
            "username": username,
            "is_admin": user.is_admin,
            "session": sessions_count,
            "ip": request.client.host,
            "jti": token_hex(8)
        })

        UsersSessions.create(user_id=user.id, jwt_token=jwt_token)

        redirect = RedirectResponse(request.url_for("home"), status_code=303)
        redirect.set_cookie("jwt_token", str(jwt_token), samesite="strict")

        return redirect


class Logout(HTTPEndpoint):
    @jwt_authenticated
    async def get(self, request: Request) -> RedirectResponse:
        token = request.cookies.get("jwt_token")

        UsersSessions.get(jwt_token=token).delete_instance()

        response = RedirectResponse(request.url_for("login"), status_code=303)
        response.delete_cookie("jwt_token")

        return response
