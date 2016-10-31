import json
import time
import aiohttp
from aiohttp import web
from stores import messages_table, message_recipient_table


async def websocket_handler(request):
    nc = request.app['nats']
    db = request.app['db']

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    current_user_id = request.GET['user']

    async def user_handler(event):
        event_data = json.loads(event.data.decode('utf-8'))
        ws.send_str(json.dumps(event_data))

    sid_user = await nc.subscribe('channel.%s' % current_user_id, cb=user_handler)

    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                event_data = json.loads(msg.data)
                if event_data['type'] == 'message.im':
                    ts = time.time()
                    to_id = event_data['to']

                    async with db.acquire() as conn:
                        res = await conn.execute(
                            messages_table.insert().values(ts=ts,
                                                           text=event_data['text'],
                                                           user_id=current_user_id,
                                                           delivered=False,
                                                           read=False))
                        msg_id = list(res)[0][0]
                        await conn.execute(
                            message_recipient_table.insert().values(message_id=msg_id, user_id=to_id))

                    event_data['ts'] = ts
                    event_data['user_id'] = current_user_id
                    del event_data['to']

                    await nc.publish('channel.%s' % to_id, json.dumps(event_data).encode('utf-8'))
                    await nc.publish('channel.%s' % current_user_id, json.dumps(event_data).encode('utf-8'))
                    # await nc.publish('channel.%s' % current_user_id, msg.data.encode('utf-8'))

            elif msg.type == aiohttp.WSMsgType.ERROR:
                print('ws connection closed with exception %s' % ws.exception())
    finally:
        await nc.unsubscribe(sid_user)
        print('websocket connection closed')

    return ws
