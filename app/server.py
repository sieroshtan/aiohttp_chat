import asyncio
from aiohttp import web
from handlers import websocket_handler
from aiopg.sa import create_engine
from nats.aio.client import Client as nats_client
from settings import DATABASE


async def make_app():
    app = web.Application()

    nc = nats_client()
    await nc.connect()
    app['nats'] = nc

    app['db'] = await create_engine('postgres://{}:{}@{}:{}/{}'.format(DATABASE['USER'], DATABASE['PASSWORD'],
                                                                       DATABASE['HOST'], DATABASE['PORT'],
                                                                       DATABASE['NAME']))

    app.router.add_get('/ws', websocket_handler)

    return app

loop = asyncio.get_event_loop()
app = loop.run_until_complete(make_app())
web.run_app(app, port='8888')

