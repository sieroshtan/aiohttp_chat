from nats.aio.client import Client as nats_client
from aiopg.sa import create_engine


async def nats_middleware(app, handler):
    async def middleware_handler(request):
        nats = app.get('nats')
        if not nats:
            nats = nats_client()
            await nats.connect()
            app['nats'] = nats
        return await handler(request)
    return middleware_handler


async def db_middleware(app, handler):
    async def middleware_handler(request):
        db = app.get('db')
        if not db:
            app['db'] = db = await create_engine('postgres://chichat_user:1234@127.0.0.1:5432/chichat')
            request.app['db'] = db
        return await handler(request)
    return middleware_handler
