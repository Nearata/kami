from starlette.config import Config
from starlette.datastructures import Secret, CommaSeparatedStrings


# Config will be read from environment variables and/or ".env" files.
config = Config(".env")

JWT_SECRET = config("JWT_SECRET", cast=Secret, default="secret")
JWT_ALGORITHM = config("JWT_ALGORITHM", cast=str, default="HS256")
DEBUG = config("DEBUG", cast=bool, default=False)
SITE_NAME = config("SITE_NAME", cast=str, default="A website")
SITE_DESCRIPTION = config("SITE_DESCRIPTION", cast=str, default="")
CAPTCHA = config("CAPTCHA", cast=bool, default=False)
CAPTCHA_SITE_KEY = config("CAPTCHA_SITE_KEY", cast=str, default="")
CAPTCHA_SECRET = config("CAPTCHA_SECRET", cast=str, default="")
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=CommaSeparatedStrings, default="*")
DISCORD = config("DISCORD", cast=str, default="")
TWITTER = config("TWITTER", cast=str, default="")
FAVICON = config("FAVICON", cast=str, default="")
LOGO = config("LOGO", cast=str, default="")
