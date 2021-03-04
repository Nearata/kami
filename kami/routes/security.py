from typing import Union, Optional

from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.templating import _TemplateResponse
from starlette.responses import RedirectResponse

from kami.decorators import jwt_authenticated
from kami.templating import templates
from kami.jwt import jwt_decode
from kami.database import Users
from kami.utils import verify_password, password_requirements, hash_password


class SecurityEndpoint(HTTPEndpoint):
    @jwt_authenticated
    async def get(self, request: Request) -> _TemplateResponse:
        return templates.TemplateResponse("security/backend.html", {"request": request})


class ChangePassword(HTTPEndpoint):
    def __response(self, request: Request, extra: Optional[dict] = None) -> _TemplateResponse:
        context = {"request": request}

        if extra:
            context.update(extra)

        return templates.TemplateResponse("security/changepassword.html", context)

    @jwt_authenticated
    async def get(self, request: Request) -> _TemplateResponse:
        return self.__response(request)

    @jwt_authenticated
    async def post(self, request: Request) -> Union[_TemplateResponse, RedirectResponse]:
        data = await request.form()

        current_password = data.get("password", "")
        new_password = data.get("new_password", "")
        confirm_password = data.get("confirm_password", "")

        errors = []

        if not current_password:
            errors.append("The field password is mandatory.")

        if not new_password:
            errors.append("The field new password is mandatory.")

        if not confirm_password:
            errors.append("The field confirm password is mandatory.")

        if errors:
            return self.__response(request, {"errors": errors})

        jwt = request.cookies.get("jwt_token", "")
        jwt_decoded = jwt_decode(jwt)
        username = jwt_decoded.get("username")
        user = Users.get(username=username)
        hashed_password = user.password

        if verify_password(current_password, hashed_password) and current_password == new_password:
            errors.append("The new password is equal to the current one.")
        else:
            errors.append("The current password is wrong.")

        if new_password != confirm_password:
            errors.append("New password and confirm password are not equal.")

        psw_req_errors = password_requirements(new_password)
        for i in psw_req_errors:
            errors.append(i)

        new_hashed_password = hash_password(new_password)
        if new_hashed_password is None:
            errors.append("Unable to change password. Please contact an administrator.")

        if errors:
            return self.__response(request, {"errors": errors})

        setattr(user, "password", new_hashed_password)
        user.save()

        return self.__response(request, {"success": "Password changed."})
