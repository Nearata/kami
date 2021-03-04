from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from kami.routes.home import Homepage
from kami.routes.auth import Login, Logout
from kami.routes.dashboard import Dashboard
from kami.routes.anime import AnimeEndpoint, AnimeAdd, AnimeRemove, AnimeEdit
from kami.routes.fansub import FansubEndpoint, FansubAdd, FansubRemove, FansubEdit
from kami.routes.pages import PagesEndpoint, PagesAdd, PagesRemove, PagesEdit, PagesGet
from kami.routes.security import SecurityEndpoint, ChangePassword
from kami.exceptions import not_found
from kami.config import DEBUG, ALLOWED_HOSTS
from kami.middleware.jwt import JwtMiddleware
from kami.middleware.pages import PagesMiddleware


def create_app() -> Starlette:
    routes = [
        Route("/", Homepage, name="home"),
        Mount("/assets", StaticFiles(directory="kami/static"), name="static"),
        Route("/login", Login, name="login"),
        Route("/logout", Logout, name="logout"),
        Mount("/dashboard", routes=[
            Route("/", Dashboard, name="dashboard"),
            Mount("/account", routes=[
                Route("/security", SecurityEndpoint, name="security"),
                Route("/security/changepassword", ChangePassword, name="changepassword")
            ]),
            Mount("/admin", routes=[
                Route("/anime", AnimeEndpoint, name="anime"),
                Route("/anime/add", AnimeAdd, name="anime_add"),
                Route("/anime/remove", AnimeRemove, name="anime_remove"),
                Route("/anime/edit/{id:int}", AnimeEdit, name="anime_edit"),
                Route("/fansub", FansubEndpoint, name="fansub"),
                Route("/fansub/add", FansubAdd, name="fansub_add"),
                Route("/fansub/remove", FansubRemove, name="fansub_remove"),
                Route("/fansub/edit/{id:int}", FansubEdit, name="fansub_edit"),
                Route("/pages", PagesEndpoint, name="pages"),
                Route("/pages/add", PagesAdd, name="pages_add"),
                Route("/pages/remove", PagesRemove, name="pages_remove"),
                Route("/pages/edit/{id:int}", PagesEdit, name="pages_edit")
            ])
        ]),
        Route("/{slug}", PagesGet, name="pages_get")
    ]

    exceptions = {
        404: not_found
    }

    middleware = [
        Middleware(TrustedHostMiddleware, allowed_hosts=list(ALLOWED_HOSTS)),
        Middleware(JwtMiddleware),
        Middleware(PagesMiddleware)
    ]

    app = Starlette(debug=DEBUG, routes=routes, exception_handlers=exceptions, middleware=middleware)

    return app
