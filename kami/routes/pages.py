from typing import Optional
from datetime import datetime

from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.exceptions import HTTPException
from starlette.templating import _TemplateResponse
from starlette.responses import RedirectResponse

from kami.templating import templates
from kami.decorators import jwt_authenticated, jwt_is_admin
from kami.database import Pages


class PagesEndpoint(HTTPEndpoint):
    def __response(self, request: Request, extra: Optional[dict] = None) -> _TemplateResponse:
        context = {
            "request": request,
            "pages": Pages.select()
        }

        if extra:
            context.update(extra)

        return templates.TemplateResponse("pages/backend.html", context)

    @jwt_authenticated
    @jwt_is_admin
    async def get(self, request: Request) -> _TemplateResponse:
        return self.__response(request)

    @jwt_authenticated
    @jwt_is_admin
    async def post(self, request: Request) -> _TemplateResponse:
        data = await request.form()

        page_id = data.get("id", "")

        try:
            Pages.get(id=page_id)
        except Pages.DoesNotExist:
            return self.__response(request, {"error": "The page you want to edit doesn't exists."})

        return RedirectResponse(request.url_for("pages_edit", id=page_id), 303)


class PagesGet(HTTPEndpoint):
    async def get(self, request: Request) -> _TemplateResponse:
        slug = request.path_params.get("slug", "")

        try:
            page = Pages.get(slug=slug)
        except Pages.DoesNotExist:
            raise HTTPException(404)

        context = {
            "request": request,
            "name": page.name,
            "content": page.content
        }

        return templates.TemplateResponse("pages/frontend.html", context)


class PagesAdd(HTTPEndpoint):
    def __response(self, request: Request, extra: Optional[dict] = None) -> _TemplateResponse:
        context = {
            "request": request
        }

        if extra:
            context.update(extra)

        return templates.TemplateResponse("pages/add.html", context)

    @jwt_authenticated
    @jwt_is_admin
    async def get(self, request: Request) -> _TemplateResponse:
        return self.__response(request)

    @jwt_authenticated
    @jwt_is_admin
    async def post(self, request: Request) -> _TemplateResponse:
        data = await request.form()

        name = data.get("name", "")
        slug = data.get("slug", "")
        icon = data.get("icon", "")
        content = data.get("content", "")

        errors = []

        if not name:
            errors.append("The field name is mandatory.")

        if not slug:
            errors.append("The field slug is mandatory.")

        if not icon:
            errors.append("The icon field is mandatory.")

        if not content:
            errors.append("The field content is mandatory.")

        try:
            Pages.get(name=name)
            errors.append("A page with this name already exists.")
        except Pages.DoesNotExist:
            pass

        if errors:
            return self.__response(request, {"errors": errors})

        Pages.create(
            name=name,
            slug=slug,
            icon=icon,
            content=content
        )

        return self.__response(request, {"success": "Page created."})


class PagesRemove(HTTPEndpoint):
    def __response(self, request: Request, extra: Optional[dict] = None) -> _TemplateResponse:
        context = {
            "request": request,
            "pages": Pages.select()
        }

        if extra:
            context.update(extra)

        return templates.TemplateResponse("pages/remove.html", context)

    @jwt_authenticated
    @jwt_is_admin
    async def get(self, request: Request) -> _TemplateResponse:
        return self.__response(request)

    @jwt_authenticated
    @jwt_is_admin
    async def post(self, request: Request) -> _TemplateResponse:
        data = await request.form()

        page_id = data.get("id", "")

        try:
            Pages.get(id=page_id).delete_instance()
        except Pages.DoesNotExist:
            return self.__response(request, {"error": "Page doesn't exists."})

        return self.__response(request, {"success": "Page removed."})


class PagesEdit(HTTPEndpoint):
    def __response(self, request: Request, extra: Optional[dict] = None) -> _TemplateResponse:
        context = {
            "request": request
        }

        if extra:
            context.update(extra)

        return templates.TemplateResponse("pages/edit.html", context)

    @jwt_authenticated
    @jwt_is_admin
    async def get(self, request: Request) -> _TemplateResponse:
        page_id = request.path_params.get("id", "")

        try:
            page = Pages.get(id=page_id)
        except Pages.DoesNotExist:
            return RedirectResponse(request.url_for("pages"), 303)

        context = {
            "name": page.name,
            "slug": page.slug,
            "icon": page.icon,
            "content": page.content
        }

        return self.__response(request, context)

    @jwt_authenticated
    @jwt_is_admin
    async def post(self, request: Request) -> _TemplateResponse:
        data = await request.form()

        page_id = request.path_params.get("id")
        name = data.get("name", "")
        slug = data.get("slug", "")
        icon = data.get("icon", "")
        content = data.get("content", "")

        errors = []

        if not name:
            errors.append("The field name is mandatory.")

        if not slug:
            errors.append("The field slug is mandatory.")

        if not icon:
            errors.append("The field icon is mandatory.")

        if not content:
            errors.append("The field content is mandatory.")

        try:
            page = Pages.get(id=page_id)
        except Pages.DoesNotExist:
            errors.append("The page you are trying to edit doesn't exists.")

        context = {
            "errors": errors,
            "name": name,
            "slug": slug,
            "icon": icon,
            "content": content
        }

        if errors:
            return self.__response(request, context)

        setattr(page, "name", name)
        setattr(page, "slug", slug)
        setattr(page, "icon", icon)
        setattr(page, "content", content)
        setattr(page, "updated_at", datetime.now())

        page.save()

        context = {
            "success": "Page edited.",
            "name": page.name,
            "slug": page.slug,
            "icon": page.icon,
            "content": page.content
        }

        return self.__response(request, context)
