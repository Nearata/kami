from starlette.requests import Request
from starlette.endpoints import HTTPEndpoint
from starlette.responses import RedirectResponse
from starlette.templating import _TemplateResponse

from kami.decorators import jwt_authenticated, jwt_is_admin
from kami.database import Fansub
from kami.templating import templates


class AdminFansub(HTTPEndpoint):
    def __response(self, request: Request, extra: dict = None) -> _TemplateResponse:
        context = {
            "request": request,
            "fansub": Fansub.select()
        }

        if extra:
            context.update(extra)

        return templates.TemplateResponse("admin_fansub.html", context)

    @jwt_authenticated
    @jwt_is_admin
    async def get(self, request: Request) -> _TemplateResponse:
        return self.__response(request)

    @jwt_authenticated
    @jwt_is_admin
    async def post(self, request: Request):
        data = await request.form()
        formtype = data.get("formtype")

        if formtype == "add_fansub":
            return await self.__add_fansub(request)

        if formtype == "remove_fansub":
            return await self.__remove_fansub(request)

        if formtype == "edit_fansub":
            fansub = Fansub.get(name=data.get("name"))
            return RedirectResponse(request.url_for("admin_fansub_edit", id=fansub.id), 303)

        return RedirectResponse(request.url_for("admin_fansub"), status_code=303)

    async def __add_fansub(self, request: Request) -> _TemplateResponse:
        data = await request.form()

        name = data.get("name")

        try:
            Fansub.get(name=name)
            return self.__response(request, {"error": "This fansub already exists in the database."})
        except Fansub.DoesNotExist:
            pass

        Fansub.create(name=name)

        return self.__response(request, {"success": "Fansub added."})

    async def __remove_fansub(self, request: Request):
        data = await request.form()

        name = data.get("name")

        if not name:
            return RedirectResponse(request.url_for("admin_fansub"), status_code=303)

        try:
            Fansub.get(name=name)
        except Fansub.DoesNotExist:
            return self.__response(request, {"error": "This fansub doesn't exists in the database."})

        Fansub.get(name=name).delete_instance()

        return self.__response(request, {"success": "Fansub removed."})


class AdminFansubEdit(HTTPEndpoint):
    def __response(self, request: Request, extra: dict = None) -> _TemplateResponse:
        context = {"request": request}

        if extra:
            context.update(extra)

        return templates.TemplateResponse("admin_fansub_edit.html", context)

    @jwt_authenticated
    @jwt_is_admin
    async def get(self, request: Request):
        fansub_id = request.path_params["id"]

        try:
            fansub = Fansub.get(id=fansub_id)
        except Fansub.DoesNotExist:
            return RedirectResponse(request.url_for("admin_fansub"))

        return self.__response(request, {
            "name": fansub.name,
        })

    @jwt_authenticated
    @jwt_is_admin
    async def post(self, request: Request) -> _TemplateResponse:
        data = await request.form()
        fansub_id = request.path_params["id"]

        name = data.get("name")

        fansub = Fansub.get(id=fansub_id)
        setattr(fansub, "name", name)
        fansub.save()

        return self.__response(request, {
            "success": "Fansub edited.",
            "name": fansub.name
        })
