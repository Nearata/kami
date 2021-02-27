from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.templating import _TemplateResponse

from kami.decorators import jwt_authenticated, jwt_is_admin
from kami.database import Anime, Fansub
from kami.templating import templates


class AdminAnime(HTTPEndpoint):
    def __response(self, request: Request, extra: dict = None) -> _TemplateResponse:
        context = {
            "request": request,
            "fansub": Fansub.select(),
            "anime": Anime.select()
        }

        if extra:
            context.update(extra)

        return templates.TemplateResponse("admin_anime.html", context)

    @jwt_authenticated
    @jwt_is_admin
    async def get(self, request: Request) -> _TemplateResponse:
        return self.__response(request)

    @jwt_authenticated
    @jwt_is_admin
    async def post(self, request: Request):
        data = await request.form()
        formtype = data.get("formtype")

        if formtype == "add_anime":
            return await self.__add_anime(request)

        if formtype == "remove_anime":
            return await self.__remove_anime(request)

        if formtype == "edit_anime":
            anime = Anime.get(name=data.get("name"))
            return RedirectResponse(request.url_for("admin_anime_edit", id=anime.id), 303)

        return RedirectResponse(request.url_for("admin_anime"))

    async def __add_anime(self, request: Request) -> _TemplateResponse:
        data = await request.form()

        name = data.get("name")
        fansub_name = data.get("fansub")
        url = data.get("url")

        try:
            Anime.get(name=name)
            return self.__response(request, {"error": "This anime is already in the database."})
        except Anime.DoesNotExist:
            pass

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

    async def __remove_anime(self, request: Request) -> _TemplateResponse:
        data = await request.form()

        name = data.get("name")

        try:
            Anime.get(name=name)
        except Anime.DoesNotExist:
            return self.__response(request, {"error": "This anime doesn't exists."})

        Anime.get(name=name).delete_instance()

        return self.__response(request, {"success": f"Anime {name} removed."})


class AdminAnimeEdit(HTTPEndpoint):
    def __response(self, request: Request, extra: dict = None) -> _TemplateResponse:
        context = {
            "request": request,
            "fansub": Fansub.select()
        }

        if extra:
            context.update(extra)

        return templates.TemplateResponse("admin_anime_edit.html", context)

    @jwt_authenticated
    @jwt_is_admin
    async def get(self, request: Request):
        anime_id = request.path_params["id"]

        try:
            anime = Anime.get(id=anime_id)
            fansub = Fansub.get(id=anime.fansub_id)
            fansub_name = fansub.name
        except Anime.DoesNotExist:
            return RedirectResponse(request.url_for("admin_anime"))
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

        name = data.get("name")
        fansub_name = data.get("fansub")
        url = data.get("url")

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

        anime.save()

        return self.__response(request, {
            "success": "Anime edited.",
            "title": anime.name,
            "current_fansub": fansub_name,
            "url": anime.url
        })
