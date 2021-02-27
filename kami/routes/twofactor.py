from typing import Optional

from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.templating import _TemplateResponse

from pyotp import random_base32 as otp_random_base32
from pyotp import TOTP

from kami.decorators import jwt_authenticated
from kami.templating import templates
from kami.jwt import jwt_decode
from kami.database import Users
from kami.utils import verify_password
from kami.config import SITE_NAME


class TwoFactor(HTTPEndpoint):
    def __response(self, request: Request, extra: Optional[dict] = None, status_code: Optional[int] = 200) -> _TemplateResponse:
        context = {"request": request}

        if extra:
            context.update(extra)

        return templates.TemplateResponse("security_twofactor.html", context=context, status_code=status_code)

    @jwt_authenticated
    async def get(self, request: Request) -> _TemplateResponse:
        token = request.cookies.get("jwt_token", "")
        token_decoded = jwt_decode(token)

        username = token_decoded.get("username")
        user = Users.get(username=username)
        is_twofa = user.is_twofa

        context = {"is_twofa": is_twofa}

        secret = user.twofa_secret or otp_random_base32()
        totp = TOTP(secret).provisioning_uri(username, SITE_NAME)

        if not is_twofa:
            context.update({
                "qrcode": totp,
                "secret": secret
            })

        return self.__response(request, context)

    @jwt_authenticated
    async def post(self, request: Request) -> _TemplateResponse:
        data = await request.form()

        password = data.get("password", "")
        code = data.get("code", "")

        token = request.cookies.get("jwt_token", "")
        token_decoded = jwt_decode(token)

        username = token_decoded.get("username")
        user = Users.get(username=username)
        is_twofa = user.is_twofa

        secret = data.get("secret", user.twofa_secret)

        context = {"is_twofa": is_twofa}
        errors = []

        if not secret:
            errors.append("Invalid request. Please try again.")
            context.update({"errors": errors})
            return self.__response(request, context, 400)

        if not password:
            errors.append("The password field is mandatory.")

        if not code:
            errors.append("The code field is mandatory.")

        if not verify_password(password, user.password):
            errors.append("The password is not valid.")

        totp = TOTP(secret).provisioning_uri(username, SITE_NAME)

        if not is_twofa:
            context.update({
                "qrcode": totp,
                "secret": secret
            })

        if errors:
            context.update({"errors": errors})
            return self.__response(request, context, 401)

        if is_twofa:
            user.is_twofa = False
            user.twofa_secret = ""

            new_secret = otp_random_base32()
            new_totp = TOTP(new_secret).provisioning_uri(username, SITE_NAME)
            context.update({
                "qrcode": new_totp,
                "secret": new_secret
            })
        else:
            user.is_twofa = True
            user.twofa_secret = secret
            del context["qrcode"]
            del context["secret"]

        user.save()

        context.update({
            "success": f"2Factor {'enabled' if user.is_twofa else 'disabled'}",
            "is_twofa": user.is_twofa
        })

        return self.__response(request, context)
