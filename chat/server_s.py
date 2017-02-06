# standalone

from aiohttp import web
from chat.views import ws_handler

from chat.middlwares import nats_middleware, db_middleware

app = web.Application(middlewares=[
    nats_middleware,
    db_middleware
])

app.router.add_get('/ws', ws_handler)

web.run_app(app, port=8888)
