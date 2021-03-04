from typing import Optional
from datetime import datetime

from starlette.requests import Request
from starlette.endpoints import HTTPEndpoint
from starlette.responses import RedirectResponse
from starlette.templating import _TemplateResponse

from kami.decorators import jwt_authenticated, jwt_is_admin
from kami.database import Fansub
from kami.templating import templates


class FansubEndpoint(HTTPEndpoint):
    def __response(self, request: Request, extra: Optional[dict] = None) -> _TemplateResponse:
        context = {
            "request": request,
            "fansub": Fansub.select()
        }

        if extra:
            context.update(extra)

        return templates.TemplateResponse("fansub/backend.html", context)

    @jwt_authenticated
    @jwt_is_admin
    async def get(self, request: Request) -> _TemplateResponse:
        return self.__response(request)

    @jwt_authenticated
    @jwt_is_admin
    async def post(self, request: Request):
        data = await request.form()

        fansub_id = data.get("id", "")

        try:
            Fansub.get(id=fansub_id)
        except Fansub.DoesNotExist:
            return self.__response(request, {"error": "The fansub you want to edit doesn't exists."})

        return RedirectResponse(request.url_for("fansub_edit", id=fansub_id), 303)


class FansubAdd(HTTPEndpoint):
    def __response(self, request: Request, extra: Optional[dict] = None) -> _TemplateResponse:
        context = {
            "request": request
        }

        if extra:
            context.update(extra)

        return templates.TemplateResponse("fansub/add.html", context)

    @jwt_authenticated
    @jwt_is_admin
    async def get(self, request: Request) -> _TemplateResponse:
        return self.__response(request)

    @jwt_authenticated
    @jwt_is_admin
    async def post(self, request: Request) -> _TemplateResponse:
        data = await request.form()

        name = data.get("name", "")

        errors = []

        if not name:
            errors.append("The field name is mandatory.")

        try:
            Fansub.get(name=name)
            errors.append("This fansub is already exists in the database.")
        except Fansub.DoesNotExist:
            pass

        if errors:
            return self.__response(request, {"errors": errors})

        Fansub.create(name=name)

        context = {
            "success": "Fansub added."
        }

        return self.__response(request, context)


class FansubRemove(HTTPEndpoint):
    def __response(self, request: Request, extra: Optional[dict] = None) -> _TemplateResponse:
        context = {
            "request": request,
            "fansub": Fansub.select()
        }

        if extra:
            context.update(extra)

        return templates.TemplateResponse("fansub/remove.html", context)

    @jwt_authenticated
    @jwt_is_admin
    async def get(self, request: Request) -> _TemplateResponse:
        return self.__response(request)

    @jwt_authenticated
    @jwt_is_admin
    async def post(self, request: Request) -> _TemplateResponse:
        data = await request.form()

        fansub_id = data.get("id", "")

        errors = []

        try:
            Fansub.get(id=fansub_id)
        except Fansub.DoesNotExist:
            errors.append("The fansub you want to remove doesn't exists in the database.")

        if errors:
            return self.__response(request, {"errors": errors})

        Fansub.get(id=fansub_id).delete_instance()

        context = {
            "success": "Fansub removed."
        }

        return self.__response(request, context)


class FansubEdit(HTTPEndpoint):
    def __response(self, request: Request, extra: Optional[dict] = None) -> _TemplateResponse:
        context = {"request": request}

        if extra:
            context.update(extra)

        return templates.TemplateResponse("fansub/edit.html", context)

    @jwt_authenticated
    @jwt_is_admin
    async def get(self, request: Request):
        fansub_id = request.path_params["id"]

        try:
            fansub = Fansub.get(id=fansub_id)
        except Fansub.DoesNotExist:
            return RedirectResponse(request.url_for("fansub"))

        context = {
            "name": fansub.name
        }

        return self.__response(request, context)

    @jwt_authenticated
    @jwt_is_admin
    async def post(self, request: Request) -> _TemplateResponse:
        data = await request.form()

        fansub_id = request.path_params["id"]
        name = data.get("name", "")

        errors = []

        if not name:
            errors.append("The field name is mandatory.")

        try:
            Fansub.get(id=fansub_id, name=name)
            errors.append("A fansub with this name already exists.")
        except Fansub.DoesNotExist:
            pass

        context = {
            "errors": errors,
            "name": name
        }

        if errors:
            return self.__response(request, context)

        fansub = Fansub.get(id=fansub_id)
        setattr(fansub, "name", name)
        setattr(fansub, "updated_at", datetime.now())
        fansub.save()

        context = {
            "success": "Fansub edited.",
            "name": fansub.name
        }

        return self.__response(request, context)
