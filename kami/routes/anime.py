from typing import Optional
from datetime import datetime

from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.templating import _TemplateResponse

from kami.decorators import jwt_authenticated, jwt_is_admin
from kami.database import Anime, Fansub
from kami.templating import templates


class AnimeEndpoint(HTTPEndpoint):
    def __response(self, request: Request, extra: Optional[dict] = None) -> _TemplateResponse:
        context = {
            "request": request,
            "anime": Anime.select()
        }

        if extra:
            context.update(extra)

        return templates.TemplateResponse("anime/backend.html", context)

    @jwt_authenticated
    @jwt_is_admin
    async def get(self, request: Request) -> _TemplateResponse:
        return self.__response(request)

    @jwt_authenticated
    @jwt_is_admin
    async def post(self, request: Request) -> _TemplateResponse:
        data = await request.form()

        anime_id = data.get("id", "")

        try:
            Anime.get(id=anime_id)
        except Anime.DoesNotExist:
            return self.__response(request, {"error": "The anime you want to edit doesn't exists."})

        return RedirectResponse(request.url_for("anime_edit", id=anime_id), 303)


class AnimeAdd(HTTPEndpoint):
    def __response(self, request: Request, extra: Optional[dict] = None) -> _TemplateResponse:
        context = {
            "request": request,
            "anime": Anime.select(),
            "fansub": Fansub.select()
        }

        if extra:
            context.update(extra)

        return templates.TemplateResponse("anime/add.html", context)

    @jwt_authenticated
    @jwt_is_admin
    async def get(self, request: Request) -> _TemplateResponse:
        return self.__response(request)

    @jwt_authenticated
    @jwt_is_admin
    async def post(self, request: Request) -> _TemplateResponse:
        data = await request.form()

        name = data.get("name", "")
        fansub_name = data.get("fansub", "")
        url = data.get("url", "")

        errors = []

        if not name:
            errors.append("The field name is mandatory.")

        if not url:
            errors.append("The field url is mandatory.")

        try:
            Anime.get(name=name)
            errors.append("This anime is already in the database.")
        except Anime.DoesNotExist:
            pass

        if errors:
            return self.__response(request, {"errors": errors})

        try:
            fansub = Fansub.get(name=fansub_name)
            fansub_id = fansub.id
        except Fansub.DoesNotExist:
            fansub_id = ""

        Anime.create(
            name=name,
            fansub_id=fansub_id,
            url=url
        )

        return self.__response(request, {"success": "Anime added."})


class AnimeRemove(HTTPEndpoint):
    def __response(self, request: Request, extra: Optional[dict] = None) -> _TemplateResponse:
        context = {
            "request": request,
            "anime": Anime.select()
        }

        if extra:
            context.update(extra)

        return templates.TemplateResponse("anime/remove.html", context)

    @jwt_authenticated
    @jwt_is_admin
    async def get(self, request: Request) -> _TemplateResponse:
        return self.__response(request)

    @jwt_authenticated
    @jwt_is_admin
    async def post(self, request: Request) -> _TemplateResponse:
        data = await request.form()

        anime_id = data.get("id", "")

        try:
            Anime.get(id=anime_id).delete_instance()
        except Anime.DoesNotExist:
            return self.__response(request, {"error": "The anime you want to remove doesn't exists."})

        return self.__response(request, {"success": "Anime removed."})


class AnimeEdit(HTTPEndpoint):
    def __response(self, request: Request, extra: dict = None) -> _TemplateResponse:
        context = {
            "request": request,
            "fansub": Fansub.select()
        }

        if extra:
            context.update(extra)

        return templates.TemplateResponse("anime/edit.html", context)

    @jwt_authenticated
    @jwt_is_admin
    async def get(self, request: Request):
        anime_id = request.path_params["id"]

        try:
            anime = Anime.get(id=anime_id)
            fansub = Fansub.get(id=anime.fansub_id)
            fansub_name = fansub.name
        except Anime.DoesNotExist:
            return RedirectResponse(request.url_for("anime"))
        except Fansub.DoesNotExist:
            fansub_name = ""

        return self.__response(request, {
            "title": anime.name,
            "current_fansub": fansub_name,
            "url": anime.url.replace(",", "\n")
        })

    @jwt_authenticated
    @jwt_is_admin
    async def post(self, request: Request) -> _TemplateResponse:
        data = await request.form()
        anime_id = request.path_params["id"]

        name = data.get("name", "")
        fansub_name = data.get("fansub", "")
        url = data.get("url", "")

        errors = []

        if not name:
            errors.append("The field name is mandatory.")

        if not fansub_name:
            errors.append("The field fansub is mandatory.")

        if not url:
            errors.append("The field url is mandatory.")

        context = {
            "errors": errors,
            "title": name,
            "current_fansub": fansub_name,
            "url": url.replace(",", "\n")
        }

        if errors:
            return self.__response(request, context)

        anime = Anime.get(id=anime_id)

        try:
            fansub = Fansub.get(name=fansub_name)
            fansub_id = fansub.id
            fansub_name = fansub.name
        except Fansub.DoesNotExist:
            fansub_id = ""
            fansub_name = ""

        setattr(anime, "name", name)
        setattr(anime, "fansub_id", fansub_id)
        setattr(anime, "url", url)
        setattr(anime, "updated_at", datetime.now())

        anime.save()

        context = {
            "success": "Anime edited.",
            "title": anime.name,
            "current_fansub": fansub_name,
            "url": anime.url.replace(",", "\n")
        }

        return self.__response(request, context)
