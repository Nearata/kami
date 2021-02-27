from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.templating import _TemplateResponse

from kami.templating import templates
from kami.database import Anime, Fansub


class Homepage(HTTPEndpoint):
    async def get(self, request: Request) -> _TemplateResponse:
        context = {"request": request}

        anime = []
        for i in Anime.select():
            try:
                fansub = Fansub.get(id=i.fansub_id)
                fansub_name = fansub.name
            except Fansub.DoesNotExist:
                fansub_name = "N.A"

            anime.append({
                "name": i.name,
                "url": [
                    {
                        "name": parts.split(";")[0],
                        "href": parts.split(";")[1]
                    } for parts in i.url.split(",")
                ] if len(i.url) else [],
                "fansub": fansub_name
            })

        context.update({"anime": anime})

        return templates.TemplateResponse("home.html", context)
