# gunicorn

from aiohttp import web
from chat.views import ws_handler

app = web.Application()
app.router.add_get('/ws', ws_handler)
