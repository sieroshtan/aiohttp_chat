import json
import uuid
import asyncio
import aiohttp
from aiohttp import web
from .stores import messages_table, user_channel_table
import sqlalchemy as sa


def ts_from_uuid1():
    uuid1 = uuid.uuid1()
    return str((uuid1.time - 0x01b21dd213814000) / 1e7)


async def _im_message(request, in_event, current_user_id):
    db = request.app['db']
    nc = request.app['nats']

    ts = ts_from_uuid1()

    out_event = {
        'type': 'message.im',
        'ts': ts,
        'user_is': current_user_id,
        'text': in_event['text']
    }

    async with db.acquire() as conn:
        res = await conn.execute(
            messages_table.insert().values(ts=ts,
                                           text=in_event['text'],
                                           user_sender_id=current_user_id,
                                           channel_id=in_event['channel'],
                                           delivered=False))

    await nc.publish('user.%s' % in_event['to'], json.dumps(out_event).encode('utf-8'))
    await nc.publish('user.%s' % current_user_id, json.dumps(out_event).encode('utf-8'))


async def _im_read(request, in_event, current_user_id):
    db = request.app['db']
    nc = request.app['nats']

    ts = ts_from_uuid1()

    out_event = {
        'type': 'message.im',
        'ts': ts,
        'user_is': current_user_id,
        'text': in_event['text']
    }

    await nc.publish('user.%s' % in_event['to'], json.dumps(out_event).encode('utf-8'))
    await nc.publish('user.%s' % current_user_id, json.dumps(out_event).encode('utf-8'))


async def _group_message(request, in_event, current_user_id):
    db = request.app['db']
    nc = request.app['nats']

    ts = ts_from_uuid1()

    out_event = {
        'type': 'message.im',
        'ts': ts,
        'user_is': current_user_id,
        'text': in_event['text']
    }

    async with db.acquire() as conn:
        channel_users = await conn.execute(
            sa.select([user_channel_table.c.user_id]).where(user_channel_table.c.channel_id == in_event['channel'])
        )

        for row in channel_users:
            to_id = row[user_channel_table.c.user_id]
            await nc.publish('user.%s' % to_id, json.dumps(out_event).encode('utf-8'))

        await conn.execute(
            messages_table.insert().values(ts=ts,
                                           text=in_event['text'],
                                           user_sender_id=current_user_id,
                                           channel_id=in_event['channel'],
                                           delivered=False)
        )


async def ws_handler(request):
    nc = request.app['nats']

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async def user_handler(event):
        event_data = json.loads(event.data.decode('utf-8'))
        ws.send_str(json.dumps(event_data))

    current_user_id = request.GET['user']

    sid_user = await nc.subscribe('user.%s' % current_user_id, cb=user_handler)

    try:
        async for msg in ws:
            if msg.tp == aiohttp.MsgType.text:

                if msg.data == 'heartbeat':
                    ws.send_str('heartbeat')
                else:
                    event = json.loads(msg.data)

                    if event['type'] == 'message.im':
                        await _im_message(request, event, current_user_id)

                    elif event['type'] == 'message.group':
                        await _group_message(request, event, current_user_id)

    except (asyncio.CancelledError, aiohttp.ClientDisconnectedError):
        print("WS Disconnected")
    finally:
        await nc.unsubscribe(sid_user)
        print('WS Closed')

    return ws
