from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from kami.routes.home import Homepage
from kami.routes.auth import Login, Logout
from kami.routes.dashboard import Dashboard, AccountSecurity
from kami.routes.anime import AdminAnime, AdminAnimeEdit
from kami.routes.fansub import AdminFansub, AdminFansubEdit
from kami.routes.changepassword import ChangePassword
from kami.exceptions import not_found
from kami.config import DEBUG, ALLOWED_HOSTS
from kami.middleware.jwt import JwtMiddleware


def create_app() -> Starlette:
    routes = [
        Route("/", Homepage, name="home"),
        Mount("/assets", StaticFiles(directory="kami/static"), name="static"),
        Route("/login", Login, name="login"),
        Route("/logout", Logout, name="logout"),
        Mount("/dashboard", routes=[
            Route("/", Dashboard, name="dashboard"),
            Mount("/account", routes=[
                Route("/security", AccountSecurity, name="account_security"),
                Route("/security/changepassword", ChangePassword, name="security_changepassword")
            ]),
            Mount("/admin", routes=[
                Route("/anime", AdminAnime, name="admin_anime"),
                Route("/anime/{id:int}", AdminAnimeEdit, name="admin_anime_edit"),
                Route("/fansub", AdminFansub, name="admin_fansub"),
                Route("/fansub/{id:int}", AdminFansubEdit, name="admin_fansub_edit")
            ])
        ])
    ]

    exceptions = {
        404: not_found
    }

    middleware = [
        Middleware(TrustedHostMiddleware, allowed_hosts=list(ALLOWED_HOSTS)),
        Middleware(JwtMiddleware)
    ]

    app = Starlette(debug=DEBUG, routes=routes, exception_handlers=exceptions, middleware=middleware)

    return app
