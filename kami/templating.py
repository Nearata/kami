from starlette.templating import Jinja2Templates

from kami.config import SITE_NAME, SITE_DESCRIPTION, DISCORD, TWITTER, FAVICON, LOGO


templates = Jinja2Templates(directory="kami/templates")
templates.env.globals["site_name"] = SITE_NAME
templates.env.globals["site_description"] = SITE_DESCRIPTION
templates.env.globals["discord_url"] = DISCORD
templates.env.globals["twitter_url"] = TWITTER
templates.env.globals["favicon"] = FAVICON
templates.env.globals["logo"] = LOGO
